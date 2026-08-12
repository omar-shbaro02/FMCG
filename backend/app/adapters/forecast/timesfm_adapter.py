from __future__ import annotations

import importlib
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Protocol, cast

import numpy as np

from app.adapters.forecast.interface import ForecastAdapter
from app.adapters.forecast.schemas import (
    AdapterMetadata,
    ConfidenceInterval,
    ForecastAdapterError,
    ForecastDirection,
    ForecastPoint,
    ForecastRequest,
    ForecastResponse,
    UncertaintyLevel,
)
from app.config import Settings


class TimesFMRuntime(Protocol):
    def forecast(self, *, horizon: int, inputs: list[np.ndarray[Any, Any]]) -> tuple[Any, Any]: ...


class TimesFMAdapterException(RuntimeError):
    def __init__(self, error: ForecastAdapterError) -> None:
        super().__init__(error.message)
        self.error = error


@dataclass(frozen=True)
class TimesFMConfig:
    model_id: str
    context_length: int
    batch_size: int
    device: str
    timeout_seconds: int
    lower_quantile_index: int
    upper_quantile_index: int

    @classmethod
    def from_settings(cls, settings: Settings) -> TimesFMConfig:
        return cls(
            settings.timesfm_model_id,
            settings.timesfm_context_length,
            settings.timesfm_batch_size,
            settings.timesfm_device,
            settings.timesfm_timeout_seconds,
            settings.timesfm_quantile_lower_index,
            settings.timesfm_quantile_upper_index,
        )


