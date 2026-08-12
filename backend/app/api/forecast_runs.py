import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.forecast import get_forecast_adapter
from app.adapters.forecast.schemas import (
    ForecastContext,
    ForecastCovariates,
    ForecastRequest,
    HistoryPoint,
)
from app.adapters.forecast.timesfm_adapter import TimesFMAdapterException
from app.config import Settings, get_settings
from app.database import get_db
from app.domain.auth import AuthenticatedUser, UserRole
from app.domain.cases import transition_case
from app.domain.forecasts import CommercialSeriesPoint, derive_evidence
from app.models.entities import (
    AuditEvent,
    BaselineCalculation,
    CaseStatus,
    DiagnosticCase,
    ForecastEvidence,
    ForecastRun,
    WeeklyFmcgSale,
)
from app.schemas.forecasts import ForecastEvidenceResponse, ForecastRunResponse
from app.security import require_roles

router = APIRouter(tags=["forecasts"])


@router.post(
    "/api/diagnostic-cases/{case_id}/forecast-runs",
    response_model=ForecastRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_forecast_run(
    case_id: uuid.UUID,
    actor: Annotated[
        AuthenticatedUser,
        Depends(require_roles(UserRole.ADMIN, UserRole.COMMERCIAL_DIRECTOR)),
    ],
    session: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ForecastRun:
    case = session.get(DiagnosticCase, case_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Diagnostic case not found"
        )
    if case.status != CaseStatus.READY_FOR_FORECAST:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Case is not ready for forecast"
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
    baseline = session.scalar(
        select(BaselineCalculation)
        .where(BaselineCalculation.diagnostic_case_id == case.id)
        .order_by(BaselineCalculation.created_at.desc())
    )
    if not rows or baseline is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Forecast requires an ingested series and baseline calculation",
        )
    series_id = f"{case.sku_id}|{case.channel}|{case.region}"
    request = ForecastRequest(
        series_id=series_id,
        horizon=case.forecast_horizon_weeks,
        history=[
            HistoryPoint(week_start_date=row.week_start_date, value=float(row.sell_out_units))
            for row in rows
        ],
        covariates=ForecastCovariates(
            promo_flag=[row.promo_flag for row in rows],
            discount_depth=[float(row.discount_depth) for row in rows],
            out_of_stock_flag=[row.out_of_stock_flag for row in rows],
        ),
        context=ForecastContext(
            sku_id=case.sku_id,
            channel=case.channel,
            region=case.region,
            promotion_start_week=case.promotion_start_week,
            promotion_end_week=case.promotion_end_week,
        ),
    )
    adapter = get_forecast_adapter(settings.forecast_adapter, settings)
    metadata = adapter.get_metadata()
    run = ForecastRun(
        diagnostic_case_id=case.id,
        adapter_name=metadata["adapter_name"],
        adapter_version=metadata["adapter_version"],
        forecast_target=request.forecast_target,
        series_id=series_id,
        horizon_weeks=request.horizon,
        run_status="RUNNING",
        input_snapshot_json=request.model_dump(mode="json"),
        output_json=None,
        error_json=None,
        started_at=datetime.now(UTC),
        created_by=uuid.UUID(actor.id),
    )
    transition_case(case, CaseStatus.FORECASTING)
    session.add(run)
    session.flush()
    try:
        forecast = adapter.forecast(request)
    except TimesFMAdapterException as exc:
        run.run_status = "FAILED"
        run.error_json = exc.error.model_dump(mode="json")
        run.completed_at = datetime.now(UTC)
        case.status = CaseStatus.FAILED
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=run.error_json
        ) from exc

    baseline_points = baseline.baseline_values_json.get("output_values", [])
    baseline_values = [
        float(point["value"]) for point in baseline_points if isinstance(point, dict)
    ]
    derived = derive_evidence(
        forecast,
        baseline_values,
        [
            CommercialSeriesPoint(
                row.week_start_date,
                float(row.sell_out_units),
                float(row.sell_in_units),
            )
            for row in rows
        ],
    )
    output: dict[str, Any] = forecast.model_dump(mode="json")
    latency = getattr(adapter, "last_latency_seconds", None)
    output["run_metadata"] = {"latency_seconds": latency, **metadata}
    run.output_json = output
    run.run_status = "COMPLETED"
    run.completed_at = datetime.now(UTC)
    evidence = ForecastEvidence(
        forecast_run_id=run.id,
        forecast_target=forecast.forecast_target,
        forecast_horizon=forecast.forecast_horizon,
        series_id=forecast.series_id,
        forecast_direction=derived.forecast_direction.value,
        forecasted_values_json=[
            point.model_dump(mode="json") for point in forecast.forecasted_values
        ],
        confidence_interval_json={
            **forecast.confidence_interval.model_dump(mode="json"),
            "derived_values": derived.evidence_values,
            "sell_in_sell_out_divergence": derived.sell_in_sell_out_divergence,
        },
        baseline_comparison=derived.baseline_comparison.value,
        post_promo_retention_status=derived.post_promo_retention_status.value,
        decay_signal=derived.decay_signal.value,
        uncertainty_level=derived.uncertainty_level.value,
        data_quality_notes_json=derived.data_quality_notes,
    )
    session.add(evidence)
    transition_case(case, CaseStatus.INTERPRETING)
    session.add(
        AuditEvent(
            actor_id=uuid.UUID(actor.id),
            event_type="FORECAST_RUN_COMPLETED",
            entity_type="forecast_run",
            entity_id=run.id,
            before_json=None,
            after_json={"case_id": str(case.id), "adapter": metadata, "status": "COMPLETED"},
            correlation_id=str(uuid.uuid4()),
        )
    )
    session.commit()
    session.refresh(run)
    return run


@router.get(
    "/api/diagnostic-cases/{case_id}/forecast-evidence",
    response_model=ForecastEvidenceResponse,
)
def get_forecast_evidence(
    case_id: uuid.UUID,
    _: Annotated[
        AuthenticatedUser,
        Depends(
            require_roles(
                UserRole.ADMIN, UserRole.COMMERCIAL_DIRECTOR, UserRole.READ_ONLY_EXECUTIVE
            )
        ),
    ],
    session: Annotated[Session, Depends(get_db)],
) -> ForecastEvidence:
    evidence = session.scalar(
        select(ForecastEvidence)
        .join(ForecastRun, ForecastRun.id == ForecastEvidence.forecast_run_id)
        .where(ForecastRun.diagnostic_case_id == case_id)
        .order_by(ForecastEvidence.created_at.desc())
    )
    if evidence is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Forecast evidence not found"
        )
    return evidence
