from datetime import UTC, date, datetime
from enum import StrEnum
from math import isfinite

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ForecastDirection(StrEnum):
    STRONGLY_INCREASING = "STRONGLY_INCREASING"
    INCREASING = "INCREASING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"
    STRONGLY_DECLINING = "STRONGLY_DECLINING"
    UNCERTAIN = "UNCERTAIN"


class BaselineComparison(StrEnum):
    ABOVE_BASELINE = "ABOVE_BASELINE"
    AT_BASELINE = "AT_BASELINE"
    BELOW_BASELINE = "BELOW_BASELINE"
    INSUFFICIENT = "INSUFFICIENT"


class RetentionStatus(StrEnum):
    SUSTAINED = "SUSTAINED"
    PARTIAL = "PARTIAL"
    WEAK = "WEAK"
    COLLAPSED = "COLLAPSED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INSUFFICIENT = "INSUFFICIENT"


class DecaySignal(StrEnum):
    NONE = "NONE"
    MILD = "MILD"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    UNCERTAIN = "UNCERTAIN"


class UncertaintyLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    INSUFFICIENT = "INSUFFICIENT"


class HistoryPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")
    week_start_date: date
    value: float

    @model_validator(mode="after")
    def finite_non_negative(self) -> "HistoryPoint":
        if not isfinite(self.value) or self.value < 0:
            raise ValueError("history value must be finite and non-negative")
        return self


class ForecastContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sku_id: str
    channel: str
    region: str
    promotion_start_week: date
    promotion_end_week: date


class ForecastCovariates(BaseModel):
    model_config = ConfigDict(extra="forbid")
    promo_flag: list[bool] = Field(default_factory=list)
    discount_depth: list[float] = Field(default_factory=list)
    out_of_stock_flag: list[bool] = Field(default_factory=list)


class ForecastRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    forecast_target: str = "sell_out_units"
    series_id: str
    time_grain: str = "weekly"
    horizon: int = Field(ge=4, le=8)
    history: list[HistoryPoint] = Field(min_length=4)
    covariates: ForecastCovariates = Field(default_factory=ForecastCovariates)
    context: ForecastContext

    @model_validator(mode="after")
    def validate_contract(self) -> "ForecastRequest":
        if self.forecast_target != "sell_out_units" or self.time_grain != "weekly":
            raise ValueError("MVP supports weekly sell_out_units only")
        expected = f"{self.context.sku_id}|{self.context.channel}|{self.context.region}"
        if self.series_id != expected:
            raise ValueError("series_id must match context grain")
        dates = [point.week_start_date for point in self.history]
        if dates != sorted(dates) or len(dates) != len(set(dates)):
            raise ValueError("history must be unique and chronological")
        return self


class ForecastPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")
    week_start_date: date
    point_forecast: float
    lower_bound: float
    upper_bound: float

    @model_validator(mode="after")
    def valid_interval(self) -> "ForecastPoint":
        values = (self.lower_bound, self.point_forecast, self.upper_bound)
        if not all(isfinite(value) and value >= 0 for value in values):
            raise ValueError("forecast values must be finite and non-negative")
        if not self.lower_bound <= self.point_forecast <= self.upper_bound:
            raise ValueError("forecast interval must contain point forecast")
        return self


class ConfidenceInterval(BaseModel):
    model_config = ConfigDict(extra="forbid")
    level: float = Field(gt=0, lt=1)
    available: bool


class AdapterMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    adapter_name: str
    adapter_version: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ForecastResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    forecast_target: str
    forecast_horizon: int = Field(ge=4, le=8)
    series_id: str
    forecast_direction: ForecastDirection
    forecasted_values: list[ForecastPoint]
    confidence_interval: ConfidenceInterval
    baseline_comparison: BaselineComparison = BaselineComparison.INSUFFICIENT
    post_promo_retention_status: RetentionStatus = RetentionStatus.INSUFFICIENT
    decay_signal: DecaySignal = DecaySignal.UNCERTAIN
    uncertainty_level: UncertaintyLevel
    data_quality_notes: list[str]
    adapter_metadata: AdapterMetadata

    @model_validator(mode="after")
    def exact_horizon(self) -> "ForecastResponse":
        if len(self.forecasted_values) != self.forecast_horizon:
            raise ValueError("forecasted_values length must equal forecast_horizon")
        return self


class ForecastAdapterError(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: str
    message: str
    retryable: bool
    adapter_name: str
