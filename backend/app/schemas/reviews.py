import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.entities import ReviewStatus


class EvidenceRequest(BaseModel):
    evidence: str = Field(min_length=3, max_length=500)
    reason: str = Field(min_length=3, max_length=1000)
    owner: str = Field(min_length=2, max_length=100)


class HumanReviewCreate(BaseModel):
    review_status: ReviewStatus
    validated_risk_class: str | None = Field(default=None, max_length=100)
    reviewer_comments: str | None = Field(default=None, max_length=4000)
    requested_evidence: list[EvidenceRequest] = Field(default_factory=list, max_length=20)
    final_decision_note: str | None = Field(default=None, max_length=4000)


class HumanReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    diagnostic_case_id: uuid.UUID
    reviewer_id: uuid.UUID
    review_status: ReviewStatus
    validated_risk_class: str | None
    reviewer_comments: str | None
    requested_evidence_json: list[dict[str, str]]
    final_decision_note: str | None
    reviewed_at: datetime | None
    created_at: datetime


class FeedbackCreate(BaseModel):
    feedback_type: str = Field(min_length=2, max_length=100)
    observed_outcome: dict[str, object] = Field(default_factory=dict)
    classification_correct: bool | None = None
    simulation_useful: bool | None = None
    notes: str | None = Field(default=None, max_length=4000)


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    diagnostic_case_id: uuid.UUID
    submitted_by: uuid.UUID
    feedback_type: str
    observed_outcome_json: dict[str, object]
    classification_correct: bool | None
    simulation_useful: bool | None
    notes: str | None
    created_at: datetime
