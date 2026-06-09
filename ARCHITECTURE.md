# FMCG Trade Promotion Distortion Intelligence
# System Architecture & Design Document

## Executive Overview

This is a sophisticated multi-agent decision intelligence system designed specifically for FMCG (Fast-Moving Consumer Goods) companies to evaluate trade promotion health.

**Core Purpose**: Determine whether promotional growth is:
- **HEALTHY** - Real, sustainable demand increase
- **FRAGILE** - Dependent on promotional mechanics
- **DISTORTIONARY** - Market-damaging trade loading
- **MISLEADING** - Leadership being misled by inflated numbers

---

## System Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                             │
│  Dashboard → New Case → Analysis Workflow → Review → Finalize   │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                    REACT FRONTEND (Vite)                        │
│  • Dashboard with case list & metrics                          │
│  • Case creation form (25+ fields)                             │
│  • Real-time workflow tracking                                 │
│  • Agent output visualization                                   │
│  • Executive report generation                                 │
│  • Human review & approval interface                           │
└─────────────────────────────────────────────────────────────────┘
                                ↓
                    (HTTP REST API)
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            ORCHESTRATOR (Sequential Workflow)           │   │
│  │  Agent 1 → Agent 2 → Agent 3 → Agent 4 → Agent 5 → 6   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                ↓
        (OpenAI API calls for each agent)
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│              STORAGE & PERSISTENCE LAYER                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SQLite Database (MVP) / PostgreSQL (Production)        │  │
│  │  • Promotion cases with full input data                 │  │
│  │  • Agent outputs (JSON) for each specialist             │  │
│  │  • Human review decisions                               │  │
│  │  • Audit trail of all agent executions                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## The 6-Agent Orchestration System

### Agent 1: Campaign Intent & Commercial Context Analyst

**Role**: Establish baseline understanding and context

**Input**: 
- Complete promotion case data
- Sales figures, financial metrics
- Management notes

**Key Analysis**:
- What is the REAL commercial intent?
- Is this volume-drive, market-share grab, inventory-clearing, or something else?
- What risk level is the business willing to tolerate?
- Are there red flags in how this is framed?

**Output**:
```json
{
  "campaign_intent": "Aggressive volume push targeting key account",
  "evaluation_lens": "volume_growth_with_concentration_risk",
  "risk_tolerance": "high",
  "commercial_context_flags": ["aggressive_sales_push", "key_account_negotiation", "eoy_numbers"],
  "intent_clarity": "clear but aggressive",
  "confidence": 0.88,
  "handoff_note": "Intent is clear but high-risk. Recommend concentration analysis."
}
```

**Confidence**: 85-95% (based on data clarity)

---

### Agent 2: Trade Concentration & Key Account Risk Analyst

**Role**: Evaluate concentration risk and sustainability

**Input**: 
- Case data + Agent 1 output
- Sales distribution metrics
- Key account contribution %

**Key Analysis**:
- How concentrated is the growth?
- Is one account/channel driving most of it?
- Classic trade loading indicators (sell-in >> sell-out)?
- Will this growth sustain when the promotion ends?

**Output**:
```json
{
  "growth_distribution": {"concentrated": true, "top_account_percent": 62},
  "main_concentration_source": "single_key_account_negotiation",
  "concentration_risk_level": "high",
  "key_account_dependency": {"accounts": ["Retailer ABC"], "percent_of_growth": 62},
  "channel_trade_risk": {"gap": 17000, "gap_percent": 18.2},
  "sell_in_vs_sell_out_visibility": "clear_gap_visible",
  "trade_loading_risk": "moderate_to_high",
  "sustainability_judgment": "fragile_post_promotion",
  "confidence": 0.82,
  "handoff_note": "High concentration + sell-in/sell-out gap suggests inventory buildup"
}
```

**Confidence**: 75-90%

---

### Agent 3: Margin & Trade Efficiency Analyst

**Role**: Financial impact and ROI assessment

