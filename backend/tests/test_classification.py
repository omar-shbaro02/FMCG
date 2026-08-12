import pytest

from app.domain.classification import (
    CLASSIFIER_RULE_VERSION,
    RULE_DEFINITIONS,
    ClassificationInput,
    EvidenceConfidence,
    GrowthQualityClass,
    Priority,
    classify,
)
from app.domain.interpretation import InterpretationInput, interpret


def result_for(*candidates: str, confidence: str = "STRONG"):
    result = interpret(
        InterpretationInput(
            {
                "forecast_direction": "FLAT",
                "baseline_comparison": "AT_BASELINE",
                "retention_status": "SUSTAINED",
                "decay_signal": "NONE",
                "uncertainty_level": "LOW",
            },
            [],
            adjacent_series_available=True,
        )
    )
    return result.__class__(
        result.growth_signal_summary,
        result.facts,
        result.interpretation_statements,
        list(candidates),
        {candidate: ["fixture_evidence"] for candidate in candidates},
        {},
        result.missing_evidence,
        result.uncertainty_notes,
        confidence,
    )


@pytest.mark.parametrize(
    ("candidate", "priority"),
    [
        ("HEALTHY_GROWTH_CANDIDATE", Priority.HEALTHY_CANDIDATE),
        ("TEMPORARY_UPLIFT", Priority.INVESTIGATION_RECOMMENDED),
        ("PULL_FORWARD_RISK", Priority.INVESTIGATION_RECOMMENDED),
        ("CANNIBALIZATION_RISK", Priority.INVESTIGATION_RECOMMENDED),
        ("DISCOUNT_DEPENDENCY_RISK", Priority.INVESTIGATION_RECOMMENDED),
        ("MARGIN_VALUE_QUALITY_RISK", Priority.P1_COMMERCIAL_REVIEW),
    ],
)
def test_each_major_fixture_class_has_deterministic_priority(
    candidate: str, priority: Priority
) -> None:
    classified = classify(ClassificationInput(result_for(candidate)))
    assert classified.primary_class == GrowthQualityClass(candidate)
    assert classified.priority is priority
    assert classified.rule_version == CLASSIFIER_RULE_VERSION


def test_loading_and_stock_pressure_converge_to_p1_with_one_primary() -> None:
    classified = classify(ClassificationInput(result_for("LOADING_RISK", "CHANNEL_STOCK_PRESSURE")))
    assert classified.primary_class is GrowthQualityClass.LOADING_RISK
    assert GrowthQualityClass.CHANNEL_STOCK_PRESSURE in classified.secondary_classes
    assert classified.priority is Priority.P1_COMMERCIAL_REVIEW


def test_insufficient_evidence_never_produces_a_risk_class() -> None:
    classified = classify(
        ClassificationInput(result_for("PULL_FORWARD_RISK", confidence="INSUFFICIENT"))
    )
    assert classified.primary_class is None
    assert classified.evidence_confidence is EvidenceConfidence.INSUFFICIENT
    assert classified.priority is Priority.INVESTIGATION_RECOMMENDED


def test_priority_is_independent_from_confidence() -> None:
    classified = classify(
        ClassificationInput(
            result_for(confidence="WEAK"),
            business_impact="HIGH",
            critical_evidence_incomplete=True,
        )
    )
    assert classified.evidence_confidence is EvidenceConfidence.WEAK
    assert classified.priority is Priority.P1_COMMERCIAL_REVIEW


def test_all_ten_frozen_classes_have_auditable_rule_definitions() -> None:
    assert set(RULE_DEFINITIONS) == set(GrowthQualityClass)
    assert all(rule.required_evidence for rule in RULE_DEFINITIONS.values())
    assert all(rule.owner_implications for rule in RULE_DEFINITIONS.values())
