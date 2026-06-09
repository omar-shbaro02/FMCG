"""
Main FastAPI Application for FMCG Trade Promotion Distortion Intelligence
"""

import os
import uuid
from datetime import datetime
from typing import List
from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import json

from models import Base, PromotionCase, CaseStatus, AgentAudit
from schemas.schemas import (
    PromotionCaseInput, PromotionCaseResponse, CaseListResponse, FinalJudgment,
    HumanReviewInput, ReanalysisRequest
)
from orchestrator.orchestrator import AgentOrchestrator

load_dotenv()

# Setup database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./fmcg_cases.db')
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="FMCG Trade Promotion Distortion Intelligence",
    description="Multi-agent decision intelligence for promotional health analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv('FRONTEND_URL', 'http://localhost:5173')],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = AgentOrchestrator()


# Helper to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/cases")
async def create_case(case_input: PromotionCaseInput, db: Session = Depends(get_db)):
    """Create a new promotion case."""
    try:
        case_id = str(uuid.uuid4())
        
        # Create case record
        db_case = PromotionCase(
            id=case_id,
            promotion_id=case_input.promotion_id,
            brand=case_input.brand,
            category=case_input.category,
            sku=case_input.sku,
            channel=case_input.channel,
            key_account=case_input.key_account,
            region=case_input.region,
            promotion_period_start=case_input.promotion_period_start,
            promotion_period_end=case_input.promotion_period_end,
            campaign_objective=case_input.campaign_objective,
            promotion_type=case_input.promotion_type,
            baseline_sales_volume=case_input.baseline_sales_volume,
            promotion_sales_volume=case_input.promotion_sales_volume,
            uplift_percent=case_input.uplift_percent,
            key_account_contribution_percent=case_input.key_account_contribution_percent,
            channel_contribution_percent=case_input.channel_contribution_percent,
            num_participating_customers=case_input.num_participating_customers,
            sell_in_volume=case_input.sell_in_volume,
            sell_out_volume=case_input.sell_out_volume,
            post_promotion_demand=case_input.post_promotion_demand,
            repeat_order_behavior=json.dumps(case_input.repeat_order_behavior),
            inventory_impact=json.dumps(case_input.inventory_impact),
            replenishment_issues=case_input.replenishment_issues,
            forecast_variance=case_input.forecast_variance,
            discount_percent=case_input.discount_percent,
            trade_spend=case_input.trade_spend,
            gross_margin_before=case_input.gross_margin_before,
            gross_margin_during=case_input.gross_margin_during,
            management_notes=case_input.management_notes,
            data_quality_confidence=case_input.data_quality_confidence,
            status=CaseStatus.DRAFT,
        )
        
        db.add(db_case)
        db.commit()
        db.refresh(db_case)
        
        response = PromotionCaseResponse(
            id=db_case.id,
            promotion_id=db_case.promotion_id,
            brand=db_case.brand,
            category=db_case.category,
            status=db_case.status.value,
            created_at=db_case.created_at,
            updated_at=db_case.updated_at,
            finalized_at=db_case.finalized_at,
        )
        
        return {"case": response, "message": "Case created successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/cases")
async def list_cases(db: Session = Depends(get_db)):
    """List all promotion cases."""
    cases = db.query(PromotionCase).order_by(PromotionCase.created_at.desc()).all()

    response_cases = []
    for case in cases:
        # Extract final judgment info if available
        growth_health = None
        distortion_severity = None
        recommended_action = None
        confidence = None

        if case.agent_6_output:
            try:
                agent_6 = json.loads(case.agent_6_output) if isinstance(case.agent_6_output, str) else case.agent_6_output
                growth_health = agent_6.get("growth_health")
                distortion_severity = agent_6.get("distortion_severity")
                recommended_action = agent_6.get("recommended_action")
                confidence = agent_6.get("confidence")
            except:
                pass

        response_cases.append(PromotionCaseResponse(
            id=case.id,
            promotion_id=case.promotion_id,
            brand=case.brand,
            category=case.category,
            status=case.status.value,
            created_at=case.created_at,
            updated_at=case.updated_at,
            finalized_at=case.finalized_at,
            growth_health=growth_health,
            distortion_severity=distortion_severity,
            recommended_action=recommended_action,
            confidence=confidence,
            human_review_approved=case.human_review_approved,
        ))

    return CaseListResponse(cases=response_cases, total=len(response_cases))