**Input**: 
- Case data + Agent 1 & 2 outputs
- Margin data, discount levels, trade spend

**Key Analysis**:
- How much margin is being sacrificed?
- Is the trade spend justified by incremental volume?
- Is the discount creating dependency?
- Can this be repeated sustainably?

**Output**:
```json
{
  "margin_impact": {
    "baseline_margin": 38.5,
    "promo_margin": 22.1,
    "erosion_points": -16.4,
    "total_impact": -890000
  },
  "trade_spend_efficiency": 1.09,  # per unit uplift
  "financial_risk_level": "high",
  "discount_dependency_risk": "high - growth highly elastic",
  "financial_sustainability_judgment": "unsustainable_at_current_investment",
  "confidence": 0.85,
  "handoff_note": "Margin erosion severe. Trade spend high. Financial model doesn't work."
}
```

**Confidence**: 80-95%

---

### Agent 4: Demand & Inventory Propagation Analyst

**Role**: Distinguish real demand from artificial buildup

**Input**: 
- Case data + Agents 1-3 outputs
- Inventory, replenishment, post-promo demand data

**Key Analysis**:
- Is the volume growth REAL demand or inventory buildup?
- Is there bullwhip effect up the supply chain?
- What happens post-promotion?
- Repeat order patterns?

**Output**:
```json
{
  "demand_movement": {
    "during_promotion": "artificially_high_sell_in",
    "post_promotion": "sharp_decline_to_48k",
    "true_demand_signal": "approximately_baseline"
  },
  "inventory_impact": {
    "buildup": "severe_45_percent_increase",
    "propagation": "up_supply_chain"
  },
  "propagation_risk_level": "high",
  "post_promotion_behavior": "sharp_demand_cliff",
  "root_cause_confidence": "high_confidence",
  "confidence": 0.87,
  "handoff_note": "Clear inventory buildup with cliff post-promo. Not real demand."
}
```

**Confidence**: 75-90%

---

### Agent 5: Governance & Escalation Analyst

**Role**: Risk synthesis and governance recommendation

**Input**: 
- Case data + All Agent 1-4 outputs

**Key Analysis**:
- Overall severity combining all risk signals
- Who should make this decision?
- What governance actions are needed?
- Should this escalate?

**Output**:
```json
{
  "overall_case_severity": "high",
  "urgency": "elevated",
  "recommended_escalation_level": "VP_Marketing",
  "primary_owner": "Brand Manager",
  "supporting_owners": ["Sales Director", "Finance Manager"],
  "recommended_governance_action": "pause_and_reassess",
  "reassessment_timing": "within_2_weeks",
  "executive_attention_filter": "yes_cfo_should_know",
  "governance_risk_flags": ["margin_erosion", "financial_unsustainability", "inventory_risk"],
  "handoff_to_final_brain": "Multiple risk signals align: concentration, trade loading, financial unsustainability."
}
```

**Confidence**: 80-90%

---

### Agent 6: Executive Distortion Intelligence Brain

**Role**: FINAL JUDGMENT for leadership

**Input**: 
- Case data + All Agent 1-5 outputs
- Must synthesize, not summarize

**Key Analysis**:
- Is this growth HEALTHY, FRAGILE, DISTORTIONARY, or MISLEADING?
- What is the strategic impact?
- What must leadership know?
- What are they likely assuming that's WRONG?

