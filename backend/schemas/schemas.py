from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class PromotionCaseInput(BaseModel):
    promotion_id: str
    brand: str
    category: str
    sku: str
    channel: str
    key_account: Optional[str] = None
    region: str
    promotion_period_start: str
    promotion_period_end: str
    campaign_objective: str
    promotion_type: str
    baseline_sales_volume: float
    promotion_sales_volume: float
    uplift_percent: float
    key_account_contribution_percent: float
    channel_contribution_percent: float
    num_participating_customers: int
    sell_in_volume: float
    sell_out_volume: float
    post_promotion_demand: float
    repeat_order_behavior: Dict[str, Any] = Field(default_factory=dict)
    inventory_impact: Dict[str, Any] = Field(default_factory=dict)
    replenishment_issues: Optional[str] = None
    forecast_variance: float
    discount_percent: float
    trade_spend: float
    gross_margin_before: float
    gross_margin_during: float
    management_notes: Optional[str] = None
    data_quality_confidence: float = Field(ge=0, le=100)


class Agent1Output(BaseModel):
    campaign_intent: str
    evaluation_lens: str
    risk_tolerance: str
    commercial_context_flags: List[str]
    intent_clarity: str
    confidence: float
    handoff_note: str


class Agent2Output(BaseModel):
    growth_distribution: Dict[str, Any]
    main_concentration_source: str
    concentration_risk_level: str  # low, medium, high, critical
    key_account_dependency: Dict[str, Any]
    channel_trade_risk: Dict[str, Any]
    sell_in_vs_sell_out_visibility: str
    trade_loading_risk: str
    sustainability_judgment: str
    confidence: float
    handoff_note: str


class Agent3Output(BaseModel):
    margin_impact: Dict[str, Any]
    trade_spend_efficiency: float
    financial_risk_level: str  # low, medium, high, critical
    discount_dependency_risk: str
    financial_sustainability_judgment: str
    confidence: float
    handoff_note: str


class Agent4Output(BaseModel):
    demand_movement: Dict[str, Any]
    inventory_impact: Dict[str, Any]
    propagation_risk_level: str  # low, medium, high, critical
    post_promotion_behavior: str
    root_cause_confidence: str
    confidence: float
    handoff_note: str


class Agent5Output(BaseModel):
    overall_case_severity: str  # low, medium, high, critical
    urgency: str  # routine, elevated, urgent, critical
    recommended_escalation_level: str
    primary_owner: str
    supporting_owners: List[str]
    recommended_governance_action: str
    reassessment_timing: str
    executive_attention_filter: str
    governance_risk_flags: List[str]
    handoff_to_final_brain: str


class Agent6Output(BaseModel):
    growth_health: str  # healthy, fragile, distortionary, misleading
    distortion_severity: str  # none, low, moderate, high, critical
    strategic_sustainability: str  # sustainable, at_risk, unsustainable
    recommended_action: str
    confidence: float
    executive_interpretation: str
    strongest_judgment_drivers: List[str]
    what_leadership_should_not_assume: List[str]
    required_next_action: str
    owner: str
    timing: str
    executive_risk_flags: List[str]


class FinalJudgment(BaseModel):
    growth_health: str
    distortion_severity: str
    strategic_sustainability: str
    recommended_action: str
    confidence: float
    executive_interpretation: str
    why_this_is_right: str
    what_not_to_assume: List[str]
    next_actions: List[str]
    owner: str
    timing: str
    all_agent_outputs: Dict[str, Any]
    governance_flags: List[str]


class PromotionCaseResponse(BaseModel):
    id: str
    promotion_id: str
    brand: str
    category: str
    status: str
    created_at: datetime
    updated_at: datetime
    finalized_at: Optional[datetime]
    growth_health: Optional[str] = None
    distortion_severity: Optional[str] = None
    recommended_action: Optional[str] = None
    confidence: Optional[float] = None
    human_review_approved: bool = False


class CaseListResponse(BaseModel):
    cases: List[PromotionCaseResponse]
    total: int


class HumanReviewInput(BaseModel):
    human_notes: Optional[str] = None
    override: bool = False


class ReanalysisRequest(BaseModel):
    reason: Optional[str] = None
