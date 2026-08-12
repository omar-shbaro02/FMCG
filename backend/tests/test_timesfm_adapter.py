import time
from typing import Any

import numpy as np
import pytest

from app.adapters.forecast.timesfm_adapter import (
    TimesFMAdapter,
    TimesFMAdapterException,
    TimesFMConfig,
)
from tests.test_forecast_adapter_contract import request


class SuccessfulRuntime:
    def forecast(self, *, horizon: int, inputs: list[np.ndarray[Any, Any]]) -> tuple[Any, Any]:
        assert len(inputs) == 1
        point = np.asarray([[110 + index for index in range(horizon)]], dtype=float)
        quantiles = np.zeros((1, horizon, 10), dtype=float)
        for index in range(horizon):
            quantiles[0, index, :] = np.linspace(point[0, index] - 10, point[0, index] + 10, 10)
        return point, quantiles


class NonFiniteRuntime:
    def forecast(self, *, horizon: int, inputs: list[np.ndarray[Any, Any]]) -> tuple[Any, Any]:
        point = np.full((1, horizon), np.nan)
        return point, np.zeros((1, horizon, 10))


class SlowRuntime:
    def forecast(self, *, horizon: int, inputs: list[np.ndarray[Any, Any]]) -> tuple[Any, Any]:
        time.sleep(0.05)
        return SuccessfulRuntime().forecast(horizon=horizon, inputs=inputs)


def config(**changes: Any) -> TimesFMConfig:
    values = {
        "model_id": "google/timesfm-2.5-200m-pytorch",
        "context_length": 1024,
        "batch_size": 16,
        "device": "cpu",
        "timeout_seconds": 2,
        "lower_quantile_index": 1,
        "upper_quantile_index": 9,
    }
    values.update(changes)
    return TimesFMConfig(**values)


def test_timesfm_normalizes_provider_arrays_without_provider_fields() -> None:
    adapter = TimesFMAdapter(config(), SuccessfulRuntime())
    response = adapter.forecast(request())

    assert response.forecast_horizon == 6
    assert response.adapter_metadata.adapter_name == "timesfm"
    assert response.forecasted_values[0].lower_bound <= response.forecasted_values[0].point_forecast
    assert "model_id" not in response.model_dump()
    assert adapter.last_latency_seconds is not None


def test_timesfm_rejects_unsupported_context_and_nonfinite_output() -> None:
    adapter = TimesFMAdapter(config(context_length=4), SuccessfulRuntime())
    with pytest.raises(TimesFMAdapterException) as length_error:
        adapter.forecast(request())
    assert length_error.value.error.category == "UNSUPPORTED_SERIES_LENGTH"

    adapter = TimesFMAdapter(config(), NonFiniteRuntime())
    with pytest.raises(TimesFMAdapterException) as output_error:
        adapter.forecast(request())
    assert output_error.value.error.category == "MALFORMED_OUTPUT"


def test_timesfm_timeout_is_structured_and_retryable() -> None:
    adapter = TimesFMAdapter(config(timeout_seconds=0.001), SlowRuntime())
    with pytest.raises(TimesFMAdapterException) as error:
        adapter.forecast(request())
    assert error.value.error.category == "TIMEOUT"
    assert error.value.error.retryable


def test_timesfm_unavailable_runtime_is_visible(monkeypatch: pytest.MonkeyPatch) -> None:
    def unavailable(_: str) -> Any:
        raise ImportError

    monkeypatch.setattr(
        "app.adapters.forecast.timesfm_adapter.importlib.import_module", unavailable
    )
    adapter = TimesFMAdapter(config())
    assert not adapter.health_check()
    with pytest.raises(TimesFMAdapterException) as error:
        adapter.forecast(request())
    assert error.value.error.category == "MODEL_UNAVAILABLE"
