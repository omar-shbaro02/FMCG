from abc import ABC, abstractmethod
from typing import Any

from app.adapters.llm.schemas import LLMInterpretationOutput

FORBIDDEN_ACTION_LANGUAGE = (
    "increase budget",
    "repeat the promotion",
    "change price",
    "replenish stock",
    "final decision",
    "automatically",
)


class LLMGatewayError(ValueError):
    pass


class LLMGateway(ABC):
    @abstractmethod
    def interpret_growth_quality(
        self, facts: dict[str, Any], allowed_evidence_keys: set[str]
    ) -> LLMInterpretationOutput: ...

    @abstractmethod
    def generate_investigation_plan(self, facts: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    def simulate_decision_options(self, facts: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    def generate_executive_output(self, facts: dict[str, Any]) -> dict[str, Any]: ...


class ControlledLLMInterpreter:
    """Validate gateway output and retry only within a small explicit bound."""

    def __init__(self, gateway: LLMGateway, max_attempts: int = 2) -> None:
        if max_attempts not in range(1, 4):
            raise ValueError("max_attempts must be between 1 and 3")
        self.gateway = gateway
        self.max_attempts = max_attempts

    def interpret(
        self, facts: dict[str, Any], allowed_evidence_keys: set[str]
    ) -> LLMInterpretationOutput:
        last_error: Exception | None = None
        for _ in range(self.max_attempts):
            try:
                raw = self.gateway.interpret_growth_quality(facts, allowed_evidence_keys)
                return validate_interpretation_output(raw, allowed_evidence_keys)
            except (LLMGatewayError, ValueError) as exc:
                last_error = exc
        raise LLMGatewayError(
            f"Interpretation failed validation after {self.max_attempts} attempts"
        ) from last_error


def validate_interpretation_output(
    raw: Any, allowed_evidence_keys: set[str]
) -> LLMInterpretationOutput:
    output = LLMInterpretationOutput.model_validate(raw)
    cited = {key for statement in output.interpretations for key in statement.evidence_keys}
    unsupported = cited - allowed_evidence_keys
    if unsupported:
        raise LLMGatewayError(f"Unsupported evidence references: {sorted(unsupported)}")
    text = " ".join(
        [output.summary, *(item.statement for item in output.interpretations)]
    ).casefold()
    if any(phrase in text for phrase in FORBIDDEN_ACTION_LANGUAGE):
        raise LLMGatewayError("LLM output contains forbidden action or certainty language")
    return output