**Output**:
```json
{
  "growth_health": "DISTORTIONARY",
  "distortion_severity": "high",
  "strategic_sustainability": "unsustainable",
  "recommended_action": "Halt expansion of this promotional model. Conduct retailer negotiation reset.",
  "confidence": 0.89,
  "executive_interpretation": "This appears to be 85% volume uplift, but investigation reveals classic trade loading. Retailer received aggressive discount to build inventory, not to drive end-consumer sales. Post-promotion, demand will crater. The financial model is indefensible.",
  "strongest_judgment_drivers": [
    "Sell-in (95K) >> Sell-out (78K) with 18% gap",
    "Post-promotion demand (48K) << baseline (50K)",
    "Repeat order rate collapsing from 72% to 38%",
    "Margin erosion from 38.5% to 22.1% unaffordable",
    "Trade spend ROI 1.09 with short payback horizon"
  ],
  "what_leadership_should_not_assume": [
    "Do NOT assume this 85% uplift is real demand",
    "Do NOT expect this volume to sustain post-promotion",
    "Do NOT use this as precedent for future negotiations",
    "Do NOT report this as win to investors",
    "Do NOT plan supply chain for post-promo at this volume"
  ],
  "required_next_action": "Conduct retailer conversation about sustainable model",
  "owner": "VP Marketing + Sales Director",
  "timing": "within 1 week",
  "executive_risk_flags": [
    "inventory_crisis_risk",
    "financial_performance_risk",
    "market_distortion_risk",
    "investor_communication_risk"
  ]
}
```

**Confidence**: 80-92%

---

## Key System Features

### 1. Structured Workflow
- Sequential agent execution (1→2→3→4→5→6)
- Each agent has full context from predecessors
- Real-time status updates in UI
- Comprehensive audit trail

### 2. Specific Judgment, Not Summary
- Agent 6 makes a JUDGMENT (HEALTHY/FRAGILE/DISTORTIONARY/MISLEADING)
- Not a summary of other outputs
- Backed by clear reasoning
- Includes what leadership should NOT assume

### 3. Enterprise-Grade UI
- Clean, professional dashboard
- Real-time workflow tracking
- Clear risk visualization
- Executive report formatting
- Human review & approval gate

### 4. Data Integrity
- Missing data explicitly acknowledged
- System continues with available info
- Data quality confidence levels tracked
- No invented information

### 5. Governance Integration
- Severity/urgency classification
- Escalation path recommendations
- Risk flags for leadership
- Human review before finalization

---

## Technical Stack Decision Rationale

### Backend: FastAPI
✓ Fast, async, production-ready
✓ Excellent for AI agent integration
✓ Auto-generated API docs
✓ Strong typing with Pydantic

### Frontend: React + Vite + TailwindCSS
✓ Professional, enterprise UI
✓ Real-time updates
✓ Rapid development
✓ Excellent performance

### Database: SQLite (MVP) → PostgreSQL (Production)
✓ SQLite: Zero setup, perfect for MVP
✓ PostgreSQL: Scales to enterprise
✓ JSON fields for flexible agent outputs

### LLM: OpenAI API
✓ GPT-4 for complex reasoning
✓ Reliable, battle-tested
✓ Easy integration
✓ Can swap for alternatives (Claude, local LLMs)

---

## Data Flow Example: Complete Workflow

```
USER CREATES CASE
    ↓
    ├─ Fills 25+ fields with promotion data
    ├─ Confidence level specified (80%)
    └─ Submits → Case created with status="Draft"

USER CLICKS "START ANALYSIS"
    ↓
    └─ Case status → "Analyzing"

AGENT 1 EXECUTES
    ├─ Receives: Raw case data
    ├─ LLM Call: Analyzes intent and context
    ├─ Returns: Intent analysis with confidence
    └─ Stored: agent_1_output (JSON)

AGENT 2 EXECUTES
    ├─ Receives: Case data + Agent 1 output
    ├─ LLM Call: Analyzes concentration
    ├─ Returns: Concentration risk assessment
    └─ Stored: agent_2_output (JSON)

[AGENTS 3, 4, 5 similar pattern]

AGENT 6 EXECUTES
    ├─ Receives: All prior agent outputs + case data
    ├─ LLM Call: Makes final judgment
    ├─ Returns: HEALTHY/FRAGILE/DISTORTIONARY/MISLEADING
    └─ Stored: agent_6_output (JSON)

CASE STATUS UPDATED
    └─ "Analyzing" → "Needs Review"

USER REVIEWS
    ├─ Views all agent outputs in tabs
    ├─ Reads executive interpretation
    ├─ Sees risk flags and recommendations
    └─ Can request re-analysis if needed

USER APPROVES
    ├─ Adds optional notes
    ├─ Marks as reviewed
    └─ Case status → "Finalized"

CASE COMPLETE
    └─ Stored with all agent outputs and human review
```

