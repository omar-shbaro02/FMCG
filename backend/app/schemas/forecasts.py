import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ForecastRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    diagnostic_case_id: uuid.UUID
    adapter_name: str
    adapter_version: str
    forecast_target: str
    series_id: str
    horizon_weeks: int
    run_status: str
    output_json: dict[str, object] | None
    error_json: dict[str, object] | None
    started_at: datetime | None
    completed_at: datetime | None


class ForecastEvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    forecast_run_id: uuid.UUID
    forecast_target: str
    forecast_horizon: int
    series_id: str
    forecast_direction: str
    forecasted_values_json: list[dict[str, object]]
    confidence_interval_json: dict[str, object]
    baseline_comparison: str
    post_promo_retention_status: str
    decay_signal: str
    uncertainty_level: str
    data_quality_notes_json: list[str]
