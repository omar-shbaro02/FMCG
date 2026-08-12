import uuid
from datetime import timedelta
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.auth import AuthenticatedUser, UserRole
from app.domain.baselines import BaselineInput, calculate_baseline
from app.domain.baselines.calculator import BaselineCalculationError
from app.models.entities import AuditEvent, BaselineCalculation, DiagnosticCase, WeeklyFmcgSale
from app.schemas.baselines import BaselineCalculationRequest, BaselineCalculationResponse
from app.security import require_roles

router = APIRouter(prefix="/api/diagnostic-cases", tags=["baselines"])


@router.post(
    "/{case_id}/baseline-calculations",
    response_model=BaselineCalculationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_baseline(
    case_id: uuid.UUID,
    request: BaselineCalculationRequest,
    actor: Annotated[
        AuthenticatedUser,
        Depends(require_roles(UserRole.ADMIN, UserRole.COMMERCIAL_DIRECTOR)),
    ],
    session: Annotated[Session, Depends(get_db)],
) -> BaselineCalculation:
    case = session.get(DiagnosticCase, case_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Diagnostic case not found"
        )
    rows = list(
        session.scalars(
            select(WeeklyFmcgSale)
            .where(
                WeeklyFmcgSale.source_dataset_id == case.dataset_id,
                WeeklyFmcgSale.sku_id == case.sku_id,
                WeeklyFmcgSale.channel == case.channel,
                WeeklyFmcgSale.region == case.region,
            )
            .order_by(WeeklyFmcgSale.week_start_date)
        )
    )
    history = [
        BaselineInput(
            row.week_start_date,
            Decimal(row.sell_out_units),
            row.promo_flag,
            row.out_of_stock_flag,
        )
        for row in rows
    ]
    horizon = [
        case.promotion_end_week + timedelta(weeks=week)
        for week in range(1, case.forecast_horizon_weeks + 1)
    ]
    try:
        result = calculate_baseline(
            history,
            promotion_start=case.promotion_start_week,
            horizon_weeks=horizon,
            method=request.method,
            recent_weeks=request.recent_weeks,
        )
    except BaselineCalculationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    calculation = BaselineCalculation(
        diagnostic_case_id=case.id,
        baseline_method=result.method.value,
        baseline_start_week=result.period_start,
        baseline_end_week=result.period_end,
        baseline_values_json={
            "input_values": result.input_values,
            "output_values": result.output_values,
        },
        assumptions_json={"items": result.assumptions},
        quality_notes_json={
            "excluded_weeks": result.excluded_weeks,
            "out_of_stock_effects": result.out_of_stock_effects,
            "promotion_contamination_notes": result.promotion_contamination_notes,
            "data_quality_score": str(result.data_quality_score),
        },
    )
    session.add(calculation)
    session.flush()
    session.add(
        AuditEvent(
            actor_id=uuid.UUID(actor.id),
            event_type="BASELINE_CALCULATED",
            entity_type="baseline_calculation",
            entity_id=calculation.id,
            before_json=None,
            after_json={
                "case_id": str(case.id),
                "method": result.method.value,
                "data_quality_score": str(result.data_quality_score),
            },
            correlation_id=str(uuid.uuid4()),
        )
    )
    session.commit()
    session.refresh(calculation)
    return calculation
