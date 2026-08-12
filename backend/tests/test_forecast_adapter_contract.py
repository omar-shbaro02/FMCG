from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.adapters.forecast import ForecastAdapterConfigurationError, get_forecast_adapter
from app.adapters.forecast.schemas import ForecastContext, ForecastRequest, HistoryPoint
from app.adapters.forecast.timesfm_adapter import TimesFMAdapter


def request() -> ForecastRequest:
    start = date(2026, 1, 5)
    return ForecastRequest(
        series_id="SKU-1|MODERN_TRADE|NORTH",
        horizon=6,
        history=[
            HistoryPoint(week_start_date=start + timedelta(weeks=i), value=100 + i)
            for i in range(12)
        ],
        context=ForecastContext(
            sku_id="SKU-1",
            channel="MODERN_TRADE",
            region="NORTH",
            promotion_start_week=date(2026, 3, 2),
            promotion_end_week=date(2026, 3, 9),
        ),
    )


def test_mock_passes_strict_contract_and_is_deterministic() -> None:
    adapter = get_forecast_adapter("mock")
    first = adapter.forecast(request())
    second = adapter.forecast(request())

    assert first.model_dump(exclude={"adapter_metadata": {"generated_at"}}) == second.model_dump(
        exclude={"adapter_metadata": {"generated_at"}}
    )
    assert len(first.forecasted_values) == 6
    assert first.adapter_metadata.adapter_name == "mock"
    assert adapter.health_check()


def test_malformed_output_and_unknown_fields_are_rejected() -> None:
    adapter = get_forecast_adapter("mock")
    malformed = adapter.forecast(request()).model_dump()
    malformed["forecasted_values"][0]["point_forecast"] = float("nan")
    with pytest.raises(ValidationError):
        adapter.normalize_output(malformed)
    malformed = adapter.forecast(request()).model_dump()
    malformed["commercial_recommendation"] = "repeat promotion"
    with pytest.raises(ValidationError):
        adapter.normalize_output(malformed)


def test_request_enforces_series_grain_and_chronology() -> None:
    payload = request().model_dump()
    payload["series_id"] = "wrong"
    with pytest.raises(ValidationError):
        ForecastRequest.model_validate(payload)
    payload = request().model_dump()
    payload["history"] = list(reversed(payload["history"]))
    with pytest.raises(ValidationError):
        ForecastRequest.model_validate(payload)


def test_registry_selects_timesfm_without_silent_mock_fallback() -> None:
    assert isinstance(get_forecast_adapter("timesfm"), TimesFMAdapter)
    with pytest.raises(ForecastAdapterConfigurationError):
        get_forecast_adapter("unknown")