class TimesFMAdapter(ForecastAdapter):
    """TimesFM 2.5 numeric inference isolated behind the normalized contract."""

    name = "timesfm"
    adapter_version = "2.5-contract-1"

    def __init__(self, config: TimesFMConfig, runtime: TimesFMRuntime | None = None) -> None:
        self.config = config
        self._runtime = runtime
        self.last_latency_seconds: float | None = None

    def validate_input(self, series_request: ForecastRequest) -> None:
        ForecastRequest.model_validate(series_request.model_dump())
        if len(series_request.history) > self.config.context_length:
            raise self._error(
                "UNSUPPORTED_SERIES_LENGTH",
                f"History exceeds configured context length {self.config.context_length}",
                False,
            )

    def prepare_series(self, series_request: ForecastRequest) -> list[np.ndarray[Any, Any]]:
        self.validate_input(series_request)
        series = np.asarray([point.value for point in series_request.history], dtype=np.float32)
        if series.ndim != 1 or not np.isfinite(series).all():
            raise self._error(
                "MALFORMED_DATA", "Prepared series is not finite and one-dimensional", False
            )
        return [series]

    def forecast(self, series_request: ForecastRequest) -> ForecastResponse:
        inputs = self.prepare_series(series_request)
        runtime = self._runtime or self._load_runtime()
        started = time.perf_counter()
        executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="timesfm")
        future = executor.submit(runtime.forecast, horizon=series_request.horizon, inputs=inputs)
        try:
            raw = future.result(timeout=self.config.timeout_seconds)
        except TimeoutError as exc:
            future.cancel()
            executor.shutdown(wait=False, cancel_futures=True)
            raise self._error(
                "TIMEOUT", "TimesFM inference exceeded configured timeout", True
            ) from exc
        except MemoryError as exc:
            executor.shutdown(wait=False, cancel_futures=True)
            raise self._error(
                "MEMORY_FAILURE", "TimesFM inference exhausted available memory", True
            ) from exc
        except Exception as exc:
            executor.shutdown(wait=False, cancel_futures=True)
            raise self._error(
                "MODEL_FAILURE", f"TimesFM inference failed: {type(exc).__name__}", True
            ) from exc
        else:
            executor.shutdown(wait=True)
        finally:
            self.last_latency_seconds = time.perf_counter() - started
        return self.normalize_output(
            {
                "raw": raw,
                "request": series_request,
            }
        )

    def normalize_output(self, raw_output: Any) -> ForecastResponse:
        try:
            request = raw_output["request"]
            point_raw, quantile_raw = raw_output["raw"]
            point = np.asarray(point_raw, dtype=float)
            quantiles = np.asarray(quantile_raw, dtype=float)
            horizon = request.horizon
            if point.shape != (1, horizon) or quantiles.ndim != 3:
                raise ValueError("unexpected output shape")
            if quantiles.shape[0] != 1 or quantiles.shape[1] != horizon:
                raise ValueError("quantile horizon does not match request")
            lower = quantiles[0, :, self.config.lower_quantile_index]
            upper = quantiles[0, :, self.config.upper_quantile_index]
            predicted = point[0]
            if not all(np.isfinite(values).all() for values in (predicted, lower, upper)):
                raise ValueError("non-finite forecast output")
            last_week = request.history[-1].week_start_date
            points = [
                ForecastPoint(
                    week_start_date=last_week + timedelta(weeks=index),
                    point_forecast=max(0, float(predicted[index - 1])),
                    lower_bound=max(0, float(lower[index - 1])),
                    upper_bound=max(0, float(upper[index - 1])),
                )
                for index in range(1, horizon + 1)
            ]
        except TimesFMAdapterException:
            raise
        except Exception as exc:
            raise self._error(
                "MALFORMED_OUTPUT",
                f"TimesFM returned invalid normalized output: {type(exc).__name__}",
                False,
            ) from exc
        first, last = points[0].point_forecast, points[-1].point_forecast
        relative_change = (last - first) / first if first else 0
        direction = self._direction(relative_change)
        return ForecastResponse(
            forecast_target=request.forecast_target,
            forecast_horizon=horizon,
            series_id=request.series_id,
            forecast_direction=direction,
            forecasted_values=points,
            confidence_interval=ConfidenceInterval(level=0.8, available=True),
            uncertainty_level=UncertaintyLevel.MEDIUM,
            data_quality_notes=[],
            adapter_metadata=AdapterMetadata(
                adapter_name=self.name,
                adapter_version=self.adapter_version,
            ),
        )

    def health_check(self) -> bool:
        try:
            self._runtime = self._runtime or self._load_runtime()
        except TimesFMAdapterException:
            return False
        return True

    def get_metadata(self) -> dict[str, str]:
        return {
            "adapter_name": self.name,
            "adapter_version": self.adapter_version,
            "model_id": self.config.model_id,
            "device": self.config.device,
        }

    def _load_runtime(self) -> TimesFMRuntime:
        try:
            timesfm = importlib.import_module("timesfm")
            model_class = timesfm.TimesFM_2p5_200M_torch
            model = model_class.from_pretrained(self.config.model_id)
            model.compile(
                timesfm.ForecastConfig(
                    max_context=self.config.context_length,
                    max_horizon=8,
                    normalize_inputs=True,
                    per_core_batch_size=self.config.batch_size,
                    use_continuous_quantile_head=True,
                    force_flip_invariance=True,
                    infer_is_positive=True,
                    fix_quantile_crossing=True,
                )
            )
        except (ImportError, AttributeError) as exc:
            raise self._error(
                "MODEL_UNAVAILABLE", "TimesFM 2.5 runtime is unavailable", False
            ) from exc
        except MemoryError as exc:
            raise self._error(
                "MEMORY_FAILURE", "TimesFM model could not fit in memory", True
            ) from exc
        except Exception as exc:
            raise self._error(
                "MODEL_UNAVAILABLE", f"TimesFM model failed to load: {type(exc).__name__}", True
            ) from exc
        return cast(TimesFMRuntime, model)

    def _error(self, category: str, message: str, retryable: bool) -> TimesFMAdapterException:
        return TimesFMAdapterException(
            ForecastAdapterError(
                category=category,
                message=message,
                retryable=retryable,
                adapter_name=self.name,
            )
        )

    @staticmethod
    def _direction(relative_change: float) -> ForecastDirection:
        if relative_change > 0.2:
            return ForecastDirection.STRONGLY_INCREASING
        if relative_change > 0.05:
            return ForecastDirection.INCREASING
        if relative_change < -0.2:
            return ForecastDirection.STRONGLY_DECLINING
        if relative_change < -0.05:
            return ForecastDirection.DECLINING
        return ForecastDirection.STABLE
