import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.entities import CaseStatus


class DiagnosticCaseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    dataset_id: uuid.UUID
    sku_id: str = Field(min_length=1, max_length=100)
    channel: str = Field(min_length=1, max_length=150)
    region: str = Field(min_length=1, max_length=150)
    promotion_start_week: date
    promotion_end_week: date
    forecast_horizon_weeks: int = Field(ge=4, le=8)
    management_concern_note: str | None = Field(default=None, max_length=4000)

    @model_validator(mode="after")
    def valid_window(self) -> "DiagnosticCaseCreate":
        if self.promotion_end_week < self.promotion_start_week:
            raise ValueError("promotion_end_week must not precede promotion_start_week")
        return self


class DiagnosticCaseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    sku_id: str | None = Field(default=None, min_length=1, max_length=100)
    channel: str | None = Field(default=None, min_length=1, max_length=150)
    region: str | None = Field(default=None, min_length=1, max_length=150)
    promotion_start_week: date | None = None
    promotion_end_week: date | None = None
    forecast_horizon_weeks: int | None = Field(default=None, ge=4, le=8)
    management_concern_note: str | None = Field(default=None, max_length=4000)


class DiagnosticCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    dataset_id: uuid.UUID
    sku_id: str
    channel: str
    region: str
    promotion_start_week: date
    promotion_end_week: date
    forecast_horizon_weeks: int
    status: CaseStatus
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


class DiagnosticCaseListResponse(BaseModel):
    items: list[DiagnosticCaseResponse]
    page: int
    page_size: int
    total: int


class CaseReadinessResponse(BaseModel):
    ready: bool
    reasons: list[str]
    series_observation_count: int
    status: CaseStatus