@app.get("/api/cases/{case_id}")
async def get_case(case_id: str, db: Session = Depends(get_db)):
    """Get a specific case with all agent outputs."""
    case = db.query(PromotionCase).filter(PromotionCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Parse agent outputs
    agent_outputs = {}
    for agent_num in range(1, 7):
        field_name = f"agent_{agent_num}_output"
        output_data = getattr(case, field_name)
        if output_data:
            try:
                agent_outputs[f"agent_{agent_num}"] = json.loads(output_data) if isinstance(output_data, str) else output_data
            except:
                pass

    return {
        "case": {
            "id": case.id,
            "promotion_id": case.promotion_id,
            "brand": case.brand,
            "category": case.category,
            "sku": case.sku,
            "channel": case.channel,
            "key_account": case.key_account,
            "region": case.region,
            "promotion_period_start": case.promotion_period_start,
            "promotion_period_end": case.promotion_period_end,
            "campaign_objective": case.campaign_objective,
            "promotion_type": case.promotion_type,
            "baseline_sales_volume": case.baseline_sales_volume,
            "promotion_sales_volume": case.promotion_sales_volume,
            "uplift_percent": case.uplift_percent,
            "key_account_contribution_percent": case.key_account_contribution_percent,
            "channel_contribution_percent": case.channel_contribution_percent,
            "num_participating_customers": case.num_participating_customers,
            "sell_in_volume": case.sell_in_volume,
            "sell_out_volume": case.sell_out_volume,
            "post_promotion_demand": case.post_promotion_demand,
            "repeat_order_behavior": json.loads(case.repeat_order_behavior) if case.repeat_order_behavior else {},
            "inventory_impact": json.loads(case.inventory_impact) if case.inventory_impact else {},
            "replenishment_issues": case.replenishment_issues,
            "forecast_variance": case.forecast_variance,
            "discount_percent": case.discount_percent,
            "trade_spend": case.trade_spend,
            "gross_margin_before": case.gross_margin_before,
            "gross_margin_during": case.gross_margin_during,
            "management_notes": case.management_notes,
            "data_quality_confidence": case.data_quality_confidence,
            "status": case.status.value,
            "created_at": case.created_at.isoformat(),
            "updated_at": case.updated_at.isoformat(),
            "finalized_at": case.finalized_at.isoformat() if case.finalized_at else None,
        },
        "agent_outputs": agent_outputs,
        "human_review_approved": case.human_review_approved,
        "human_review_notes": case.human_review_notes,
    }


@app.post("/api/cases/{case_id}/analyze")
async def analyze_case(case_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger agent analysis for a case."""
    try:
        case = db.query(PromotionCase).filter(PromotionCase.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Update status to analyzing
        case.status = CaseStatus.ANALYZING
        db.commit()
        
        # Run analysis in background
        background_tasks.add_task(run_analysis_workflow, case_id)
        
        return {"message": "Analysis started", "case_id": case_id, "status": "ANALYZING"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def run_analysis_workflow(case_id: str):
    """Run the full agent workflow for a case."""
    db = SessionLocal()
    try:
        case = db.query(PromotionCase).filter(PromotionCase.id == case_id).first()
        if not case:
            return
        
        # Prepare case data for orchestrator
        case_data = {
            "case_id": case.id,
            "promotion_id": case.promotion_id,
            "brand": case.brand,
            "category": case.category,
            "sku": case.sku,
            "channel": case.channel,
            "key_account": case.key_account,
            "region": case.region,
            "promotion_period_start": case.promotion_period_start,
            "promotion_period_end": case.promotion_period_end,
            "campaign_objective": case.campaign_objective,
            "promotion_type": case.promotion_type,
            "baseline_sales_volume": case.baseline_sales_volume,
            "promotion_sales_volume": case.promotion_sales_volume,
            "uplift_percent": case.uplift_percent,
            "key_account_contribution_percent": case.key_account_contribution_percent,
            "channel_contribution_percent": case.channel_contribution_percent,
            "num_participating_customers": case.num_participating_customers,
            "sell_in_volume": case.sell_in_volume,
            "sell_out_volume": case.sell_out_volume,
            "post_promotion_demand": case.post_promotion_demand,
            "repeat_order_behavior": json.loads(case.repeat_order_behavior) if case.repeat_order_behavior else {},
            "inventory_impact": json.loads(case.inventory_impact) if case.inventory_impact else {},
            "replenishment_issues": case.replenishment_issues,
            "forecast_variance": case.forecast_variance,
            "discount_percent": case.discount_percent,
            "trade_spend": case.trade_spend,
            "gross_margin_before": case.gross_margin_before,
            "gross_margin_during": case.gross_margin_during,
            "management_notes": case.management_notes,
            "data_quality_confidence": case.data_quality_confidence,
        }
        
        # Run orchestrator
        results = orchestrator.orchestrate(case_data)
        
        # Store agent outputs
        for agent_num in range(1, 7):
            agent_key = f"agent_{agent_num}"
            if agent_key in results["agents"]:
                field_name = f"agent_{agent_num}_output"
                setattr(case, field_name, results["agents"][agent_key])

        if results.get("final_output"):
            case.final_judgment = results["final_output"]

        for audit in results.get("audit_log", []):
            db.add(AgentAudit(
                id=audit.get("id", str(uuid.uuid4())),
                case_id=case.id,
                agent_number=audit.get("agent_number"),
                agent_name=audit.get("agent_name"),
                raw_input=audit.get("raw_input"),
                raw_output=audit.get("raw_output"),
                parsed_output=audit.get("parsed_output"),
                confidence=audit.get("confidence"),
                error_message=audit.get("error_message"),
            ))
        
        # Update case status to NEEDS_REVIEW
        case.status = CaseStatus.NEEDS_REVIEW
        case.updated_at = datetime.utcnow()
        
        db.commit()
        print(f"Analysis complete for case {case_id}")
        
    except Exception as e:
        print(f"Error in analysis workflow: {str(e)}")
        db.rollback()
    finally:
        db.close()


@app.post("/api/cases/{case_id}/approve")
async def approve_case(case_id: str, review: HumanReviewInput = None, db: Session = Depends(get_db)):
    """Human review and approval of a case."""
    try:
        case = db.query(PromotionCase).filter(PromotionCase.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        if not case.agent_6_output:
            raise HTTPException(status_code=400, detail="Case must be analyzed before approval")
        
        case.human_review_approved = True
        case.human_review_notes = review.human_notes if review else None
        case.human_review_at = datetime.utcnow()
        case.status = CaseStatus.FINALIZED
        case.finalized_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "message": "Case approved and finalized",
            "case_id": case_id,
            "status": case.status.value,
            "finalized_at": case.finalized_at.isoformat()
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/cases/{case_id}/request-reanalysis")
async def request_reanalysis(case_id: str, request: ReanalysisRequest = None, db: Session = Depends(get_db)):
    """Request re-analysis of a case."""
    try:
        case = db.query(PromotionCase).filter(PromotionCase.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        case.status = CaseStatus.DRAFT
        reason = request.reason if request else None
        case.human_review_notes = f"Re-analysis requested: {reason}" if reason else "Re-analysis requested"
        case.updated_at = datetime.utcnow()
        case.final_judgment = None
        
        # Clear previous agent outputs
        for agent_num in range(1, 7):
            field_name = f"agent_{agent_num}_output"
            setattr(case, field_name, None)
        
        db.commit()
        
        return {
            "message": "Re-analysis requested",
            "case_id": case_id,
            "status": case.status.value
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
