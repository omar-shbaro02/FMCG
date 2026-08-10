import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.domain.auth import UserRole


class DatasetStatus(StrEnum):
    UPLOADED = "UPLOADED"
    VALIDATING = "VALIDATING"
    VALID = "VALID"
    VALID_WITH_WARNINGS = "VALID_WITH_WARNINGS"
    INVALID = "INVALID"
    ARCHIVED = "ARCHIVED"


class CaseStatus(StrEnum):
    DRAFT = "DRAFT"
    DATA_VALIDATION = "DATA_VALIDATION"
    READY_FOR_FORECAST = "READY_FOR_FORECAST"
    FORECASTING = "FORECASTING"
    INTERPRETING = "INTERPRETING"
    INVESTIGATION_PENDING = "INVESTIGATION_PENDING"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    UNDER_HUMAN_REVIEW = "UNDER_HUMAN_REVIEW"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class ReviewStatus(StrEnum):
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    VALIDATED_WITH_CHANGES = "VALIDATED_WITH_CHANGES"
    MORE_EVIDENCE_REQUIRED = "MORE_EVIDENCE_REQUIRED"
    REJECTED = "REJECTED"


class UuidTimestampMixin:
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class User(UuidTimestampMixin, Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(200))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Dataset(UuidTimestampMixin, Base):
    __tablename__ = "datasets"
    name: Mapped[str] = mapped_column(String(255))
    original_filename: Mapped[str] = mapped_column(String(255))
    storage_path: Mapped[str] = mapped_column(String(1000), unique=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    upload_status: Mapped[DatasetStatus] = mapped_column(Enum(DatasetStatus, name="dataset_status"))
    schema_version: Mapped[str] = mapped_column(String(50))
    row_count: Mapped[int | None] = mapped_column(Integer)
    date_min: Mapped[date | None] = mapped_column(Date)
    date_max: Mapped[date | None] = mapped_column(Date)
    validation_summary_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class DatasetValidationIssue(UuidTimestampMixin, Base):
    __tablename__ = "dataset_validation_issues"
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), index=True
    )
    severity: Mapped[str] = mapped_column(String(30))
    field_name: Mapped[str | None] = mapped_column(String(100))
    row_reference: Mapped[str | None] = mapped_column(String(100))
    issue_code: Mapped[str] = mapped_column(String(100), index=True)
    issue_message: Mapped[str] = mapped_column(Text)
    resolution_status: Mapped[str] = mapped_column(String(30), default="OPEN")


class WeeklyFmcgSale(UuidTimestampMixin, Base):
    __tablename__ = "weekly_fmcg_sales"
    __table_args__ = (
        UniqueConstraint(
            "week_start_date", "sku_id", "channel", "region", name="uq_weekly_series_grain"
        ),
        Index("ix_weekly_series_scope", "sku_id", "channel", "region", "week_start_date"),
    )
    week_start_date: Mapped[date] = mapped_column(Date)
    sku_id: Mapped[str] = mapped_column(String(100))
    brand: Mapped[str] = mapped_column(String(150))
    category: Mapped[str] = mapped_column(String(150))
    channel: Mapped[str] = mapped_column(String(150))
    region: Mapped[str] = mapped_column(String(150))
    sell_out_units: Mapped[Decimal] = mapped_column(Numeric(18, 3))
    sell_in_units: Mapped[Decimal] = mapped_column(Numeric(18, 3))
    promo_flag: Mapped[bool] = mapped_column(Boolean)
    discount_depth: Mapped[Decimal] = mapped_column(Numeric(7, 4))
    net_sales_value: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    gross_sales_value: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    gross_margin: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    stock_on_hand: Mapped[Decimal] = mapped_column(Numeric(18, 3))
    out_of_stock_flag: Mapped[bool] = mapped_column(Boolean)
    returns_units: Mapped[Decimal] = mapped_column(Numeric(18, 3))
    source_dataset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE")
    )


class DiagnosticCase(UuidTimestampMixin, Base):
    __tablename__ = "diagnostic_cases"
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    dataset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("datasets.id", ondelete="RESTRICT"))
    sku_id: Mapped[str] = mapped_column(String(100))
    channel: Mapped[str] = mapped_column(String(150))
    region: Mapped[str] = mapped_column(String(150))
    promotion_start_week: Mapped[date] = mapped_column(Date)
    promotion_end_week: Mapped[date] = mapped_column(Date)
    forecast_horizon_weeks: Mapped[int] = mapped_column(Integer)
    status: Mapped[CaseStatus] = mapped_column(Enum(CaseStatus, name="case_status"), index=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BaselineCalculation(UuidTimestampMixin, Base):
    __tablename__ = "baseline_calculations"
    diagnostic_case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("diagnostic_cases.id", ondelete="CASCADE"), index=True
    )
    baseline_method: Mapped[str] = mapped_column(String(100))
    baseline_start_week: Mapped[date] = mapped_column(Date)
    baseline_end_week: Mapped[date] = mapped_column(Date)
    baseline_values_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    assumptions_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    quality_notes_json: Mapped[dict[str, Any]] = mapped_column(JSON)


