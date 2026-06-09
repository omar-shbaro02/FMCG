# FMCG Trade Promotion Distortion Intelligence - Quick Start Guide

## 🚀 5-Minute Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- OpenAI API key (GPT-4 recommended)

### Step 1: Get API Key
```
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Keep it safe - you'll need it in a moment
```

### Step 2: Automated Setup

From the FMCG directory:

**Mac/Linux:**
```bash
bash setup.sh
```

**Windows:**
```bash
setup.bat
```

This will:
- ✅ Check Python and Node.js
- ✅ Create Python virtual environment
- ✅ Install all Python dependencies
- ✅ Install all Node.js dependencies
- ✅ Create backend/.env file

### Step 3: Configure API Key

Edit `backend/.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4o
```

### Step 4: Initialize Database

```bash
python backend/setup.py
```

This will:
- Create the SQLite database
- Load 4 sample promotion cases
- Display success message

### Step 5: Run Everything

From the FMCG directory:

```bash
npm run dev
```

You should see output like:
```
> npm run dev

concurrently "npm run dev:backend" "npm run dev:frontend"

[0] INFO:     Started server process
[0] INFO:     Uvicorn running on http://0.0.0.0:8000
[1] ➜  Local:   http://localhost:5173/
[1] ➜  press h to show help
```

**Both servers are now running!**

### Step 6: Open Application

Go to: **http://localhost:5173**

You should see the Dashboard with sample cases.

## 🧪 Test the System

1. **View Dashboard**
   - See 4 sample promotion cases
   - Each representing different health profiles

2. **Create New Case**
   - Click "New Case"
   - Fill in the form with promotion data
   - Click "Create Case & Start Analysis"

3. **Watch Analysis Unfold**
   - Case status changes to "Analyzing"
   - Agents execute sequentially
   - Watch confidence scores update

4. **Review Results**
   - View each agent's analysis
   - See final Executive Judgment
   - Review "What Leadership Should NOT Assume"

5. **Approve Case**
   - Switch to "Human Review" tab
   - Optionally add notes
   - Click "Approve & Finalize Case"

## ⚡ Alternative: Run Separately

If you prefer running backend and frontend in separate terminals:

**Terminal 1 - Backend:**
```bash
npm run dev:backend
```

**Terminal 2 - Frontend:**
```bash
npm run dev:frontend
```

## 📊 Sample Cases Included

The system comes with 4 sample cases:

1. **PROMO-2024-Q1-HEALTHY**
   - Growth Health: HEALTHY ✓
   - Well-distributed, sustainable growth

2. **PROMO-2024-Q1-FRAGILE**
   - Growth Health: FRAGILE ⚠
   - High dependency risk, post-promo decline

3. **PROMO-2024-Q1-DISTORTIONARY**
   - Growth Health: DISTORTIONARY ✗
   - Classic trade loading scenario

4. **PROMO-2024-Q1-MISLEADING**
   - Growth Health: MISLEADING ✗
   - Leadership is being misled by inflated numbers

## 🔧 Troubleshooting

### "Port already in use"
```bash
# Kill process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Kill process on port 5173
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### "OpenAI API Error"
- Check your API key is correct
- Verify account has credits
- Check model name is set correctly

### "Database already exists"
```bash
cd backend
rm fmcg_cases.db
python setup.py
```

### "Module not found"
```bash
cd backend
pip install -r requirements.txt
```

## 📚 API Documentation

Once backend is running, visit: **http://localhost:8000/docs**

This shows all available endpoints with interactive testing.

## 🎯 Next Steps

1. **Customize Agent Logic**
   - Edit `/backend/agents/agent_*.py` files
   - Modify prompts to adjust decision criteria

2. **Connect to Your Data**
   - Add authentication to `/backend/main.py`
   - Connect to your data sources
   - Replace sample data

3. **Deploy to Production**
   - Use Docker for containerization
   - Deploy backend to cloud (AWS, GCP, Azure)
   - Deploy frontend to CDN (Vercel, Netlify)
   - Use cloud database (RDS, Cloud SQL)

## 📖 Documentation

Full documentation available in [README.md](../README.md)

## ✅ System Ready!

Your FMCG Trade Promotion Intelligence system is now running.

Start analyzing promotions to determine if growth is:
- **HEALTHY** (real, sustainable demand)
- **FRAGILE** (dependent on promotion mechanics)
- **DISTORTIONARY** (trade loading, concentration)
- **MISLEADING** (leadership is being misled)

---

Questions? Issues? See the main README.md for comprehensive documentation.
