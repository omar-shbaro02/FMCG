import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.models.entities import DatasetStatus


class DatasetResponse(BaseModel):
    id: uuid.UUID
    name: str
    original_filename: str
    upload_status: DatasetStatus
    schema_version: str
    created_at: datetime


class DatasetValidationRequest(BaseModel):
    currency: str = "USD"
    gross_margin_representation: Literal["amount", "percentage"] = "amount"
    stock_unit: Literal["units", "cases"] = "units"


class ValidationIssueResponse(BaseModel):
    severity: Literal["CRITICAL", "WARNING", "INFO"]
    field_name: str | None = None
    row_reference: str | None = None
    issue_code: str
    issue_message: str


class SeriesEligibilityResponse(BaseModel):
    series_id: str
    observation_count: int
    eligible: bool
    reasons: list[str]


class DatasetValidationResponse(BaseModel):
    dataset_id: uuid.UUID
    overall_status: DatasetStatus
    row_count: int
    valid_row_count: int
    rejected_row_count: int
    date_min: str | None
    date_max: str | None
    missing_fields: list[str]
    missing_weeks: dict[str, list[str]]
    duplicate_series: list[str]
    forecast_eligible_series: list[str]
    forecast_ineligible_series: list[SeriesEligibilityResponse]
    warnings: list[ValidationIssueResponse]
    critical_errors: list[ValidationIssueResponse]
    business_distortion_notes: list[str]
    transformations: list[str]
    declarations: dict[str, str]
