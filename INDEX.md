# FMCG Trade Promotion Distortion Intelligence
## 📚 Complete Navigation Guide

Welcome! This guide helps you navigate the entire system.

---

## 🚀 START HERE

### First Time? Follow This Order:

1. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** ← Read this first (5 min)
   - Overview of what was built
   - Feature highlights
   - Quick start overview

2. **[QUICKSTART.md](QUICKSTART.md)** ← Then this (10 min)
   - Step-by-step setup instructions
   - Choose your OS (Mac/Linux/Windows)
   - Troubleshooting quick fixes

3. **Run the system** ← Test it
   - Start backend
   - Start frontend
   - Create a promotion case
   - Watch agents analyze it

4. **[README.md](README.md)** ← Reference anytime
   - Complete documentation
   - All API endpoints
   - Configuration options
   - Production deployment

---

## 📋 Documentation Index

### Quick References
| Document | Purpose | Read Time |
|----------|---------|-----------|
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | System overview | 5 min |
| [QUICKSTART.md](QUICKSTART.md) | Setup & run | 10 min |

### Deep Dives
| Document | Purpose | Read Time |
|----------|---------|-----------|
| [README.md](README.md) | Complete reference | 20 min |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design | 30 min |
| [CONFIG.md](CONFIG.md) | Configuration guide | 15 min |

### System Files
| Directory | Purpose |
|-----------|---------|
| `backend/` | FastAPI application |
| `frontend/` | React application |
| `backend/agents/` | 6 AI agent implementations |
| `backend/schemas/` | Pydantic data schemas |
| `backend/orchestrator/` | Agent orchestration logic |

---

## 🎯 By Use Case

### "I want to set up the system locally"
1. [QUICKSTART.md](QUICKSTART.md) - Step by step setup
2. Choose `setup.sh` (Mac/Linux) or `setup.bat` (Windows)
3. `python backend/setup.py` - Load sample data
4. Start both servers and open browser

