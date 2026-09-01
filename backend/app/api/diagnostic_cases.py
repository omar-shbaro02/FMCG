import uuid
from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.auth import AuthenticatedUser, UserRole
from app.domain.cases import assess_readiness, transition_case
from app.models.entities import AuditEvent, CaseStatus, Dataset, DiagnosticCase
from app.schemas.diagnostic_cases import (
    CaseReadinessResponse,
    DiagnosticCaseCreate,
    DiagnosticCaseListResponse,
    DiagnosticCaseResponse,
    DiagnosticCaseUpdate,
)
from app.security import require_roles

router = APIRouter(prefix="/api/diagnostic-cases", tags=["diagnostic-cases"])
CASE_MANAGERS = (UserRole.ADMIN, UserRole.COMMERCIAL_DIRECTOR)
CASE_READERS = (*CASE_MANAGERS, UserRole.READ_ONLY_EXECUTIVE)


def _get_case(session: Session, case_id: uuid.UUID) -> DiagnosticCase:
    case = session.get(DiagnosticCase, case_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Diagnostic case not found"
        )
    return case


def _audit(
    session: Session,
    actor: AuthenticatedUser,
    case: DiagnosticCase,
    event: str,
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
) -> None:
    session.add(
        AuditEvent(
            actor_id=uuid.UUID(actor.id),
            event_type=event,
            entity_type="diagnostic_case",
            entity_id=case.id,
            before_json=before,
            after_json=after,
            correlation_id=str(uuid.uuid4()),
        )
    )


@router.post("", response_model=DiagnosticCaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(
    request: DiagnosticCaseCreate,
    actor: Annotated[AuthenticatedUser, Depends(require_roles(*CASE_MANAGERS))],
    session: Annotated[Session, Depends(get_db)],
) -> DiagnosticCase:
    if session.get(Dataset, request.dataset_id) is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Dataset not found"
        )
    case = DiagnosticCase(
        title=request.title,
        description=request.management_concern_note,
        dataset_id=request.dataset_id,
        sku_id=request.sku_id,
        channel=request.channel,
        region=request.region,
        promotion_start_week=request.promotion_start_week,
        promotion_end_week=request.promotion_end_week,
        forecast_horizon_weeks=request.forecast_horizon_weeks,
        status=CaseStatus.DRAFT,
        created_by=uuid.UUID(actor.id),
    )
    session.add(case)
    session.flush()
    _audit(session, actor, case, "DIAGNOSTIC_CASE_CREATED", None, {"status": "DRAFT"})
    session.commit()
    session.refresh(case)
    return case


@router.get("", response_model=DiagnosticCaseListResponse)
def list_cases(
    actor: Annotated[AuthenticatedUser, Depends(require_roles(*CASE_READERS))],
    session: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 25,
) -> DiagnosticCaseListResponse:
    query = select(DiagnosticCase)
    total = session.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = list(
        session.scalars(
            query.order_by(DiagnosticCase.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    return DiagnosticCaseListResponse(items=items, page=page, page_size=page_size, total=total)


@router.get("/{case_id}", response_model=DiagnosticCaseResponse)
def get_case(
    case_id: uuid.UUID,
    _: Annotated[AuthenticatedUser, Depends(require_roles(*CASE_READERS))],
    session: Annotated[Session, Depends(get_db)],
) -> DiagnosticCase:
    return _get_case(session, case_id)


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case(
    case_id: uuid.UUID,
    actor: Annotated[AuthenticatedUser, Depends(require_roles(*CASE_MANAGERS))],
    session: Annotated[Session, Depends(get_db)],
) -> None:
    case = _get_case(session, case_id)
    snapshot = {
        "title": case.title,
        "status": case.status.value,
        "dataset_id": str(case.dataset_id),
        "sku_id": case.sku_id,
        "channel": case.channel,
        "region": case.region,
    }
    _audit(session, actor, case, "DIAGNOSTIC_CASE_DELETED", snapshot, None)
    session.delete(case)
    session.commit()


@router.patch("/{case_id}", response_model=DiagnosticCaseResponse)
def update_case(
    case_id: uuid.UUID,
    request: DiagnosticCaseUpdate,
    actor: Annotated[AuthenticatedUser, Depends(require_roles(*CASE_MANAGERS))],
    session: Annotated[Session, Depends(get_db)],
) -> DiagnosticCase:
    case = _get_case(session, case_id)
    if case.status != CaseStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Only draft cases can be edited"
        )
    before = {
        "title": case.title,
        "sku_id": case.sku_id,
        "channel": case.channel,
        "region": case.region,
    }
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(case, "description" if field == "management_concern_note" else field, value)
    if case.promotion_end_week < case.promotion_start_week:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid promotion window"
        )
    case.updated_at = datetime.now(UTC)
    _audit(
        session,
        actor,
        case,
        "DIAGNOSTIC_CASE_UPDATED",
        before,
        request.model_dump(mode="json", exclude_unset=True),
    )
    session.commit()
    session.refresh(case)
    return case


@router.get("/{case_id}/readiness", response_model=CaseReadinessResponse)
def case_readiness(
    case_id: uuid.UUID,
    _: Annotated[AuthenticatedUser, Depends(require_roles(*CASE_MANAGERS))],
    session: Annotated[Session, Depends(get_db)],
) -> CaseReadinessResponse:
    case = _get_case(session, case_id)
    result = assess_readiness(session, case)
    return CaseReadinessResponse(**result.__dict__, status=case.status)


@router.post("/{case_id}/submit", response_model=CaseReadinessResponse)
def submit_case(
    case_id: uuid.UUID,
    actor: Annotated[AuthenticatedUser, Depends(require_roles(*CASE_MANAGERS))],
    session: Annotated[Session, Depends(get_db)],
) -> CaseReadinessResponse:
    case = _get_case(session, case_id)
    if case.status != CaseStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Only draft cases can be submitted"
        )
    result = assess_readiness(session, case)
    if not result.ready:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Case is not ready for forecasting", "reasons": result.reasons},
        )
    transition_case(case, CaseStatus.DATA_VALIDATION)
    transition_case(case, CaseStatus.READY_FOR_FORECAST)
    case.updated_at = datetime.now(UTC)
    _audit(
        session,
        actor,
        case,
        "DIAGNOSTIC_CASE_SUBMITTED",
        {"status": "DRAFT"},
        {"status": case.status.value},
    )
    session.commit()
    return CaseReadinessResponse(**result.__dict__, status=case.status)
