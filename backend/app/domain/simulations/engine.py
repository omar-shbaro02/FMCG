from dataclasses import dataclass
from enum import StrEnum

from app.domain.classification import ClassificationResult
from app.domain.investigations import InvestigationPlanResult


class DecisionOption(StrEnum):
    REPEAT_PROMOTION_IMMEDIATELY = "REPEAT_PROMOTION_IMMEDIATELY"
    SCALE_PROMOTION_BUDGET = "SCALE_PROMOTION_BUDGET"
    REWARD_AS_HEALTHY_GROWTH = "REWARD_AS_HEALTHY_GROWTH"
    PAUSE_AND_MONITOR = "PAUSE_AND_MONITOR"
    INVESTIGATE_FIRST = "INVESTIGATE_FIRST"
    REDESIGN_MECHANIC_BEFORE_REPEAT = "REDESIGN_MECHANIC_BEFORE_REPEAT"
    ESCALATE_P1_COMMERCIAL_REVIEW = "ESCALATE_P1_COMMERCIAL_REVIEW"


@dataclass(frozen=True)
class DecisionSimulationResult:
    option: DecisionOption
    decision_being_tested: str
    required_assumptions: list[str]
    evidence_supporting: list[str]
    evidence_against: list[str]
    plausible_benefits: list[str]
    plausible_risks: list[str]
    unresolved_uncertainty: list[str]
    verification_needed: list[str]
    affected_functions: list[str]
    confidence: str
    human_review_required: bool = True


OPTION_LANGUAGE: dict[DecisionOption, tuple[str, str, str]] = {
    DecisionOption.REPEAT_PROMOTION_IMMEDIATELY: (
        "Whether an immediate repeat could preserve near-term movement.",
        "May preserve near-term volume if the observed response persists.",
        "May repeat timing, discount, stock, or margin distortion.",
    ),
    DecisionOption.SCALE_PROMOTION_BUDGET: (
        "Whether greater promotion support could extend the observed response.",
        "May extend reach if growth is incremental and value-accretive.",
        "May amplify cost and distortion if growth quality is unresolved.",
    ),
    DecisionOption.REWARD_AS_HEALTHY_GROWTH: (
        "Whether the signal could be recognized as healthy growth.",
        "May recognize genuinely sustained consumer movement.",
        "May reward temporary, shifted, or value-dilutive volume.",
    ),
    DecisionOption.PAUSE_AND_MONITOR: (
        "Whether an additional observation window could clarify retention.",
        "May add actual post-promotion evidence without new exposure.",
        "May delay a time-sensitive commercial response.",
    ),
    DecisionOption.INVESTIGATE_FIRST: (
        "Whether evidence owners should resolve identified gaps before commitment.",
        "May reduce avoidable exposure by resolving material uncertainty.",
        "May consume time while the commercial window narrows.",
    ),
    DecisionOption.REDESIGN_MECHANIC_BEFORE_REPEAT: (
        "Whether a changed mechanic could address the observed risk pattern.",
        "May test a less distortion-prone source of demand.",
        "May introduce new assumptions without proving the original diagnosis.",
    ),
    DecisionOption.ESCALATE_P1_COMMERCIAL_REVIEW: (
        "Whether cross-functional leadership review is warranted before commitment.",
        "May align owners around converging high-impact risks.",
        "May add governance effort when risks later prove immaterial.",
    ),
}


def simulate_options(
    classification: ClassificationResult, plan: InvestigationPlanResult
) -> list[DecisionSimulationResult]:
    risk_labels = [
        item.value
        for item in ([classification.primary_class] if classification.primary_class else [])
        + classification.secondary_classes
    ]
    gaps = list(dict.fromkeys(gap for item in plan.items for gap in item.missing_evidence))
    owners = list(dict.fromkeys(item.recommended_human_owner for item in plan.items))
    results = []
    for option in DecisionOption:
        decision, benefit, risk = OPTION_LANGUAGE[option]
        results.append(
            DecisionSimulationResult(
                option=option,
                decision_being_tested=decision,
                required_assumptions=[
                    "Human owners validate the evidence relevant to this option."
                ],
                evidence_supporting=[f"Candidate class: {value}" for value in risk_labels],
                evidence_against=classification.exclusion_reasons,
                plausible_benefits=[benefit],
                plausible_risks=[risk, *plan.acting_too_early_risks],
                unresolved_uncertainty=gaps,
                verification_needed=gaps
                or ["Confirm current evidence with the named human owner."],
                affected_functions=owners,
                confidence=classification.evidence_confidence.value,
            )
        )
    return results
