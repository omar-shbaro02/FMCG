#!/usr/bin/env python3
"""
Setup script for FMCG Trade Promotion Intelligence System.
Initializes database and loads sample data.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from models import Base, PromotionCase
from schemas.schemas import PromotionCaseInput
from sample_data import get_all_sample_cases
import uuid
from datetime import datetime
import json

def setup_database():
    """Initialize database and tables"""
    print("🔧 Setting up database...")
    
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./fmcg_cases.db')
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    
    return engine

def load_sample_data(engine):
    """Load sample promotion cases"""
    print("📊 Loading sample data...")
    
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_count = db.query(PromotionCase).count()
        if existing_count > 0:
            print(f"⚠ Database already has {existing_count} cases. Skipping sample data load.")
            return
        
        sample_cases = get_all_sample_cases()
        
        for case_data in sample_cases:
            # Convert to PromotionCaseInput for validation
            case_input = PromotionCaseInput(**case_data)
            
            # Create database record
            db_case = PromotionCase(
                id=str(uuid.uuid4()),
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
            )
            db.add(db_case)
            print(f"  ✓ Added sample case: {case_input.promotion_id}")
        
        db.commit()
        print(f"✓ Loaded {len(sample_cases)} sample promotion cases")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error loading sample data: {e}")
        raise
    finally:
        db.close()

def main():
    print("\n" + "="*60)
    print("FMCG Trade Promotion Distortion Intelligence - Setup")
    print("="*60 + "\n")
    
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠ Warning: OPENAI_API_KEY not set in environment")
        print("  The system will not be able to run agent analysis without it.")
        print("  Please set: export OPENAI_API_KEY=sk-xxxxxx\n")
    
    # Setup database
    engine = setup_database()
    
    # Load sample data (optional)
    response = input("Load sample promotion cases? (y/n): ").strip().lower()
    if response == 'y':
        load_sample_data(engine)
    
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Backend: python main.py")
    print("2. Frontend: npm run dev")
    print("3. Open: http://localhost:5173")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
