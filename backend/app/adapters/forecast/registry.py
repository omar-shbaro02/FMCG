from app.adapters.forecast.interface import ForecastAdapter
from app.adapters.forecast.mock_adapter import MockForecastAdapter


class ForecastAdapterConfigurationError(ValueError):
    pass


def get_forecast_adapter(name: str) -> ForecastAdapter:
    normalized = name.strip().casefold()
    if normalized == "mock":
        return MockForecastAdapter()
    if normalized == "timesfm":
        raise ForecastAdapterConfigurationError(
            "TimesFM is not available until Task 10; no silent mock fallback is permitted"
        )
    raise ForecastAdapterConfigurationError(f"Unknown forecast adapter: {name}")
