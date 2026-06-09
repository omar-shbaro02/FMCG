# FMCG Trade Promotion Distortion Intelligence

A sophisticated multi-agent decision intelligence system for FMCG companies that evaluates whether promotional growth is healthy, fragile, distortionary, or misleading to leadership.

## System Architecture

The system uses a 6-agent orchestration workflow:

1. **Agent 1**: Campaign Intent & Commercial Context Analyst
   - Analyzes the underlying commercial intent and risk tolerance
   - Identifies intent clarity and commercial context flags

2. **Agent 2**: Trade Concentration & Key Account Risk Analyst
   - Evaluates concentration risk and trade loading behavior
   - Assesses sustainability based on distribution

3. **Agent 3**: Margin & Trade Efficiency Analyst
   - Evaluates financial impact and margin erosion
   - Assesses trade spend efficiency and financial sustainability

4. **Agent 4**: Demand & Inventory Propagation Analyst
   - Distinguishes between real demand and artificial inventory buildup
   - Identifies bullwhip effect risks and supply chain issues

5. **Agent 5**: Governance & Escalation Analyst
   - Synthesizes all risk signals
   - Recommends governance actions and escalation paths

6. **Agent 6**: Executive Distortion Intelligence Brain
   - Produces the final leadership judgment
   - Classifies growth as: HEALTHY, FRAGILE, DISTORTIONARY, or MISLEADING

## Tech Stack

**Backend:**
- FastAPI (Python async web framework)
- SQLAlchemy (ORM)
- SQLite (MVP database)
- OpenAI API (LLM integration)

**Frontend:**
- React 18
- Vite (build tool)
- TailwindCSS (styling)
- React Router (navigation)
- Lucide React (icons)

## Prerequisites

- Python 3.9+
- Node.js 16+ & npm
- OpenAI API key (GPT-4 recommended)

## Installation & Quick Start

### Automated Setup (Recommended)

From the FMCG directory, run the setup script:

**Mac/Linux:**
```bash
bash setup.sh
```

**Windows:**
```bash
setup.bat
```

This will install all dependencies for both backend and frontend.

### Manual Setup

**Backend:**
```bash
cd backend

# Create Python virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-xxxxxxxxxxxx
# OPENAI_MODEL=gpt-4o
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install
```

## Running the Application

### From Parent Directory (Simplest)

```bash
# From FMCG directory
npm run dev
```

This runs both backend and frontend simultaneously.

You'll see:
```
[0] INFO:     Uvicorn running on http://0.0.0.0:8000
[1] ➜  Local:   http://localhost:5173/
```

### Separately (Alternative)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/Scripts/activate  # Or: venv\Scripts\activate on Windows
python main.py
```

Backend runs on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Frontend runs on `http://localhost:5173`

## Environment Variables

Create a `.env` file in the `backend` directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o

# Database
DATABASE_URL=sqlite:///./fmcg_cases.db

# CORS
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

## API Documentation

Once the backend is running, interactive API documentation is available at:

```
http://localhost:8000/docs
```

This provides a Swagger UI where you can:
- View all endpoints
- See request/response schemas
- Test endpoints directly

## API Endpoints

### Cases

- `POST /api/cases` - Create new promotion case
- `GET /api/cases` - List all cases
- `GET /api/cases/{case_id}` - Get case details with all agent outputs
- `POST /api/cases/{case_id}/analyze` - Start agent analysis workflow
- `POST /api/cases/{case_id}/approve` - Approve case and finalize
- `POST /api/cases/{case_id}/request-reanalysis` - Request re-analysis

### Health

- `GET /health` - System health check

## Workflow

### 1. Create a Promotion Case

Navigate to **New Case** and fill in the structured form with:
- Promotion identification (ID, brand, category, SKU)
- Channel and market details (channel, key account, region)
- Promotion period and campaign details
- Sales metrics (baseline, promotion volume, uplift %)
- Concentration metrics (key account %, channel %, participating stores)
- Inventory signals (sell-in, sell-out, forecast variance)
- Financial metrics (discount, trade spend, margins)
- Data quality confidence level

### 2. Start Agent Analysis

Click **Start Analysis** to trigger the sequential agent workflow:
- Agents run one after another
- Each agent receives prior outputs as context
- Case status changes from "Draft" → "Analyzing" → "Needs Review"

### 3. Review Agent Outputs

Switch to **Agent Analysis** tab to:
- See each agent's structured decision
- Review confidence scores
- Inspect detailed reasoning

### 4. Review Final Executive Judgment

Switch to **Final Judgment** tab to:
- See the 4 core classifications:
  - **Growth Health**: HEALTHY | FRAGILE | DISTORTIONARY | MISLEADING
  - **Distortion Severity**: none | low | moderate | high | critical
  - **Strategic Sustainability**: sustainable | at_risk | unsustainable
- Review executive interpretation
- Understand judgment drivers
- Learn what leadership should NOT assume
- See required next actions

### 5. Human Review & Approval

Switch to **Human Review** tab to:
- Approve the recommendation as-is
- Add your own notes and modifications
- Request re-analysis if needed
- Finalize the case

## Key Features

### Enterprise-Grade UI
- Clean, professional design
- Status badges and severity indicators
- Confidence bars with color coding
- Responsive data tables

### Structured Workflow
- Multi-step case progression
- Visual workflow stepper
- Real-time analysis status updates
- Agent-by-agent confidence tracking

### Comprehensive Judgment
- Not a summary; a definitive judgment
- Based on all specialist inputs
- Clear risk flags for leadership
- Actionable recommendations

