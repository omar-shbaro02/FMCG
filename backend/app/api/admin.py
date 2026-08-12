from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.domain.auth import AuthenticatedUser, UserRole
from app.domain.classification import CLASSIFIER_RULE_VERSION
from app.domain.executive_outputs import OUTPUT_VERSION
from app.models.entities import AuditEvent, ForecastRun, User
from app.schemas.admin import AuditListResponse
from app.security import require_roles

router = APIRouter(prefix="/api/admin", tags=["admin"])
AdminActor = Annotated[AuthenticatedUser, Depends(require_roles(UserRole.ADMIN))]


@router.get("/audit-events", response_model=AuditListResponse)
def audit_events(
    _: AdminActor,
    session: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 25,
) -> AuditListResponse:
    total = session.scalar(select(func.count()).select_from(AuditEvent)) or 0
    items = list(
        session.scalars(
            select(AuditEvent)
            .order_by(AuditEvent.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    return AuditListResponse(items=items, page=page, page_size=page_size, total=total)


@router.get("/health")
def admin_health(_: AdminActor, session: Annotated[Session, Depends(get_db)]) -> dict[str, Any]:
    session.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "reachable", "secrets_exposed": False}


@router.get("/jobs")
def jobs(_: AdminActor, session: Annotated[Session, Depends(get_db)]) -> dict[str, Any]:
    failed = list(
        session.scalars(select(ForecastRun).where(ForecastRun.run_status == "FAILED").limit(100))
    )
    return {
        "background_worker": "NOT_CONFIGURED",
        "failed_forecast_runs": [
            {"id": str(item.id), "case_id": str(item.diagnostic_case_id), "status": item.run_status}
            for item in failed
        ],
    }


@router.get("/configuration-metadata")
def configuration_metadata(
    _: AdminActor,
    session: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    roles = [role.value for role in UserRole]
    users = session.scalar(select(func.count()).select_from(User)) or 0
    return {
        "user_count": users,
        "roles": roles,
        "forecast_adapter": settings.forecast_adapter,
        "classifier_version": CLASSIFIER_RULE_VERSION,
        "executive_output_version": OUTPUT_VERSION,
        "prompt_version": None,
        "secrets_included": False,
    }
