from dataclasses import replace

import pytest

from app.domain.classification import ClassificationInput, GrowthQualityClass, Priority, classify
from app.domain.executive_outputs import FINAL_REVIEW_STATEMENT, generate_executive_output
from app.domain.interpretation import InterpretationInput, InterpretationResult, interpret
from app.domain.investigations import build_investigation_plan
from app.domain.simulations import DecisionOption, simulate_options


def candidate_result(candidates: list[str], confidence: str = "STRONG") -> InterpretationResult:
    base = interpret(
        InterpretationInput(
            {
                "forecast_direction": "STABLE",
                "baseline_comparison": "AT_BASELINE",
                "retention_status": "SUSTAINED",
                "decay_signal": "NONE",
                "uncertainty_level": "LOW",
            },
            [],
            adjacent_series_available=True,
        )
    )
    return replace(
        base,
        candidate_risks=candidates,
        supporting_evidence={item: ["fixture_evidence"] for item in candidates},
        evidence_confidence=confidence,
    )


@pytest.mark.parametrize(
    ("scenario", "candidates", "expected", "priority", "owner"),
    [
        (
            "A",
            ["HEALTHY_GROWTH_CANDIDATE"],
            "HEALTHY_GROWTH_CANDIDATE",
            "HEALTHY_CANDIDATE",
            "SALES_OPERATIONS",
        ),
        (
            "B",
            ["TEMPORARY_UPLIFT"],
            "TEMPORARY_UPLIFT",
            "INVESTIGATION_RECOMMENDED",
            "SALES_OPERATIONS",
        ),
        (
            "C",
            ["PULL_FORWARD_RISK"],
            "PULL_FORWARD_RISK",
            "INVESTIGATION_RECOMMENDED",
            "DEMAND_PLANNING",
        ),
        (
            "D",
            ["LOADING_RISK", "CHANNEL_STOCK_PRESSURE"],
            "LOADING_RISK",
            "P1_COMMERCIAL_REVIEW",
            "SALES_OPERATIONS",
        ),
        (
            "E",
            ["DISCOUNT_DEPENDENCY_RISK"],
            "DISCOUNT_DEPENDENCY_RISK",
            "INVESTIGATION_RECOMMENDED",
            "REVENUE_GROWTH_MANAGEMENT",
        ),
        (
            "F",
            ["MARGIN_VALUE_QUALITY_RISK"],
            "MARGIN_VALUE_QUALITY_RISK",
            "P1_COMMERCIAL_REVIEW",
            "FINANCE",
        ),
        (
            "G",
            ["CANNIBALIZATION_RISK"],
            "CANNIBALIZATION_RISK",
            "INVESTIGATION_RECOMMENDED",
            "CATEGORY_MANAGEMENT",
        ),
        (
            "H",
            ["PULL_FORWARD_RISK", "DISCOUNT_DEPENDENCY_RISK"],
            "PULL_FORWARD_RISK",
            "P1_COMMERCIAL_REVIEW",
            "DEMAND_PLANNING",
        ),
    ],
)
def test_required_scenario_journey(
    scenario: str, candidates: list[str], expected: str, priority: str, owner: str
) -> None:
    interpretation = candidate_result(candidates)
    classification = classify(ClassificationInput(interpretation))
    plan = build_investigation_plan(classification, set())
    simulations = simulate_options(classification, plan)
    output = generate_executive_output(interpretation, classification, plan, simulations)
    assert scenario
    assert classification.primary_class == GrowthQualityClass(expected)
    assert classification.priority == Priority(priority)
    assert plan.recommended_owner == owner
    assert {item.option for item in simulations} == set(DecisionOption)
    assert all(item.human_review_required for item in simulations)
    assert FINAL_REVIEW_STATEMENT in output.markdown
    assert "execute this option" not in output.markdown.casefold()


def test_scenario_i_insufficient_evidence_is_honest_and_specific() -> None:
    interpretation = candidate_result(["PULL_FORWARD_RISK"], "INSUFFICIENT")
    classification = classify(ClassificationInput(interpretation))
    plan = build_investigation_plan(classification, set())
    assert classification.primary_class is None
    assert classification.evidence_confidence.value == "INSUFFICIENT"
    assert plan.items[0].missing_evidence
    assert plan.items[0].recommended_human_owner == "COMMERCIAL_DIRECTOR"
