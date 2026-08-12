from dataclasses import dataclass
from enum import StrEnum

from app.domain.interpretation import InterpretationResult

CLASSIFIER_RULE_VERSION = "fmcg-growth-quality-rules/1.0.0"


class GrowthQualityClass(StrEnum):
    HEALTHY_GROWTH_CANDIDATE = "HEALTHY_GROWTH_CANDIDATE"
    TEMPORARY_UPLIFT = "TEMPORARY_UPLIFT"
    PULL_FORWARD_RISK = "PULL_FORWARD_RISK"
    LOADING_RISK = "LOADING_RISK"
    CHANNEL_STOCK_PRESSURE = "CHANNEL_STOCK_PRESSURE"
    CANNIBALIZATION_RISK = "CANNIBALIZATION_RISK"
    DISCOUNT_DEPENDENCY_RISK = "DISCOUNT_DEPENDENCY_RISK"
    MARGIN_VALUE_QUALITY_RISK = "MARGIN_VALUE_QUALITY_RISK"
    INVESTIGATION_RECOMMENDED = "INVESTIGATION_RECOMMENDED"
    P1_COMMERCIAL_REVIEW = "P1_COMMERCIAL_REVIEW"


class Priority(StrEnum):
    HEALTHY_CANDIDATE = "HEALTHY_CANDIDATE"
    MONITOR = "MONITOR"
    INVESTIGATION_RECOMMENDED = "INVESTIGATION_RECOMMENDED"
    P1_COMMERCIAL_REVIEW = "P1_COMMERCIAL_REVIEW"


class EvidenceConfidence(StrEnum):
    STRONG = "STRONG"
    MEDIUM = "MEDIUM"
    WEAK = "WEAK"
    INSUFFICIENT = "INSUFFICIENT"


@dataclass(frozen=True)
class RuleDefinition:
    definition: str
    required_evidence: tuple[str, ...]
    supporting_evidence: tuple[str, ...]
    contradicting_evidence: tuple[str, ...]
    confidence_conditions: str
    exclusion_conditions: tuple[str, ...]
    priority_impact: Priority
    owner_implications: tuple[str, ...]


RULE_DEFINITIONS: dict[GrowthQualityClass, RuleDefinition] = {
    GrowthQualityClass.HEALTHY_GROWTH_CANDIDATE: RuleDefinition(
        "Sustained post-promotion baseline retention, pending human validation.",
        ("baseline_comparison", "retention_status", "decay_signal"),
        ("above baseline", "sustained retention"),
        ("loading", "stock", "discount", "cannibalization", "margin risk"),
        "At least medium confidence and no unresolved material risk.",
        ("insufficient evidence", "any material risk"),
        Priority.HEALTHY_CANDIDATE,
        ("Commercial Director",),
    ),
    GrowthQualityClass.TEMPORARY_UPLIFT: RuleDefinition(
        "Promotion uplift returns quickly to expected baseline.",
        ("retention_status", "baseline_comparison"),
        ("weak retention", "at or below baseline"),
        ("sustained post-promotion improvement",),
        "At least weak aligned evidence.",
        ("insufficient aligned baseline",),
        Priority.INVESTIGATION_RECOMMENDED,
        ("Sales", "Revenue Growth Management"),
    ),
    GrowthQualityClass.PULL_FORWARD_RISK: RuleDefinition(
        "Promotion may have accelerated future purchases into the current period.",
        ("baseline_comparison", "decay_signal"),
        ("below baseline", "moderate or strong decay"),
        ("sustained retention",),
        "At least weak aligned pre/post evidence.",
        ("insufficient post-promotion horizon",),
        Priority.INVESTIGATION_RECOMMENDED,
        ("Demand Planning", "Sales"),
    ),
    GrowthQualityClass.LOADING_RISK: RuleDefinition(
        "Sell-in growth is not confirmed by consumer movement.",
        ("sell_in_sell_out_divergence",),
        ("material sell-in excess",),
        ("sell-out follows sell-in",),
        "At least weak aligned sell-in and sell-out evidence.",
        ("missing sell-in or sell-out",),
        Priority.P1_COMMERCIAL_REVIEW,
        ("Sales", "Supply Chain"),
    ),
    GrowthQualityClass.CHANNEL_STOCK_PRESSURE: RuleDefinition(
        "Volume may be accumulating in the channel rather than reaching consumers.",
        ("sell_in_sell_out_divergence", "stock evidence"),
        ("sell-in excess", "stock accumulation", "returns increase"),
        ("stable stock", "sell-out follows"),
        "At least weak divergence plus validated stock evidence.",
        ("stock evidence unavailable",),
        Priority.P1_COMMERCIAL_REVIEW,
        ("Supply Chain", "Sales"),
    ),
    GrowthQualityClass.CANNIBALIZATION_RISK: RuleDefinition(
        "Promoted SKU growth coincides with adjacent portfolio decline.",
        ("identified adjacent series", "adjacent_series_decline"),
        ("material adjacent decline",),
        ("adjacent series stable or growing",),
        "At least weak aligned adjacent-series evidence.",
        ("adjacent series unavailable",),
        Priority.INVESTIGATION_RECOMMENDED,
        ("Category Management", "Revenue Growth Management"),
    ),
    GrowthQualityClass.DISCOUNT_DEPENDENCY_RISK: RuleDefinition(
        "Movement appears dependent on discount rather than sustained demand.",
        ("discount_dependency_signal", "retention_status"),
        ("high-discount response", "weak retention"),
        ("movement without discount", "sustained retention"),
        "At least weak repeated discount and movement evidence.",
        ("discount history unavailable",),
        Priority.INVESTIGATION_RECOMMENDED,
        ("Revenue Growth Management", "Finance"),
    ),
    GrowthQualityClass.MARGIN_VALUE_QUALITY_RISK: RuleDefinition(
        "Volume grows while unit value or gross margin materially compresses.",
        ("margin_value_compression", "unit_margin_change_ratio"),
        ("positive volume", "material value or margin compression"),
        ("stable unit value and margin",),
        "At least weak validated value and margin evidence.",
        ("margin or net-value evidence unavailable",),
        Priority.P1_COMMERCIAL_REVIEW,
        ("Finance", "Revenue Growth Management"),
    ),
    GrowthQualityClass.INVESTIGATION_RECOMMENDED: RuleDefinition(
        "A signal requires structured commercial verification before action.",
        ("material risk or conflicting/weak evidence",),
        ("one credible risk", "medium or weak confidence"),
        ("strong, complete, non-conflicting evidence",),
        "Any confidence, including insufficient.",
        (),
        Priority.INVESTIGATION_RECOMMENDED,
        ("Commercial Director", "relevant evidence owner"),
    ),
    GrowthQualityClass.P1_COMMERCIAL_REVIEW: RuleDefinition(
        "Converging risks or high-impact uncertainty require urgent human review.",
        ("converging material risks or high-impact critical gap",),
        ("loading plus stock", "pull-forward plus discount", "margin deterioration"),
        ("single low-impact signal",),
        "Urgency is independent from evidence confidence.",
        (),
        Priority.P1_COMMERCIAL_REVIEW,
        ("Commercial Director", "Finance", "Sales", "Supply Chain"),
    ),
}