### "I want to understand how it works"
1. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Overview
2. [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed design
3. Explore `backend/agents/` - See agent logic
4. Read the 6 agent files to understand reasoning

### "I want to customize agent logic"
1. [ARCHITECTURE.md](ARCHITECTURE.md) - Understand workflow
2. Open `backend/agents/agent_X_name.py`
3. Modify the `AGENT_X_SYSTEM_PROMPT`
4. Test with sample cases

### "I want to deploy to production"
1. [README.md](README.md#production-deployment) - Deployment section
2. [ARCHITECTURE.md](ARCHITECTURE.md#deployment-architecture) - Architecture
3. [CONFIG.md](CONFIG.md#deployment-configuration) - Docker config
4. Set up cloud infrastructure (AWS/GCP/Azure)

### "I want to integrate with my data"
1. [README.md](README.md#customizing-agent-logic) - Customization
2. [CONFIG.md](CONFIG.md#database-configuration) - Database setup
3. Add your data source connections
4. Modify `backend/main.py` routes

---

## 📂 Backend File Guide

### Core Application
```
backend/main.py
└─ FastAPI app, all HTTP routes
   ├─ POST /api/cases - Create case
   ├─ GET /api/cases - List cases
   ├─ POST /api/cases/{id}/analyze - Start analysis
   └─ Full API docs at /docs
```

### Database
```
backend/models.py
└─ SQLAlchemy models
   ├─ PromotionCase - Main case table
   └─ AgentAudit - Agent execution audit trail

backend/setup.py
└─ Database initialization
   ├─ Creates tables
   └─ Loads sample data
```

### Agents (The Brain)
```
backend/agents/
├─ agent_1_intent.py          Campaign intent analysis
├─ agent_2_concentration.py   Trade concentration risk
├─ agent_3_margin.py          Financial impact
├─ agent_4_demand.py          Demand signals
├─ agent_5_governance.py      Governance & escalation
└─ agent_6_brain.py           Executive judgment

Each agent has:
✓ System prompt (instructions)
✓ Prompt builder (context + case data)
✓ Response parser (JSON → Pydantic model)
✓ Confidence scoring
```

### Orchestration
```
backend/orchestrator/orchestrator.py
└─ Orchestrator class
   ├─ run_agent() - Execute single agent
   └─ orchestrate() - Sequential workflow
       └─ Chains all 6 agents
```

### Data Definitions
```
backend/schemas/schemas.py
└─ Pydantic models for all data
   ├─ PromotionCaseInput - Create case
   ├─ Agent1Output - Agent 1 output schema
   ├─ ... (through Agent6Output)
   └─ FinalJudgment - Final report schema
```

### Sample Data
```
backend/sample_data.py
└─ 4 representative promotion cases
   ├─ HEALTHY - Real sustainable growth
   ├─ FRAGILE - Post-promo decline risk
   ├─ DISTORTIONARY - Trade loading
   └─ MISLEADING - Leadership misled
```

---

## 📂 Frontend File Guide

### Main Application
```
frontend/src/App.jsx
└─ Main React component with routing
   ├─ Dashboard page
   ├─ New case page
   ├─ Case detail page
   └─ Navigation

frontend/src/main.jsx
└─ React entry point
```

### Pages
```
frontend/src/pages/
├─ Dashboard.jsx
│  └─ Case list with status, health, recommendations
├─ NewCase.jsx
│  └─ 25+ field form for promotion data
└─ CaseDetail.jsx
   ├─ Case data tab - View all input fields
   ├─ Workflow tab - Watch agents execute
   ├─ Judgment tab - Executive report
   └─ Review tab - Approve/finalize
```

### Components
```
frontend/src/components/
├─ Navigation.jsx
│  └─ Header with logo and navigation links
└─ Badges.jsx
   ├─ StatusBadge - Draft/Analyzing/Review/Finalized
   ├─ HealthBadge - Healthy/Fragile/Distortionary/Misleading
   ├─ SeverityBadge - Risk levels
   └─ ConfidenceBar - Confidence visualization
```

### API Integration
```
frontend/src/hooks/useAPI.js
└─ API client with methods
   ├─ getCases() - Get all cases
   ├─ getCase(id) - Get single case
   ├─ createCase(data) - Create new case
   ├─ analyzeCase(id) - Start analysis
   ├─ approveCase(id, notes) - Approve case
   └─ requestReanalysis(id, reason) - Request re-analysis
```

### Styling
```
frontend/src/index.css
└─ Global Tailwind styles + custom utilities
   ├─ .card - Card component
   ├─ .badge - Badge styling
   ├─ .btn - Button variants
   └─ .badge-* - Badge variants
```

---

## 🔑 Key Concepts

### The 6 Agents

| # | Agent | Role | Focuses On |
|---|-------|------|-----------|
| 1 | Intent | Baseline understanding | Commercial intent, risk tolerance |
| 2 | Concentration | Concentration risk | Key account dependency, trade loading |
| 3 | Margin | Financial impact | Margin erosion, trade spend ROI |
| 4 | Demand | Real demand signals | True demand vs inventory buildup |
| 5 | Governance | Risk synthesis | Escalation, governance actions |
| 6 | Brain | Final judgment | HEALTHY/FRAGILE/DISTORTIONARY/MISLEADING |

### The 4 Judgments

```
HEALTHY
├─ Real demand growth
├─ Sustainable post-promotion
├─ Good financial model
└─ Market-positive

FRAGILE
├─ Growth dependent on mechanics
├─ High post-promo decline risk
├─ Concentration concerns
└─ Short-term only

DISTORTIONARY
├─ Trade loading scenario
├─ Market-damaging tactics
├─ Inventory buildup
└─ Unsustainable

MISLEADING
├─ Leadership being deceived
├─ Numbers misrepresent reality
├─ Sell-in >> sell-out gap
└─ Financial model indefensible
```

---

## ⚡ Quick Commands

### Setup
```bash
# Mac/Linux
bash setup.sh

# Windows
setup.bat
```

### Backend
```bash
cd backend
source venv/Scripts/activate      # venv\Scripts\activate on Windows
python main.py                     # Runs on localhost:8000
```

### Frontend
```bash
cd frontend
npm run dev                        # Runs on localhost:5173
```

### Database
```bash
cd backend
python setup.py                    # Initialize & load sample data
```

### View API Docs
```
http://localhost:8000/docs        # Interactive Swagger UI
```

---

## 🛠️ Common Tasks

### Add a New Agent

1. Create `backend/agents/agent_7_name.py`
2. Define `AGENT_7_SYSTEM_PROMPT`
3. Create `create_agent_7_prompt()` function
4. Create `parse_agent_7_response()` function
5. Add to `backend/orchestrator/orchestrator.py`
6. Update UI in `frontend/src/pages/CaseDetail.jsx`

### Change Agent Logic

1. Open `backend/agents/agent_X_name.py`
2. Edit `AGENT_X_SYSTEM_PROMPT`
3. Test with sample case
4. Review changes in Agent output tab

### Connect to Your Database

1. Update `DATABASE_URL` in `.env`
2. Modify database import in `backend/main.py`
3. Optionally migrate data via `backend/setup.py`

### Deploy to Cloud

1. Follow [ARCHITECTURE.md](ARCHITECTURE.md#deployment-architecture)
2. Use Docker files from [CONFIG.md](CONFIG.md#docker)
3. Set secrets in cloud provider
4. Deploy both services

---

## 🚨 Troubleshooting

### Setup Issues?
→ See [QUICKSTART.md - Troubleshooting](QUICKSTART.md#troubleshooting-configuration)

### API Errors?
→ Check [README.md - Troubleshooting](README.md#troubleshooting)

### Performance Issues?
→ See [ARCHITECTURE.md - Performance](ARCHITECTURE.md#performance-characteristics)

### Need Different Model?
→ See [CONFIG.md - LLM Integration](CONFIG.md#llm-provider-integration)

---

## 📞 File Quick Reference

### Must Read (In Order)
1. PROJECT_SUMMARY.md
2. QUICKSTART.md
3. README.md

### Configuration & Customization
- CONFIG.md - All configuration options
- ARCHITECTURE.md - System design & customization
- backend/agents/*.py - Agent prompt logic

### Setup & Deployment
- setup.sh or setup.bat - Automated setup
- backend/setup.py - Database initialization
- CONFIG.md - Deployment guide

---

## ✅ Verification Checklist

After setup, verify everything works:

```
☐ Backend starts without errors (localhost:8000)
☐ Frontend loads (localhost:5173)
☐ Dashboard shows 4 sample cases
☐ Can view case details
☐ API docs work (localhost:8000/docs)
☐ Can create a new case
☐ Analysis workflow completes
☐ Executive report displays
☐ Can approve and finalize cases
```

---

## 🎓 Learning Path

**For Users** (1-2 hours)
1. PROJECT_SUMMARY.md
2. QUICKSTART.md
3. Try creating a case
4. Review sample outputs

**For Developers** (4-6 hours)
1. PROJECT_SUMMARY.md
2. QUICKSTART.md & run system
3. ARCHITECTURE.md - Full read
4. Explore backend/agents/
5. Try modifying an agent prompt

**For DevOps** (2-4 hours)
1. PROJECT_SUMMARY.md
2. README.md & ARCHITECTURE.md
3. CONFIG.md - Full read
4. Plan cloud deployment

---

## 📞 Next Steps

### Now:
1. Read PROJECT_SUMMARY.md (5 min)
2. Follow QUICKSTART.md (10 min)
3. Run the system locally

### Today:
1. Create a promotion case
2. Watch the 6-agent workflow
3. Review the executive report

### This Week:
1. Customize agent logic for your needs
2. Connect to your data sources
3. Plan production deployment

### This Month:
1. Deploy to cloud
2. Integrate with leadership workflows
3. Train your team

---

**🎉 You're all set! Start with [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) →**

---

## File Directory Tree

```
FMCG/
├── PROJECT_SUMMARY.md          ← START HERE
├── QUICKSTART.md               ← Then this
├── README.md                   ← Reference guide
├── ARCHITECTURE.md             ← Technical deep-dive
├── CONFIG.md                   ← Configuration options
├── setup.sh                    ← Auto setup (Mac/Linux)
├── setup.bat                   ← Auto setup (Windows)
├── .gitignore
│
├── backend/                    🔧 FastAPI Backend
│   ├── main.py                 ← Main app
│   ├── models.py               ← Database models
│   ├── setup.py                ← Database init
│   ├── requirements.txt        ← Python deps
│   ├── .env.example            ← Config template
│   ├── sample_data.py          ← Sample cases
│   ├── agents/                 🧠 AI Agents
│   │   ├── agent_1_intent.py
│   │   ├── agent_2_concentration.py
│   │   ├── agent_3_margin.py
│   │   ├── agent_4_demand.py
│   │   ├── agent_5_governance.py
│   │   └── agent_6_brain.py
│   ├── schemas/                📋 Data Schemas
│   │   └── schemas.py
│   └── orchestrator/           🎼 Orchestration
│       └── orchestrator.py
│
└── frontend/                   💻 React Frontend
    ├── package.json            ← NPM config
    ├── vite.config.js          ← Build config
    ├── tailwind.config.js      ← Tailwind config
    ├── postcss.config.js       ← PostCSS config
    ├── index.html              ← HTML entry
    └── src/
        ├── main.jsx            ← React entry
        ├── App.jsx             ← Main component
        ├── index.css           ← Global styles
        ├── pages/              📄 Pages
        │   ├── Dashboard.jsx   ← Case list
        │   ├── NewCase.jsx     ← Case form
        │   └── CaseDetail.jsx  ← Case detail
        ├── components/         🎨 Components
        │   ├── Navigation.jsx
        │   └── Badges.jsx
        └── hooks/              🪝 API Hooks
            └── useAPI.js
```

---

**Ready? Let's go! → [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**
