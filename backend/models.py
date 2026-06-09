from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Text, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class CaseStatus(str, enum.Enum):
    DRAFT = "Draft"
    ANALYZING = "Analyzing"
    NEEDS_REVIEW = "Needs Review"
    FINALIZED = "Finalized"


class PromotionCase(Base):
    __tablename__ = "promotion_cases"
    
    id = Column(String, primary_key=True)
    promotion_id = Column(String, unique=True)
    brand = Column(String)
    category = Column(String)
    sku = Column(String)
    channel = Column(String)
    key_account = Column(String, nullable=True)
    region = Column(String)
    promotion_period_start = Column(String)
    promotion_period_end = Column(String)
    campaign_objective = Column(String)
    promotion_type = Column(String)
    
    # Sales data
    baseline_sales_volume = Column(Float)
    promotion_sales_volume = Column(Float)
    uplift_percent = Column(Float)
    key_account_contribution_percent = Column(Float)
    channel_contribution_percent = Column(Float)
    num_participating_customers = Column(Integer)
    sell_in_volume = Column(Float)
    sell_out_volume = Column(Float)
    post_promotion_demand = Column(Float)
    
    # Behavior & inventory
    repeat_order_behavior = Column(String)  # JSON serialized
    inventory_impact = Column(String)  # JSON serialized
    replenishment_issues = Column(String, nullable=True)
    forecast_variance = Column(Float)
    
    # Financial
    discount_percent = Column(Float)
    trade_spend = Column(Float)
    gross_margin_before = Column(Float)
    gross_margin_during = Column(Float)
    
    # Metadata
    management_notes = Column(Text, nullable=True)
    data_quality_confidence = Column(Float)  # 0-100
    status = Column(Enum(CaseStatus), default=CaseStatus.DRAFT)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    finalized_at = Column(DateTime, nullable=True)
    
    # Agent outputs (stored as JSON for flexibility)
    agent_1_output = Column(JSON, nullable=True)
    agent_2_output = Column(JSON, nullable=True)
    agent_3_output = Column(JSON, nullable=True)
    agent_4_output = Column(JSON, nullable=True)
    agent_5_output = Column(JSON, nullable=True)
    agent_6_output = Column(JSON, nullable=True)
    
    # Final judgment
    final_judgment = Column(JSON, nullable=True)
    human_review_approved = Column(Boolean, default=False)
    human_review_notes = Column(Text, nullable=True)
    human_review_at = Column(DateTime, nullable=True)


class AgentAudit(Base):
    __tablename__ = "agent_audits"
    
    id = Column(String, primary_key=True)
    case_id = Column(String)
    agent_number = Column(Integer)
    agent_name = Column(String)
    raw_input = Column(JSON)
    raw_output = Column(Text)
    parsed_output = Column(JSON)
    confidence = Column(Float)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
