from dataclasses import asdict, dataclass
from typing import Any

from app.domain.classification import ClassificationResult
from app.domain.interpretation import InterpretationResult
from app.domain.investigations import InvestigationPlanResult
from app.domain.simulations import DecisionSimulationResult

OUTPUT_VERSION = "fmcg-executive-output/1.0.0"
FINAL_REVIEW_STATEMENT = (
    "This output supports leadership review. It does not make or execute the final "
    "commercial decision."
)
SECTION_ORDER = (
    "growth_signal_summary",
    "forecast_evidence",
    "growth_quality_judgment",
    "risk_classification",
    "investigation_plan",
    "decision_simulation",
    "priority",
    "recommended_human_owner",
    "evidence_confidence",
    "decision_affected",
    "next_verification_actions",
    "final_human_review_statement",
)


@dataclass(frozen=True)
class ExecutiveOutputResult:
    output_version: str
    review_label: str
    sections: dict[str, Any]
    markdown: str


def _bullet_lines(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values) or "- None recorded"


def generate_executive_output(
    interpretation: InterpretationResult,
    classification: ClassificationResult,
    plan: InvestigationPlanResult,
    simulations: list[DecisionSimulationResult],
) -> ExecutiveOutputResult:
    primary = classification.primary_class.value if classification.primary_class else None
    sections: dict[str, Any] = {
        "growth_signal_summary": interpretation.growth_signal_summary,
        "forecast_evidence": interpretation.facts,
        "growth_quality_judgment": {
            "candidate_judgment": primary,
            "interpretation": interpretation.interpretation_statements,
            "uncertainty": interpretation.uncertainty_notes,
        },
        "risk_classification": {
            "primary": primary,
            "secondary": [item.value for item in classification.secondary_classes],
            "rule_version": classification.rule_version,
        },
        "investigation_plan": [item.to_dict() for item in plan.items],
        "decision_simulation": [asdict(item) for item in simulations],
        "priority": classification.priority.value,
        "recommended_human_owner": plan.recommended_owner,
        "evidence_confidence": classification.evidence_confidence.value,
        "decision_affected": plan.decision_affected,
        "next_verification_actions": list(
            dict.fromkeys(gap for item in plan.items for gap in item.missing_evidence)
        ),
        "final_human_review_statement": FINAL_REVIEW_STATEMENT,
    }
    if tuple(sections) != SECTION_ORDER:
        raise RuntimeError("Executive output section order changed")
    risk = sections["risk_classification"]
    verification = sections["next_verification_actions"]
    markdown = f"""# FMCG Growth Quality Diagnostic

`DRAFT — HUMAN REVIEW PENDING`

## 1. Growth signal summary

{interpretation.growth_signal_summary}

## 2. Forecast evidence

{_bullet_lines([f"{item['key']}: {item['value']}" for item in interpretation.facts])}

## 3. Growth-quality judgment

Candidate judgment: {primary or "No supported risk class"}.
This remains subject to human validation.

## 4. Primary and secondary risk classification

- Primary: {risk["primary"] or "None — insufficient evidence"}
- Secondary: {", ".join(risk["secondary"]) or "None"}
- Rule version: {risk["rule_version"]}

## 5. Structured investigation plan

{_bullet_lines([item.question for item in plan.items])}

## 6. Neutral decision simulations

{_bullet_lines([f"{item.option.value}: {item.decision_being_tested}" for item in simulations])}

## 7. Priority

{classification.priority.value}

## 8. Recommended human owner

{plan.recommended_owner}

## 9. Evidence confidence

{classification.evidence_confidence.value}

## 10. Decision affected

{plan.decision_affected}

## 11. Exact next verification actions

{_bullet_lines(verification)}

## 12. Final human-review statement

{FINAL_REVIEW_STATEMENT}
"""
    forbidden = (
        "automatically",
        "the model recommends",
        "forecast proves",
        "final decision is confirmed",
    )
    if any(phrase in markdown.casefold() for phrase in forbidden):
        raise ValueError("Executive output contains prohibited language")
    if markdown.count(FINAL_REVIEW_STATEMENT) != 1:
        raise RuntimeError("Human-review statement must appear exactly once")
    return ExecutiveOutputResult(OUTPUT_VERSION, "DRAFT — HUMAN REVIEW PENDING", sections, markdown)
