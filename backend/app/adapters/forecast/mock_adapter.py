from datetime import timedelta
from statistics import mean
from typing import Any

from app.adapters.forecast.interface import ForecastAdapter
from app.adapters.forecast.schemas import (
    AdapterMetadata,
    ConfidenceInterval,
    ForecastDirection,
    ForecastPoint,
    ForecastRequest,
    ForecastResponse,
    UncertaintyLevel,
)


class MockForecastAdapter(ForecastAdapter):
    """Deterministic numeric adapter for tests, CI, and frontend development."""

    name = "mock"
    version = "1.0.0"

    def validate_input(self, series_request: ForecastRequest) -> None:
        ForecastRequest.model_validate(series_request.model_dump())

    def prepare_series(self, series_request: ForecastRequest) -> list[float]:
        self.validate_input(series_request)
        return [point.value for point in series_request.history]

    def forecast(self, series_request: ForecastRequest) -> ForecastResponse:
        values = self.prepare_series(series_request)
        recent = values[-min(4, len(values)) :]
        level = mean(recent)
        slope = (recent[-1] - recent[0]) / max(len(recent) - 1, 1)
        spread = max(level * 0.1, 1.0)
        last_week = series_request.history[-1].week_start_date
        points = [
            ForecastPoint(
                week_start_date=last_week + timedelta(weeks=index),
                point_forecast=max(0, level + slope * index),
                lower_bound=max(0, level + slope * index - spread),
                upper_bound=max(0, level + slope * index + spread),
            )
            for index in range(1, series_request.horizon + 1)
        ]
        relative_slope = slope / level if level else 0
        if relative_slope > 0.05:
            direction = ForecastDirection.STRONGLY_INCREASING
        elif relative_slope > 0.01:
            direction = ForecastDirection.INCREASING
        elif relative_slope < -0.05:
            direction = ForecastDirection.STRONGLY_DECLINING
        elif relative_slope < -0.01:
            direction = ForecastDirection.DECLINING
        else:
            direction = ForecastDirection.STABLE
        return ForecastResponse(
            forecast_target=series_request.forecast_target,
            forecast_horizon=series_request.horizon,
            series_id=series_request.series_id,
            forecast_direction=direction,
            forecasted_values=points,
            confidence_interval=ConfidenceInterval(level=0.9, available=True),
            uncertainty_level=UncertaintyLevel.MEDIUM,
            data_quality_notes=["Deterministic mock forecast; not for commercial evidence."],
            adapter_metadata=AdapterMetadata(
                adapter_name=self.name,
                adapter_version=self.version,
            ),
        )

    def normalize_output(self, raw_output: Any) -> ForecastResponse:
        return ForecastResponse.model_validate(raw_output)

    def health_check(self) -> bool:
        return True

    def get_metadata(self) -> dict[str, str]:
        return {"adapter_name": self.name, "adapter_version": self.version}
