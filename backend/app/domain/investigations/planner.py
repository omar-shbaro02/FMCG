from dataclasses import asdict, dataclass

from app.domain.classification import ClassificationResult, GrowthQualityClass

VAGUE_PHRASES = ("review performance", "inspect sales", "validate data", "check the promotion")


@dataclass(frozen=True)
class InvestigationItem:
    investigation_area: str
    question: str
    why_it_matters: str
    evidence_required: list[str]
    available_evidence: list[str]
    missing_evidence: list[str]
    recommended_human_owner: str
    decision_affected: str
    risk_if_leadership_acts_too_early: str
    urgency: str
    confidence: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class InvestigationPlanResult:
    summary: str
    items: list[InvestigationItem]
    recommended_owner: str
    decision_affected: str
    acting_too_early_risks: list[str]
    evidence_confidence: str


@dataclass(frozen=True)
class InvestigationTemplate:
    area: str
    question: str
    why: str
    evidence: tuple[str, ...]
    owner: str
    decision: str
    early_risk: str


TEMPLATES: dict[GrowthQualityClass, InvestigationTemplate] = {
    GrowthQualityClass.HEALTHY_GROWTH_CANDIDATE: InvestigationTemplate(
        "POST_PROMO_RETENTION",
        "Did actual post-promotion sell-out remain materially above the aligned baseline?",
        "Sustained consumer movement is required before growth can be validated as healthy.",
        ("actual post-promotion sell-out", "aligned baseline", "stock availability"),
        "SALES_OPERATIONS",
        "REWARD_AS_HEALTHY_GROWTH",
        "Leadership may reward a temporary or distorted signal as sustained growth.",
    ),
    GrowthQualityClass.TEMPORARY_UPLIFT: InvestigationTemplate(
        "POST_PROMO_RETENTION",
        "How many post-promotion weeks remained above the aligned pre-promotion baseline?",
        "The duration of retention distinguishes sustained movement from a temporary uplift.",
        ("weekly post-promotion sell-out", "aligned baseline", "promotion end date"),
        "SALES_OPERATIONS",
        "REPEAT_PROMOTION",
        "A repeat decision may treat short-lived uplift as incremental demand.",
    ),
    GrowthQualityClass.PULL_FORWARD_RISK: InvestigationTemplate(
        "PULL_FORWARD",
        "Did promotion-period uplift precede materially below-baseline sell-out?",
        "A timing shift can overstate incremental demand and weaken following periods.",
        ("promotion uplift timing", "post-promotion actuals", "forecast trajectory", "baseline"),
        "DEMAND_PLANNING",
        "REPEAT_PROMOTION",
        "Repeating early may accelerate demand again without creating incremental consumption.",
    ),
    GrowthQualityClass.LOADING_RISK: InvestigationTemplate(
        "SELL_IN_SELL_OUT_MISMATCH",
        "Did sell-in grow materially more than consumer sell-out for the same grain and weeks?",
        "Shipment growth must be distinguished from consumer movement.",
        ("sell-in growth", "sell-out growth", "divergence ratio", "distributor stock"),
        "SALES_OPERATIONS",
        "SCALE_PROMOTION_BUDGET",
        "Scaling may add channel inventory while consumer movement remains unconfirmed.",
    ),
    GrowthQualityClass.CHANNEL_STOCK_PRESSURE: InvestigationTemplate(
        "CHANNEL_STOCK_PRESSURE",
        "Did account or distributor stock rise while sell-out failed to follow sell-in?",
        "Stock accumulation can convert apparent growth into future returns or weak orders.",
        ("stock on hand", "sell-in", "sell-out", "returns", "account concentration"),
        "SUPPLY_CHAIN",
        "REPEAT_PROMOTION",
        "Acting before stock verification may compound inventory pressure.",
    ),
    GrowthQualityClass.CANNIBALIZATION_RISK: InvestigationTemplate(
        "CANNIBALIZATION",
        "Did the promoted SKU grow while an identified adjacent SKU, pack, or segment declined?",
        "Portfolio movement is needed to distinguish incremental growth from substitution.",
        ("adjacent-series movement", "category total", "portfolio mix", "promotion overlap"),
        "CATEGORY_MANAGEMENT",
        "REWARD_AS_HEALTHY_GROWTH",
        "Leadership may reward mix transfer that did not improve total portfolio demand.",
    ),
    GrowthQualityClass.DISCOUNT_DEPENDENCY_RISK: InvestigationTemplate(
        "DISCOUNT_DEPENDENCY",
        "Did movement improve only during high-discount weeks and weaken after support ended?",
        "Repeated discount dependence may conceal weak underlying demand and value quality.",
        ("discount depth", "weekly uplift", "post-promotion decay", "promotion history"),
        "REVENUE_GROWTH_MANAGEMENT",
        "SCALE_PROMOTION_BUDGET",
        "Scaling support may deepen dependency without sustaining baseline movement.",
    ),
    GrowthQualityClass.MARGIN_VALUE_QUALITY_RISK: InvestigationTemplate(
        "MARGIN_VALUE_QUALITY",
        "Did unit net value or gross margin compress while promoted sell-out units increased?",
        "Volume alone cannot establish commercially valuable growth.",
        ("sell-out units", "net sales", "gross sales", "gross margin", "discount depth"),
        "FINANCE",
        "SCALE_PROMOTION_BUDGET",
        "Leadership may scale volume that dilutes value or margin.",
    ),
    GrowthQualityClass.INVESTIGATION_RECOMMENDED: InvestigationTemplate(
        "EVIDENCE_CONFIDENCE",
        "Which exact missing or conflicting evidence prevents a supported growth-quality class?",
        "The decision should remain open until the material evidence gap is resolved.",
        ("completeness report", "history length", "uncertainty", "contradictory evidence"),
        "COMMERCIAL_DIRECTOR",
        "INVESTIGATE_FIRST",
        "A commercial commitment may be based on an unsupported interpretation.",
    ),
    GrowthQualityClass.P1_COMMERCIAL_REVIEW: InvestigationTemplate(
        "CONVERGING_COMMERCIAL_RISK",
        "Which functions can validate each converging risk before leadership commits?",
        "Multiple material signals require coordinated evidence ownership.",
        ("risk-specific evidence", "business impact", "critical evidence gaps"),
        "COMMERCIAL_DIRECTOR",
        "ESCALATE_P1_COMMERCIAL_REVIEW",
        "A high-impact decision may proceed before cross-functional risks are reconciled.",
    ),
}