class ForecastRun(UuidTimestampMixin, Base):
    __tablename__ = "forecast_runs"
    diagnostic_case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("diagnostic_cases.id", ondelete="CASCADE"), index=True
    )
    adapter_name: Mapped[str] = mapped_column(String(100))
    adapter_version: Mapped[str] = mapped_column(String(100))
    forecast_target: Mapped[str] = mapped_column(String(100))
    series_id: Mapped[str] = mapped_column(String(500))
    horizon_weeks: Mapped[int] = mapped_column(Integer)
    run_status: Mapped[str] = mapped_column(String(50), index=True)
    input_snapshot_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    output_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    error_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))


class ForecastEvidence(UuidTimestampMixin, Base):
    __tablename__ = "forecast_evidence"
    forecast_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("forecast_runs.id", ondelete="CASCADE"), index=True
    )
    forecast_target: Mapped[str] = mapped_column(String(100))
    forecast_horizon: Mapped[int] = mapped_column(Integer)
    series_id: Mapped[str] = mapped_column(String(500))
    forecast_direction: Mapped[str] = mapped_column(String(50))
    forecasted_values_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    confidence_interval_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    baseline_comparison: Mapped[str] = mapped_column(String(50))
    post_promo_retention_status: Mapped[str] = mapped_column(String(50))
    decay_signal: Mapped[str] = mapped_column(String(50))
    uncertainty_level: Mapped[str] = mapped_column(String(50))
    data_quality_notes_json: Mapped[list[str]] = mapped_column(JSON)


class GrowthQualityAssessment(UuidTimestampMixin, Base):
    __tablename__ = "growth_quality_assessments"
    diagnostic_case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("diagnostic_cases.id", ondelete="CASCADE"), index=True
    )
    assessment_status: Mapped[str] = mapped_column(String(50))
    growth_signal_summary: Mapped[str] = mapped_column(Text)
    growth_quality_judgment: Mapped[str] = mapped_column(Text)
    primary_risk_class: Mapped[str] = mapped_column(String(100))
    secondary_risk_classes_json: Mapped[list[str]] = mapped_column(JSON)
    interpretation_evidence_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    uncertainty_notes_json: Mapped[list[str]] = mapped_column(JSON)
    rule_version: Mapped[str] = mapped_column(String(100))
    prompt_version: Mapped[str | None] = mapped_column(String(100))


class InvestigationPlan(UuidTimestampMixin, Base):
    __tablename__ = "investigation_plans"
    diagnostic_case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("diagnostic_cases.id", ondelete="CASCADE"), index=True
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("growth_quality_assessments.id", ondelete="CASCADE")
    )
    investigation_items_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    recommended_owner: Mapped[str] = mapped_column(String(100))
    decision_affected: Mapped[str] = mapped_column(Text)
    acting_too_early_risks_json: Mapped[list[str]] = mapped_column(JSON)
    evidence_confidence: Mapped[str] = mapped_column(String(50))


class DecisionSimulation(UuidTimestampMixin, Base):
    __tablename__ = "decision_simulations"
    diagnostic_case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("diagnostic_cases.id", ondelete="CASCADE"), index=True
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("growth_quality_assessments.id", ondelete="CASCADE")
    )
    option: Mapped[str] = mapped_column(String(100))
    assumptions_json: Mapped[list[str]] = mapped_column(JSON)
    potential_benefits_json: Mapped[list[str]] = mapped_column(JSON)
    potential_risks_json: Mapped[list[str]] = mapped_column(JSON)
    evidence_requirements_json: Mapped[list[str]] = mapped_column(JSON)
    confidence: Mapped[str] = mapped_column(String(50))
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ExecutiveOutput(UuidTimestampMixin, Base):
    __tablename__ = "executive_outputs"
    diagnostic_case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("diagnostic_cases.id", ondelete="CASCADE"), index=True
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("growth_quality_assessments.id", ondelete="CASCADE")
    )
    output_version: Mapped[str] = mapped_column(String(100))
    output_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    output_markdown: Mapped[str] = mapped_column(Text)
    generated_by: Mapped[str] = mapped_column(String(100))
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    human_review_status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, name="review_status")
    )


class HumanReview(UuidTimestampMixin, Base):
    __tablename__ = "human_reviews"
    diagnostic_case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("diagnostic_cases.id", ondelete="CASCADE"), index=True
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    review_status: Mapped[ReviewStatus] = mapped_column(Enum(ReviewStatus, name="review_status"))
    validated_risk_class: Mapped[str | None] = mapped_column(String(100))
    reviewer_comments: Mapped[str | None] = mapped_column(Text)
    requested_evidence_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    final_decision_note: Mapped[str | None] = mapped_column(Text)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class FeedbackEvent(UuidTimestampMixin, Base):
    __tablename__ = "feedback_events"
    diagnostic_case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("diagnostic_cases.id", ondelete="CASCADE"), index=True
    )
    submitted_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    feedback_type: Mapped[str] = mapped_column(String(100))
    observed_outcome_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    classification_correct: Mapped[bool | None] = mapped_column(Boolean)
    simulation_useful: Mapped[bool | None] = mapped_column(Boolean)
    notes: Mapped[str | None] = mapped_column(Text)


class AuditEvent(UuidTimestampMixin, Base):
    __tablename__ = "audit_events"
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    entity_type: Mapped[str] = mapped_column(String(100))
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    before_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    after_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    correlation_id: Mapped[str] = mapped_column(String(100), index=True)
