"""Replaceable numeric forecast adapters."""

from app.adapters.forecast.interface import ForecastAdapter
from app.adapters.forecast.registry import ForecastAdapterConfigurationError, get_forecast_adapter

__all__ = ["ForecastAdapter", "ForecastAdapterConfigurationError", "get_forecast_adapter"]