def build_investigation_plan(
    classification: ClassificationResult, available_evidence: set[str]
) -> InvestigationPlanResult:
    classes = ([classification.primary_class] if classification.primary_class else []) + list(
        classification.secondary_classes
    )
    unique_classes = list(dict.fromkeys(item for item in classes if item is not None))
    if not unique_classes:
        unique_classes = [GrowthQualityClass.INVESTIGATION_RECOMMENDED]
    items: list[InvestigationItem] = []
    for risk_class in unique_classes:
        template = TEMPLATES[risk_class]
        available = [item for item in template.evidence if item in available_evidence]
        missing = [item for item in template.evidence if item not in available_evidence]
        item = InvestigationItem(
            investigation_area=template.area,
            question=template.question,
            why_it_matters=template.why,
            evidence_required=list(template.evidence),
            available_evidence=available,
            missing_evidence=missing,
            recommended_human_owner=template.owner,
            decision_affected=template.decision,
            risk_if_leadership_acts_too_early=template.early_risk,
            urgency="TODAY"
            if classification.priority.value == "P1_COMMERCIAL_REVIEW"
            else "THIS_WEEK",
            confidence=classification.evidence_confidence.value,
        )
        text = " ".join(str(value) for value in item.to_dict().values()).casefold()
        if any(phrase in text for phrase in VAGUE_PHRASES):
            raise ValueError("Investigation item contains prohibited vague language")
        items.append(item)
    return InvestigationPlanResult(
        summary=f"{len(items)} exact commercial verification item(s) require human ownership.",
        items=items,
        recommended_owner=items[0].recommended_human_owner,
        decision_affected=items[0].decision_affected,
        acting_too_early_risks=[item.risk_if_leadership_acts_too_early for item in items],
        evidence_confidence=classification.evidence_confidence.value,
    )
