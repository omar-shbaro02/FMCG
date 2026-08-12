from abc import ABC, abstractmethod
from typing import Any

from app.adapters.forecast.schemas import ForecastRequest, ForecastResponse


class ForecastAdapter(ABC):
    @abstractmethod
    def validate_input(self, series_request: ForecastRequest) -> None: ...

    @abstractmethod
    def prepare_series(self, series_request: ForecastRequest) -> Any: ...

    @abstractmethod
    def forecast(self, series_request: ForecastRequest) -> ForecastResponse: ...

    @abstractmethod
    def normalize_output(self, raw_output: Any) -> ForecastResponse: ...

    @abstractmethod
    def health_check(self) -> bool: ...

    @abstractmethod
    def get_metadata(self) -> dict[str, str]: ...
