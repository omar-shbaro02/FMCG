from app.domain.classification import ClassificationInput, classify
from app.domain.executive_outputs import FINAL_REVIEW_STATEMENT, generate_executive_output
from app.domain.interpretation import InterpretationInput, interpret
from app.domain.investigations import build_investigation_plan
from app.domain.simulations import DecisionOption, simulate_options


def _workflow():
    interpretation = interpret(
        InterpretationInput(
            {
                "forecast_direction": "DECLINING",
                "baseline_comparison": "BELOW_BASELINE",
                "retention_status": "WEAK",
                "decay_signal": "STRONG",
                "uncertainty_level": "MEDIUM",
                "sell_in_sell_out_divergence": "MATERIAL_SELL_IN_EXCESS",
                "sell_in_to_sell_out_ratio": 1.5,
            },
            ["account stock has not been supplied"],
            stock_evidence_available=False,
        )
    )
    classification = classify(ClassificationInput(interpretation))
    plan = build_investigation_plan(
        classification,
        {"sell-in growth", "sell-out growth", "promotion uplift timing", "baseline"},
    )
    simulations = simulate_options(classification, plan)
    return interpretation, classification, plan, simulations


def test_investigation_plan_is_exact_owned_and_evidence_specific() -> None:
    _, _, plan, _ = _workflow()
    assert plan.items
    for item in plan.items:
        assert item.question.endswith("?")
        assert item.evidence_required
        assert item.recommended_human_owner
        assert item.decision_affected
        assert item.risk_if_leadership_acts_too_early
        assert set(item.available_evidence).isdisjoint(item.missing_evidence)


def test_simulator_returns_every_option_without_ranking_or_execution() -> None:
    _, _, _, simulations = _workflow()
    assert {item.option for item in simulations} == set(DecisionOption)
    assert len(simulations) == 7
    assert all(item.human_review_required for item in simulations)
    rendered = str(simulations).casefold()
    assert "recommended option" not in rendered
    assert "execute" not in rendered


def test_executive_output_has_frozen_sections_and_single_review_statement() -> None:
    interpretation, classification, plan, simulations = _workflow()
    output = generate_executive_output(interpretation, classification, plan, simulations)
    assert len(output.sections) == 12
    assert output.markdown.count(FINAL_REVIEW_STATEMENT) == 1
    assert output.review_label == "DRAFT — HUMAN REVIEW PENDING"
    assert output.sections["priority"] == classification.priority.value
    assert output.sections["evidence_confidence"] == classification.evidence_confidence.value


def test_insufficient_evidence_output_preserves_no_risk_class() -> None:
    interpretation = interpret(
        InterpretationInput(
            {
                "forecast_direction": "INSUFFICIENT",
                "baseline_comparison": "INSUFFICIENT",
                "uncertainty_level": "INSUFFICIENT",
            },
            [],
        )
    )
    classification = classify(ClassificationInput(interpretation))
    plan = build_investigation_plan(classification, set())
    output = generate_executive_output(
        interpretation, classification, plan, simulate_options(classification, plan)
    )
    assert output.sections["risk_classification"]["primary"] is None
    assert output.sections["evidence_confidence"] == "INSUFFICIENT"
