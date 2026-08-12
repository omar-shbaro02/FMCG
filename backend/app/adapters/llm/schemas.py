from pydantic import BaseModel, ConfigDict, Field


class InterpretationStatement(BaseModel):
    model_config = ConfigDict(extra="forbid")
    statement: str = Field(min_length=1, max_length=1000)
    evidence_keys: list[str] = Field(min_length=1)


class LLMInterpretationOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str = Field(min_length=1, max_length=2000)
    interpretations: list[InterpretationStatement]
    ambiguity: list[str]
    missing_evidence: list[str]
    refusal_reason: str | None = None
