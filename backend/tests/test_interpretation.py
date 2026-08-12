from typing import Any

import pytest

from app.adapters.llm import (
    ControlledLLMInterpreter,
    LLMGateway,
    LLMGatewayError,
    validate_interpretation_output,
)
from app.adapters.llm.schemas import LLMInterpretationOutput
from app.domain.interpretation import InterpretationInput, interpret


def evidence(**changes: object) -> dict[str, object]:
    values: dict[str, object] = {
        "forecast_direction": "DECLINING",
        "baseline_comparison": "BELOW_BASELINE",
        "retention_status": "WEAK",
        "decay_signal": "STRONG",
        "uncertainty_level": "MEDIUM",
        "sell_in_sell_out_divergence": "MATERIAL_SELL_IN_EXCESS",
        "sell_in_to_sell_out_ratio": 1.5,
    }
    values.update(changes)
    return values


def test_interpretation_separates_facts_candidates_and_missing_evidence() -> None:
    result = interpret(InterpretationInput(evidence(), ["stock week missing"]))
    assert "PULL_FORWARD_RISK" in result.candidate_risks
    assert "LOADING_RISK" in result.candidate_risks
    assert result.facts
    assert result.missing_evidence
    assert result.evidence_confidence == "MEDIUM"


def test_insufficient_evidence_refuses_candidate_classification() -> None:
    result = interpret(
        InterpretationInput(
            evidence(baseline_comparison="INSUFFICIENT", uncertainty_level="INSUFFICIENT"), []
        )
    )
    assert result.candidate_risks == []
    assert result.evidence_confidence == "INSUFFICIENT"


def test_llm_output_requires_real_evidence_references_and_no_action_language() -> None:
    valid = {
        "summary": "The signal remains ambiguous.",
        "interpretations": [
            {"statement": "Movement is below baseline.", "evidence_keys": ["baseline_comparison"]}
        ],
        "ambiguity": [],
        "missing_evidence": [],
    }
    assert validate_interpretation_output(valid, {"baseline_comparison"}).interpretations
    invalid_reference = {
        **valid,
        "interpretations": [{"statement": "x", "evidence_keys": ["invented"]}],
    }
    with pytest.raises(LLMGatewayError):
        validate_interpretation_output(invalid_reference, {"baseline_comparison"})
    forbidden = {**valid, "summary": "Automatically repeat the promotion."}
    with pytest.raises(LLMGatewayError):
        validate_interpretation_output(forbidden, {"baseline_comparison"})


class RetryingGateway(LLMGateway):
    def __init__(self) -> None:
        self.calls = 0

    def interpret_growth_quality(
        self, facts: dict[str, Any], allowed_evidence_keys: set[str]
    ) -> LLMInterpretationOutput:
        self.calls += 1
        key = "invented" if self.calls == 1 else next(iter(allowed_evidence_keys))
        return LLMInterpretationOutput.model_validate(
            {
                "summary": "The evidence remains conditional.",
                "interpretations": [
                    {"statement": "A candidate signal exists.", "evidence_keys": [key]}
                ],
                "ambiguity": [],
                "missing_evidence": [],
            }
        )

    def generate_investigation_plan(self, facts: dict[str, Any]) -> dict[str, Any]:
        return {}

    def simulate_decision_options(self, facts: dict[str, Any]) -> dict[str, Any]:
        return {}

    def generate_executive_output(self, facts: dict[str, Any]) -> dict[str, Any]:
        return {}


def test_controlled_llm_boundary_retries_invalid_output_within_bound() -> None:
    gateway = RetryingGateway()
    result = ControlledLLMInterpreter(gateway, max_attempts=2).interpret(
        {"baseline_comparison": "BELOW_BASELINE"}, {"baseline_comparison"}
    )
    assert result.interpretations[0].evidence_keys == ["baseline_comparison"]
    assert gateway.calls == 2
