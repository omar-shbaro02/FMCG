from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InterpretationInput:
    evidence: dict[str, Any]
    data_quality_notes: list[str]
    adjacent_series_available: bool = False
    margin_evidence_available: bool = True
    stock_evidence_available: bool = True


@dataclass(frozen=True)
class InterpretationResult:
    growth_signal_summary: str
    facts: list[dict[str, Any]]
    interpretation_statements: list[dict[str, Any]]
    candidate_risks: list[str]
    supporting_evidence: dict[str, list[str]]
    contradicting_evidence: dict[str, list[str]]
    missing_evidence: list[str]
    uncertainty_notes: list[str]
    evidence_confidence: str


def interpret(inputs: InterpretationInput) -> InterpretationResult:
    evidence = inputs.evidence
    facts = [
        {"key": key, "value": value} for key, value in sorted(evidence.items()) if value is not None
    ]
    candidates: list[str] = []
    supporting: dict[str, list[str]] = {}
    contradicting: dict[str, list[str]] = {}
    statements: list[dict[str, Any]] = []

    def candidate(name: str, statement: str, keys: list[str]) -> None:
        candidates.append(name)
        supporting[name] = keys
        statements.append({"statement": statement, "evidence_keys": keys})

    comparison = evidence.get("baseline_comparison")
    retention = evidence.get("retention_status")
    decay = evidence.get("decay_signal")
    direction = evidence.get("forecast_direction")
    divergence = evidence.get("sell_in_sell_out_divergence")
    if comparison == "ABOVE_BASELINE" and retention == "SUSTAINED" and decay in {"NONE", "MILD"}:
        candidate(
            "HEALTHY_GROWTH_CANDIDATE",
            "Forecast evidence remains above baseline with sustained retention; "
            "this is a candidate pending risk checks and human validation.",
            ["baseline_comparison", "retention_status", "decay_signal"],
        )
    if retention in {"PARTIAL", "WEAK"} and comparison in {"AT_BASELINE", "BELOW_BASELINE"}:
        candidate(
            "TEMPORARY_UPLIFT",
            "Post-promotion movement appears to return toward or below expected baseline.",
            ["retention_status", "baseline_comparison"],
        )
    if comparison == "BELOW_BASELINE" and decay in {"MODERATE", "STRONG"}:
        candidate(
            "PULL_FORWARD_RISK",
            "Below-baseline movement and forecast decay keep pull-forward risk plausible.",
            ["baseline_comparison", "decay_signal", "forecast_direction"],
        )
    if divergence == "MATERIAL_SELL_IN_EXCESS":
        candidate(
            "LOADING_RISK",
            "Sell-in materially exceeds sell-out, so shipment growth is not "
            "confirmed by consumer movement.",
            ["sell_in_sell_out_divergence", "sell_in_to_sell_out_ratio"],
        )
        if inputs.stock_evidence_available:
            candidate(
                "CHANNEL_STOCK_PRESSURE",
                "Sell-in divergence makes channel stock pressure plausible and "
                "requires stock verification.",
                ["sell_in_sell_out_divergence"],
            )
    if evidence.get("discount_dependency_signal") is True:
        candidate(
            "DISCOUNT_DEPENDENCY_RISK",
            "Movement is materially associated with high discount periods and retention is weak.",
            ["discount_dependency_signal", "retention_status"],
        )
    if inputs.adjacent_series_available and evidence.get("adjacent_series_decline") is True:
        candidate(
            "CANNIBALIZATION_RISK",
            "Promoted movement coincides with a material decline in an identified adjacent series.",
            ["adjacent_series_decline", "adjacent_series_change_ratio"],
        )
    if inputs.margin_evidence_available and evidence.get("margin_value_compression") is True:
        candidate(
            "MARGIN_VALUE_QUALITY_RISK",
            "Volume movement coincides with material unit-value or gross-margin compression.",
            ["margin_value_compression", "unit_margin_change_ratio"],
        )
    missing: list[str] = []
    if not inputs.adjacent_series_available:
        missing.append("adjacent SKU/pack/flavor series for cannibalization assessment")
    if not inputs.margin_evidence_available:
        missing.append("validated net value and gross margin evidence")
    if not inputs.stock_evidence_available:
        missing.append("validated account/distributor stock evidence")
    insufficient = (
        comparison == "INSUFFICIENT" or evidence.get("uncertainty_level") == "INSUFFICIENT"
    )
    if insufficient:
        candidates = []
        supporting = {}
        statements = []
        missing.append("aligned forecast and baseline evidence")
    uncertainty = list(inputs.data_quality_notes)
    if evidence.get("uncertainty_level") in {"HIGH", "INSUFFICIENT"}:
        uncertainty.append("Forecast uncertainty limits confident commercial interpretation.")
    confidence = (
        "INSUFFICIENT"
        if insufficient
        else ("WEAK" if evidence.get("uncertainty_level") == "HIGH" else "MEDIUM")
    )
    summary = (
        f"Forecast movement is {str(direction).lower().replace('_', ' ')} and "
        f"{str(comparison).lower().replace('_', ' ')}."
        if not insufficient
        else "Evidence is insufficient for a growth-quality candidate judgment."
    )
    return InterpretationResult(
        summary,
        facts,
        statements,
        candidates,
        supporting,
        contradicting,
        sorted(set(missing)),
        sorted(set(uncertainty)),
        confidence,
    )
