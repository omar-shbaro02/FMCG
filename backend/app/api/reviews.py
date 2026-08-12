import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.auth import REVIEWER_ROLES, AuthenticatedUser, UserRole
from app.domain.cases import transition_case
from app.models.entities import (
    AuditEvent,
    CaseStatus,
    DiagnosticCase,
    ExecutiveOutput,
    FeedbackEvent,
    HumanReview,
    ReviewStatus,
)
from app.schemas.reviews import (
    FeedbackCreate,
    FeedbackResponse,
    HumanReviewCreate,
    HumanReviewResponse,
)
from app.security import require_roles

router = APIRouter(tags=["human review"])
REVIEW_ROLES = (UserRole.ADMIN, UserRole.COMMERCIAL_DIRECTOR, *REVIEWER_ROLES)
READ_ROLES = (*REVIEW_ROLES, UserRole.READ_ONLY_EXECUTIVE)


def _case_and_output(
    session: Session, case_id: uuid.UUID
) -> tuple[DiagnosticCase, ExecutiveOutput]:
    case = session.get(DiagnosticCase, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Diagnostic case not found")
    output = session.scalar(
        select(ExecutiveOutput)
        .where(ExecutiveOutput.diagnostic_case_id == case_id)
        .order_by(ExecutiveOutput.generated_at.desc())
    )
    if output is None:
        raise HTTPException(status_code=409, detail="A preserved executive draft is required")
    return case, output


@router.post(
    "/api/diagnostic-cases/{case_id}/reviews",
    response_model=HumanReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    case_id: uuid.UUID,
    request: HumanReviewCreate,
    actor: Annotated[AuthenticatedUser, Depends(require_roles(*REVIEW_ROLES))],
    session: Annotated[Session, Depends(get_db)],
) -> HumanReview:
    case, output = _case_and_output(session, case_id)
    if case.status not in {CaseStatus.READY_FOR_REVIEW, CaseStatus.UNDER_HUMAN_REVIEW}:
        raise HTTPException(status_code=409, detail="Case is not ready for human review")
    if request.review_status == ReviewStatus.PENDING:
        raise HTTPException(status_code=422, detail="A submitted review cannot remain pending")
    if request.review_status == ReviewStatus.VALIDATED_WITH_CHANGES and not (
        request.validated_risk_class and request.reviewer_comments
    ):
        raise HTTPException(
            status_code=422,
            detail="A corrected classification and comments are required for changes",
        )
    if (
        request.review_status == ReviewStatus.MORE_EVIDENCE_REQUIRED
        and not request.requested_evidence
    ):
        raise HTTPException(status_code=422, detail="Specific evidence requests are required")
    if case.status == CaseStatus.READY_FOR_REVIEW:
        transition_case(case, CaseStatus.UNDER_HUMAN_REVIEW)
    review = HumanReview(
        diagnostic_case_id=case.id,
        reviewer_id=uuid.UUID(actor.id),
        review_status=request.review_status,
        validated_risk_class=request.validated_risk_class,
        reviewer_comments=request.reviewer_comments,
        requested_evidence_json=[item.model_dump() for item in request.requested_evidence],
        final_decision_note=request.final_decision_note,
        reviewed_at=datetime.now(UTC),
    )
    session.add(review)
    session.flush()
    before_status = output.human_review_status
    output.human_review_status = request.review_status
    if request.review_status in {
        ReviewStatus.VALIDATED,
        ReviewStatus.VALIDATED_WITH_CHANGES,
    }:
        transition_case(case, CaseStatus.COMPLETED)
    elif request.review_status == ReviewStatus.REJECTED:
        transition_case(case, CaseStatus.REJECTED)
    elif request.review_status == ReviewStatus.MORE_EVIDENCE_REQUIRED:
        transition_case(case, CaseStatus.INVESTIGATION_PENDING)
    session.add(
        AuditEvent(
            actor_id=uuid.UUID(actor.id),
            event_type="HUMAN_REVIEW_RECORDED",
            entity_type="human_review",
            entity_id=review.id,
            before_json={"review_status": before_status.value},
            after_json={
                "review_status": request.review_status.value,
                "validated_risk_class": request.validated_risk_class,
                "case_status": case.status.value,
            },
            correlation_id=str(uuid.uuid4()),
        )
    )
    session.commit()
    session.refresh(review)
    return review


@router.get(
    "/api/diagnostic-cases/{case_id}/reviews",
    response_model=list[HumanReviewResponse],
)
def list_reviews(
    case_id: uuid.UUID,
    _: Annotated[AuthenticatedUser, Depends(require_roles(*READ_ROLES))],
    session: Annotated[Session, Depends(get_db)],
) -> list[HumanReview]:
    return list(
        session.scalars(
            select(HumanReview)
            .where(HumanReview.diagnostic_case_id == case_id)
            .order_by(HumanReview.created_at.desc())
        )
    )


@router.post(
    "/api/diagnostic-cases/{case_id}/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_feedback(
    case_id: uuid.UUID,
    request: FeedbackCreate,
    actor: Annotated[AuthenticatedUser, Depends(require_roles(*REVIEW_ROLES))],
    session: Annotated[Session, Depends(get_db)],
) -> FeedbackEvent:
    if session.get(DiagnosticCase, case_id) is None:
        raise HTTPException(status_code=404, detail="Diagnostic case not found")
    feedback = FeedbackEvent(
        diagnostic_case_id=case_id,
        submitted_by=uuid.UUID(actor.id),
        feedback_type=request.feedback_type,
        observed_outcome_json=request.observed_outcome,
        classification_correct=request.classification_correct,
        simulation_useful=request.simulation_useful,
        notes=request.notes,
    )
    session.add(feedback)
    session.flush()
    session.add(
        AuditEvent(
            actor_id=uuid.UUID(actor.id),
            event_type="OUTCOME_FEEDBACK_RECORDED",
            entity_type="feedback_event",
            entity_id=feedback.id,
            before_json=None,
            after_json={"case_id": str(case_id), "feedback_type": request.feedback_type},
            correlation_id=str(uuid.uuid4()),
        )
    )
    session.commit()
    session.refresh(feedback)
    return feedback
