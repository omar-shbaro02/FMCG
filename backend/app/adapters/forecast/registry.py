from app.adapters.forecast.interface import ForecastAdapter
from app.adapters.forecast.mock_adapter import MockForecastAdapter
from app.adapters.forecast.timesfm_adapter import TimesFMAdapter, TimesFMConfig
from app.config import Settings, get_settings


class ForecastAdapterConfigurationError(ValueError):
    pass


def get_forecast_adapter(name: str, settings: Settings | None = None) -> ForecastAdapter:
    normalized = name.strip().casefold()
    if normalized == "mock":
        return MockForecastAdapter()
    if normalized == "timesfm":
        return TimesFMAdapter(TimesFMConfig.from_settings(settings or get_settings()))
    raise ForecastAdapterConfigurationError(f"Unknown forecast adapter: {name}")
