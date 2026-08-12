import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.domain.baselines import BaselineMethod


class BaselineCalculationRequest(BaseModel):
    method: BaselineMethod = BaselineMethod.RECENT_PRE_PROMO_AVERAGE
    recent_weeks: int = 8


class BaselineCalculationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    diagnostic_case_id: uuid.UUID
    baseline_method: str
    baseline_start_week: date
    baseline_end_week: date
    baseline_values_json: dict[str, object]
    assumptions_json: dict[str, object]
    quality_notes_json: dict[str, object]
    created_at: datetime