@dataclass(frozen=True)
class ClassificationInput:
    interpretation: InterpretationResult
    business_impact: str = "MEDIUM"
    critical_evidence_incomplete: bool = False


@dataclass(frozen=True)
class ClassificationResult:
    primary_class: GrowthQualityClass | None
    secondary_classes: list[GrowthQualityClass]
    priority: Priority
    evidence_confidence: EvidenceConfidence
    supporting_evidence: dict[str, list[str]]
    contradicting_evidence: dict[str, list[str]]
    exclusion_reasons: list[str]
    rule_version: str = CLASSIFIER_RULE_VERSION


RISK_ORDER = (
    GrowthQualityClass.MARGIN_VALUE_QUALITY_RISK,
    GrowthQualityClass.LOADING_RISK,
    GrowthQualityClass.CHANNEL_STOCK_PRESSURE,
    GrowthQualityClass.PULL_FORWARD_RISK,
    GrowthQualityClass.CANNIBALIZATION_RISK,
    GrowthQualityClass.DISCOUNT_DEPENDENCY_RISK,
    GrowthQualityClass.TEMPORARY_UPLIFT,
    GrowthQualityClass.HEALTHY_GROWTH_CANDIDATE,
)


def classify(inputs: ClassificationInput) -> ClassificationResult:
    interpretation = inputs.interpretation
    confidence = EvidenceConfidence(interpretation.evidence_confidence)
    support = interpretation.supporting_evidence
    candidates = {
        GrowthQualityClass(value)
        for value in interpretation.candidate_risks
        if value in GrowthQualityClass._value2member_map_
    }
    exclusions: list[str] = []
    if confidence is EvidenceConfidence.INSUFFICIENT:
        return ClassificationResult(
            primary_class=None,
            secondary_classes=[],
            priority=Priority.INVESTIGATION_RECOMMENDED,
            evidence_confidence=confidence,
            supporting_evidence={},
            contradicting_evidence={},
            exclusion_reasons=[
                "Risk classification excluded because aligned evidence is insufficient."
            ],
        )

    material_risks = candidates - {GrowthQualityClass.HEALTHY_GROWTH_CANDIDATE}
    if material_risks and GrowthQualityClass.HEALTHY_GROWTH_CANDIDATE in candidates:
        candidates.remove(GrowthQualityClass.HEALTHY_GROWTH_CANDIDATE)
        exclusions.append("Healthy candidate excluded while a material risk remains unresolved.")

    ordered = [item for item in RISK_ORDER if item in candidates]
    primary = ordered[0] if ordered else GrowthQualityClass.INVESTIGATION_RECOMMENDED
    secondary = ordered[1:]
    converging_p1 = (
        {GrowthQualityClass.LOADING_RISK, GrowthQualityClass.CHANNEL_STOCK_PRESSURE} <= candidates
        or GrowthQualityClass.MARGIN_VALUE_QUALITY_RISK in candidates
        or (
            GrowthQualityClass.PULL_FORWARD_RISK in candidates
            and GrowthQualityClass.DISCOUNT_DEPENDENCY_RISK in candidates
        )
    )
    if converging_p1 or (inputs.business_impact == "HIGH" and inputs.critical_evidence_incomplete):
        priority = Priority.P1_COMMERCIAL_REVIEW
        secondary.append(GrowthQualityClass.P1_COMMERCIAL_REVIEW)
    elif primary is GrowthQualityClass.HEALTHY_GROWTH_CANDIDATE:
        priority = Priority.HEALTHY_CANDIDATE
    elif material_risks or confidence in {EvidenceConfidence.MEDIUM, EvidenceConfidence.WEAK}:
        priority = Priority.INVESTIGATION_RECOMMENDED
        if GrowthQualityClass.INVESTIGATION_RECOMMENDED not in secondary:
            secondary.append(GrowthQualityClass.INVESTIGATION_RECOMMENDED)
    else:
        priority = Priority.MONITOR

    return ClassificationResult(
        primary_class=primary,
        secondary_classes=secondary,
        priority=priority,
        evidence_confidence=confidence,
        supporting_evidence={item.value: support.get(item.value, []) for item in ordered},
        contradicting_evidence=interpretation.contradicting_evidence,
        exclusion_reasons=exclusions,
    )