---

## Database Schema

### PromotionCase Table
```
id                                  VARCHAR(36) PRIMARY KEY
promotion_id                        VARCHAR(100) UNIQUE
brand, category, sku, channel       VARCHAR(255)
promotion_period_start/end          VARCHAR(10)
baseline_sales_volume               FLOAT
promotion_sales_volume              FLOAT
... 25 more fields ...
agent_1_output through agent_6_output   JSON
final_judgment                      JSON
human_review_approved               BOOLEAN
status                              ENUM(Draft, Analyzing, Needs Review, Finalized)
created_at, updated_at              DATETIME
```

### AgentAudit Table
```
id                                  VARCHAR(36) PRIMARY KEY
case_id                             VARCHAR(36) FOREIGN KEY
agent_number                        INTEGER
raw_input                           TEXT
raw_output                          TEXT
parsed_output                       JSON
confidence                          FLOAT
error_message                       TEXT (if any)
created_at                          DATETIME
```

---

## Error Handling Strategy

### Missing Data
- System acknowledges it
- Continues with available information
- Data quality confidence adjusted
- Agent expresses reduced confidence

### LLM Failures
- Catches JSON parsing errors
- Attempts graceful fallback
- Logs to audit table
- Subsequent agents skipped with notification
- User informed to retry

### Invalid API Responses
- Timeout handling: Retry with exponential backoff
- Rate limiting: Queue management
- Invalid JSON: Attempt regex extraction
- All failures logged for debugging

---

## Performance Characteristics

### Typical Analysis Time
- Agent 1: ~8-12 seconds
- Agent 2: ~10-15 seconds
- Agent 3: ~8-12 seconds
- Agent 4: ~12-18 seconds
- Agent 5: ~10-14 seconds
- Agent 6: ~12-18 seconds
- **Total**: ~60-90 seconds for full workflow

### Cost per Analysis
- 6 LLM calls
- ~4000-6000 tokens per agent
- GPT-4: ~$0.50-1.00 per case
- GPT-3.5: ~$0.05-0.10 per case

---

## Security Considerations

### API Keys
- Never hardcoded
- Environment variables only
- .env not committed to version control
- Rotate regularly

### Data Sensitivity
- Case data stored locally
- No external logging of sensitive data
- Audit trail maintained for compliance
- CORS configured for known frontend

### Authentication (Optional)
- Can add JWT tokens
- Can integrate SSO
- Rate limiting supported

---

## Future Enhancements

### Phase 2
- Authentication & user roles
- Case history & trending
- Batch processing
- Export reports (PDF, Excel)

### Phase 3
- Machine learning feedback loop
- Custom agent templates
- Integration with enterprise data sources
- Real-time dashboard with KPIs

### Phase 4
- Multi-language support
- Collaborative review workflows
- Prediction capabilities
- Automated remediation suggestions

---

## Deployment Architecture

### Development
```
Local Machine
├─ Backend (localhost:8000)
├─ Frontend (localhost:5173)
└─ SQLite Database
```

### Production
```
Cloud Infrastructure (AWS/GCP/Azure)
├─ Backend (API Gateway → ECS/Cloud Run)
├─ Frontend (CloudFront/CDN)
├─ Database (RDS PostgreSQL)
├─ Secret Management (Secrets Manager)
└─ Monitoring (CloudWatch/Stackdriver)
```

---

## Conclusion

This system transforms raw promotion data into executive-ready judgment. It combines:
- **Structured workflow** (6 specialized agents)
- **Enterprise UI** (professional, clear, actionable)
- **Business logic** (governs with risk assessment)
- **Data integrity** (no invented information)

The result: Leadership can confidently distinguish healthy growth from distortion.
