from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.entities import CaseStatus, Dataset, DatasetStatus, DiagnosticCase, WeeklyFmcgSale


class CaseReadinessError(ValueError):
    def __init__(self, reasons: list[str]) -> None:
        super().__init__("; ".join(reasons))
        self.reasons = reasons


class InvalidCaseTransitionError(ValueError):
    pass


@dataclass(frozen=True)
class CaseReadiness:
    ready: bool
    reasons: list[str]
    series_observation_count: int


ALLOWED_TRANSITIONS: dict[CaseStatus, frozenset[CaseStatus]] = {
    CaseStatus.DRAFT: frozenset({CaseStatus.DATA_VALIDATION}),
    CaseStatus.DATA_VALIDATION: frozenset({CaseStatus.READY_FOR_FORECAST, CaseStatus.FAILED}),
    CaseStatus.READY_FOR_FORECAST: frozenset({CaseStatus.FORECASTING}),
    CaseStatus.FORECASTING: frozenset({CaseStatus.INTERPRETING, CaseStatus.FAILED}),
    CaseStatus.INTERPRETING: frozenset({CaseStatus.INVESTIGATION_PENDING, CaseStatus.FAILED}),
    CaseStatus.INVESTIGATION_PENDING: frozenset({CaseStatus.READY_FOR_REVIEW, CaseStatus.FAILED}),
    CaseStatus.READY_FOR_REVIEW: frozenset({CaseStatus.UNDER_HUMAN_REVIEW}),
    CaseStatus.UNDER_HUMAN_REVIEW: frozenset(
        {CaseStatus.COMPLETED, CaseStatus.REJECTED, CaseStatus.INVESTIGATION_PENDING}
    ),
    CaseStatus.COMPLETED: frozenset(),
    CaseStatus.REJECTED: frozenset(),
    CaseStatus.FAILED: frozenset({CaseStatus.DATA_VALIDATION}),
}


def validate_case_dates(start: date, end: date, horizon: int) -> None:
    reasons = []
    if end < start:
        reasons.append("promotion_end_week must not precede promotion_start_week")
    if not 4 <= horizon <= 8:
        reasons.append("forecast_horizon_weeks must be between 4 and 8")
    if reasons:
        raise CaseReadinessError(reasons)


def assess_readiness(session: Session, case: DiagnosticCase) -> CaseReadiness:
    reasons: list[str] = []
    dataset = session.get(Dataset, case.dataset_id)
    if dataset is None:
        reasons.append("dataset does not exist")
    elif dataset.upload_status not in {DatasetStatus.VALID, DatasetStatus.VALID_WITH_WARNINGS}:
        reasons.append("dataset must pass validation before forecasting")
    elif not dataset.validation_summary_json.get("forecast_eligible_series"):
        reasons.append("dataset contains no forecast-eligible series")

    series_id = f"{case.sku_id}|{case.channel}|{case.region}"
    if dataset and series_id not in dataset.validation_summary_json.get(
        "forecast_eligible_series", []
    ):
        reasons.append("selected series is not forecast-eligible")

    statement = select(WeeklyFmcgSale).where(
        WeeklyFmcgSale.source_dataset_id == case.dataset_id,
        WeeklyFmcgSale.sku_id == case.sku_id,
        WeeklyFmcgSale.channel == case.channel,
        WeeklyFmcgSale.region == case.region,
    )
    rows = list(session.scalars(statement))
    if not rows:
        reasons.append("selected series grain has no ingested weekly observations")
    elif not any(
        row.promo_flag
        and case.promotion_start_week <= row.week_start_date <= case.promotion_end_week
        for row in rows
    ):
        reasons.append("promotion window has no promoted observation in the selected series")
    return CaseReadiness(not reasons, reasons, len(rows))


def transition_case(case: DiagnosticCase, target: CaseStatus) -> None:
    if target not in ALLOWED_TRANSITIONS[case.status]:
        raise InvalidCaseTransitionError(f"Cannot transition {case.status.value} to {target.value}")
    case.status = target


def scoped_case_query(user_id: str, role: str) -> Select[tuple[DiagnosticCase]]:
    statement = select(DiagnosticCase)
    if role != "ADMIN" and role != "COMMERCIAL_DIRECTOR":
        statement = statement.where(DiagnosticCase.created_by == user_id)
    return statement
