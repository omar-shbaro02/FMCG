from datetime import date, timedelta

from app.adapters.forecast.mock_adapter import MockForecastAdapter
from app.adapters.forecast.schemas import (
    AdapterMetadata,
    ConfidenceInterval,
    ForecastDirection,
    ForecastPoint,
    ForecastResponse,
    UncertaintyLevel,
)
from app.domain.forecasts import CommercialSeriesPoint, derive_evidence
from tests.test_forecast_adapter_contract import request


def response(values: list[float], spread: float = 10) -> ForecastResponse:
    start = date(2026, 4, 6)
    return ForecastResponse(
        forecast_target="sell_out_units",
        forecast_horizon=len(values),
        series_id="SKU-1|MODERN_TRADE|NORTH",
        forecast_direction=ForecastDirection.UNCERTAIN,
        forecasted_values=[
            ForecastPoint(
                week_start_date=start + timedelta(weeks=index),
                point_forecast=value,
                lower_bound=max(0, value - spread),
                upper_bound=value + spread,
            )
            for index, value in enumerate(values)
        ],
        confidence_interval=ConfidenceInterval(level=0.8, available=True),
        uncertainty_level=UncertaintyLevel.MEDIUM,
        data_quality_notes=["source note"],
        adapter_metadata=AdapterMetadata(adapter_name="test", adapter_version="1"),
    )


def test_sustained_above_baseline_evidence_is_deterministic() -> None:
    evidence = derive_evidence(
        response([120, 121, 122, 123]),
        [100, 100, 100, 100],
        [CommercialSeriesPoint(date(2026, 1, 5), 100, 102)],
    )
    assert evidence.baseline_comparison == "ABOVE_BASELINE"
    assert evidence.post_promo_retention_status == "SUSTAINED"
    assert evidence.forecast_direction == "STABLE"
    assert evidence.decay_signal == "NONE"
    assert evidence.sell_in_sell_out_divergence == "ALIGNED"


def test_decline_decay_loading_and_uncertainty_are_traceable() -> None:
    evidence = derive_evidence(
        response([130, 110, 90, 70], spread=40),
        [110, 110, 110, 110],
        [CommercialSeriesPoint(date(2026, 1, 5), 80, 130)],
    )
    assert evidence.forecast_direction == "STRONGLY_DECLINING"
    assert evidence.decay_signal == "STRONG"
    assert evidence.uncertainty_level == "HIGH"
    assert evidence.sell_in_sell_out_divergence == "MATERIAL_SELL_IN_EXCESS"
    assert evidence.evidence_values["sell_in_to_sell_out_ratio"] == 1.625


def test_misaligned_baseline_refuses_false_evidence() -> None:
    forecast = MockForecastAdapter().forecast(request())
    evidence = derive_evidence(forecast, [100], [])
    assert evidence.baseline_comparison == "INSUFFICIENT"
    assert evidence.uncertainty_level == "INSUFFICIENT"
    assert evidence.data_quality_notes