### Data Integrity
- Missing data is not invented
- System continues with available information
- Data quality confidence levels tracked
- Error handling and fallback behavior

### Governance
- Case severity classification
- Escalation path recommendations
- Governance risk flags
- Executive attention filtering

## Sample Data

To test the system with sample promotion data:

```python
# Sample case data
{
    "promotion_id": "PROMO-2024-Q1-001",
    "brand": "BrandX",
    "category": "Beverages",
    "sku": "BX-COLA-2L",
    "channel": "Modern Trade",
    "key_account": "Retailer ABC",
    "region": "North",
    "promotion_period_start": "2024-01-15",
    "promotion_period_end": "2024-02-15",
    "campaign_objective": "Volume Growth",
    "promotion_type": "Price Discount",
    "baseline_sales_volume": 50000,
    "promotion_sales_volume": 92500,
    "uplift_percent": 85,
    "key_account_contribution_percent": 62,
    "channel_contribution_percent": 58,
    "num_participating_customers": 342,
    "sell_in_volume": 95000,
    "sell_out_volume": 78000,
    "post_promotion_demand": 48000,
    "repeat_order_behavior": {"repeat_rate": 0.42, "trend": "declining"},
    "inventory_impact": {"shelf_inventory_increase": "45%", "warehouse_buildup": true},
    "replenishment_issues": "High variance in replenishment orders",
    "forecast_variance": 18.5,
    "discount_percent": 15,
    "trade_spend": 85000,
    "gross_margin_before": 38.5,
    "gross_margin_during": 22.1,
    "management_notes": "Aggressive promotional push by sales team. Retailer has significant buying power.",
    "data_quality_confidence": 78
}
```

## Architecture Details

### Backend Structure

```
backend/
├── main.py                    # FastAPI app & routes
├── models.py                  # SQLAlchemy models
├── requirements.txt
├── .env.example
├── agents/
│   ├── agent_1_intent.py
│   ├── agent_2_concentration.py
│   ├── agent_3_margin.py
│   ├── agent_4_demand.py
│   ├── agent_5_governance.py
│   ├── agent_6_brain.py
├── schemas/
│   └── schemas.py            # Pydantic schemas
└── orchestrator/
    └── orchestrator.py       # Agent execution orchestrator
```

### Frontend Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── index.css
    ├── components/
    │   ├── Navigation.jsx
    │   └── Badges.jsx
    ├── pages/
    │   ├── Dashboard.jsx
    │   ├── NewCase.jsx
    │   └── CaseDetail.jsx
    └── hooks/
        └── useAPI.js
```

### Database Schema

**PromotionCase Table:**
- Stores complete case data
- Agent outputs (JSON fields for flexibility)
- Human review information
- Case status tracking

**AgentAudit Table:**
- Stores all agent executions
- Raw input/output for debugging
- Confidence scores
- Error messages

## Error Handling

- **Missing LLM Output**: Returns error with descriptive message
- **Agent Failure**: Subsequent agents are skipped, errors logged
- **Invalid JSON**: Attempts to extract JSON from response, falls back gracefully
- **Database Errors**: Rolled back transactions, descriptive error responses

## Development Notes

### Adding New Agents

1. Create new agent file in `backend/agents/`
2. Define system prompt and schema
3. Add orchestrator logic in `orchestrator.py`
4. Update case model to store outputs

### Customizing Agent Logic

Each agent's decision logic is defined in its prompt file. Modify the prompts to adjust:
- Risk thresholds
- Decision criteria
- Output focus areas
- Governance recommendations

### Scaling Considerations

- Current: SQLite (MVP)
- Production: PostgreSQL, DuckDB, or Snowflake
- Agent execution: Can be moved to async queue (Celery, Airflow)
- LLM provider: Configurable (Azure OpenAI, Claude, local LLMs)

## Testing

To test the API:

```bash
# Using curl
curl -X GET http://localhost:8000/health

# Using Python
import requests
response = requests.get('http://localhost:8000/api/cases')
print(response.json())
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Find process using port 5173
lsof -i :5173

# Kill process
kill -9 <PID>
```

### CORS Errors

Ensure `FRONTEND_URL` in `.env` matches your frontend URL (default: http://localhost:5173)

### OpenAI API Errors

- Verify API key is correct
- Check OpenAI account has available credits
- Verify model name (gpt-4o is recommended)

### Database Errors

Delete `fmcg_cases.db` to reset the database

## Performance Tuning

- Agent analysis typically takes 45-90 seconds for full 6-agent workflow
- Adjust `max_tokens` in orchestrator for faster/cheaper operation
- Temperature set to 0.7 for consistency with some creativity

## Production Deployment

### Backend (Uvicorn)

```bash
# Production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# With Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Frontend (Build)

```bash
npm run build
# Outputs to dist/
```

### Docker

Create `Dockerfile` and `docker-compose.yml` for containerized deployment.

## License

Commercial - All Rights Reserved

## Support

For issues or questions about the system:
1. Check the troubleshooting section above
2. Review agent prompts for logic changes
3. Check API logs for execution errors
4. Verify environment variables are set correctly

## Roadmap

- [ ] Multi-language support
- [ ] Advanced filtering and search
- [ ] Batch case processing
- [ ] Custom agent templates
- [ ] Integration with enterprise data sources
- [ ] Real-time dashboard with KPIs
- [ ] Export reports (PDF, Excel)
- [ ] User authentication and role-based access
- [ ] Audit logging and compliance
- [ ] Machine learning-based agent feedback
