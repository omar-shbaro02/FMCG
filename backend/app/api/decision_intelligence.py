import uuid
from dataclasses import asdict
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.auth import REVIEWER_ROLES, AuthenticatedUser, UserRole
from app.domain.cases import transition_case
from app.domain.classification import ClassificationInput, classify
from app.domain.executive_outputs import generate_executive_output
from app.domain.interpretation import InterpretationInput, interpret
from app.domain.investigations import build_investigation_plan
from app.domain.simulations import simulate_options
from app.models.entities import (
    AuditEvent,
    CaseStatus,
    DecisionSimulation,
    DiagnosticCase,
    ExecutiveOutput,
    ForecastEvidence,
    ForecastRun,
    GrowthQualityAssessment,
    InvestigationPlan,
    ReviewStatus,
)
from app.schemas.decision_intelligence import DecisionIntelligenceResponse
from app.security import require_roles

router = APIRouter(tags=["decision intelligence"])


def _latest_evidence(session: Session, case_id: uuid.UUID) -> ForecastEvidence | None:
    return session.scalar(
        select(ForecastEvidence)
        .join(ForecastRun, ForecastRun.id == ForecastEvidence.forecast_run_id)
        .where(ForecastRun.diagnostic_case_id == case_id)
        .order_by(ForecastEvidence.created_at.desc())
    )


@router.post(
    "/api/diagnostic-cases/{case_id}/decision-intelligence",
    response_model=DecisionIntelligenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_decision_intelligence(
    case_id: uuid.UUID,
    actor: Annotated[
        AuthenticatedUser,
        Depends(require_roles(UserRole.ADMIN, UserRole.COMMERCIAL_DIRECTOR)),
    ],
    session: Annotated[Session, Depends(get_db)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> ExecutiveOutput:
    if idempotency_key:
        existing_event = session.scalar(
            select(AuditEvent).where(
                AuditEvent.correlation_id == f"decision:{case_id}:{idempotency_key}"
            )
        )
        if existing_event:
            existing_output = session.get(ExecutiveOutput, existing_event.entity_id)
            if existing_output:
                return existing_output
    case = session.get(DiagnosticCase, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Diagnostic case not found")
    if case.status != CaseStatus.INTERPRETING:
        raise HTTPException(status_code=409, detail="Case is not ready for interpretation")
    evidence = _latest_evidence(session, case_id)
    if evidence is None:
        raise HTTPException(status_code=422, detail="Forecast evidence is required")
    derived = evidence.confidence_interval_json.get("derived_values", {})
    evidence_values: dict[str, Any] = {
        "forecast_direction": evidence.forecast_direction,
        "baseline_comparison": evidence.baseline_comparison,
        "retention_status": evidence.post_promo_retention_status,
        "decay_signal": evidence.decay_signal,
        "uncertainty_level": evidence.uncertainty_level,
        "sell_in_sell_out_divergence": evidence.confidence_interval_json.get(
            "sell_in_sell_out_divergence"
        ),
        **(derived if isinstance(derived, dict) else {}),
    }
    interpretation = interpret(
        InterpretationInput(evidence_values, evidence.data_quality_notes_json)
    )
    classification = classify(ClassificationInput(interpretation))
    available = {item["key"].replace("_", " ") for item in interpretation.facts}
    plan = build_investigation_plan(classification, available)
    simulations = simulate_options(classification, plan)
    executive = generate_executive_output(interpretation, classification, plan, simulations)

    assessment = GrowthQualityAssessment(
        diagnostic_case_id=case.id,
        assessment_status="DRAFT",
        growth_signal_summary=interpretation.growth_signal_summary,
        growth_quality_judgment=(
            classification.primary_class.value
            if classification.primary_class
            else "NO_SUPPORTED_RISK_CLASS"
        ),
        primary_risk_class=(
            classification.primary_class.value
            if classification.primary_class
            else "INVESTIGATION_RECOMMENDED"
        ),
        secondary_risk_classes_json=[item.value for item in classification.secondary_classes],
        interpretation_evidence_json={
            "facts": interpretation.facts,
            "statements": interpretation.interpretation_statements,
            "supporting": classification.supporting_evidence,
            "contradicting": classification.contradicting_evidence,
            "missing": interpretation.missing_evidence,
            "exclusions": classification.exclusion_reasons,
            "priority": classification.priority.value,
            "evidence_confidence": classification.evidence_confidence.value,
        },
        uncertainty_notes_json=interpretation.uncertainty_notes,
        rule_version=classification.rule_version,
        prompt_version=None,
    )
    session.add(assessment)
    session.flush()
    stored_plan = InvestigationPlan(
        diagnostic_case_id=case.id,
        assessment_id=assessment.id,
        investigation_items_json=[item.to_dict() for item in plan.items],
        recommended_owner=plan.recommended_owner,
        decision_affected=plan.decision_affected,
        acting_too_early_risks_json=plan.acting_too_early_risks,
        evidence_confidence=plan.evidence_confidence,
    )
    session.add(stored_plan)
    for simulation in simulations:
        session.add(
            DecisionSimulation(
                diagnostic_case_id=case.id,
                assessment_id=assessment.id,
                option=simulation.option.value,
                assumptions_json=simulation.required_assumptions,
                potential_benefits_json=simulation.plausible_benefits,
                potential_risks_json=simulation.plausible_risks,
                evidence_requirements_json=simulation.verification_needed,
                confidence=simulation.confidence,
            )
        )
    output_json = {**executive.sections, "simulations": [asdict(item) for item in simulations]}
    output = ExecutiveOutput(
        diagnostic_case_id=case.id,
        assessment_id=assessment.id,
        output_version=executive.output_version,
        output_json=output_json,
        output_markdown=executive.markdown,
        generated_by=actor.email,
        human_review_status=ReviewStatus.PENDING,
    )
    session.add(output)
    transition_case(case, CaseStatus.INVESTIGATION_PENDING)
    transition_case(case, CaseStatus.READY_FOR_REVIEW)
    session.flush()
    session.add(
        AuditEvent(
            actor_id=uuid.UUID(actor.id),
            event_type="DECISION_INTELLIGENCE_DRAFT_CREATED",
            entity_type="executive_output",
            entity_id=output.id,
            before_json=None,
            after_json={
                "case_id": str(case.id),
                "assessment_id": str(assessment.id),
                "rule_version": classification.rule_version,
                "review_status": ReviewStatus.PENDING.value,
            },
            correlation_id=(
                f"decision:{case.id}:{idempotency_key}" if idempotency_key else str(uuid.uuid4())
            ),
        )
    )
    session.commit()
    session.refresh(output)
    return output


@router.get(
    "/api/diagnostic-cases/{case_id}/decision-intelligence/latest",
    response_model=DecisionIntelligenceResponse,
)
def get_latest_decision_intelligence(
    case_id: uuid.UUID,
    _: Annotated[
        AuthenticatedUser,
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.COMMERCIAL_DIRECTOR,
                UserRole.READ_ONLY_EXECUTIVE,
                *REVIEWER_ROLES,
            )
        ),
    ],
    session: Annotated[Session, Depends(get_db)],
) -> ExecutiveOutput:
    output = session.scalar(
        select(ExecutiveOutput)
        .where(ExecutiveOutput.diagnostic_case_id == case_id)
        .order_by(ExecutiveOutput.generated_at.desc())
    )
    if output is None:
        raise HTTPException(status_code=404, detail="Decision intelligence not found")
    return output
