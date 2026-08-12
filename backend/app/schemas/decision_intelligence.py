import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DecisionIntelligenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    diagnostic_case_id: uuid.UUID
    assessment_id: uuid.UUID
    output_version: str
    output_json: dict[str, object]
    output_markdown: str
    generated_by: str
    generated_at: datetime
    human_review_status: str
