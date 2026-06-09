#!/bin/bash
# FMCG Trade Promotion Intelligence - Setup Script for macOS/Linux

echo ""
echo "================================================"
echo "FMCG Trade Promotion Intelligence - Setup"
echo "================================================"
echo ""

# Check Python
echo "🔍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is required but not installed."
    exit 1
fi
python3 --version

# Check Node
echo "🔍 Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "✗ Node.js is required but not installed."
    exit 1
fi
node --version

# Backend setup
echo ""
echo "🔧 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Created virtual environment"
fi

source venv/bin/activate
pip install -q -r requirements.txt
echo "✓ Installed Python dependencies"

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠ IMPORTANT: Edit backend/.env and add your OpenAI API key"
    echo "   Then run: python setup.py"
    echo ""
fi

# Root npm setup (for concurrently)
echo ""
echo "🔧 Setting up root npm (concurrently)..."
if [ ! -d "node_modules" ]; then
    npm install -q
    echo "✓ Installed root npm dependencies"
fi

cd ..

# Frontend setup
echo ""
echo "🔧 Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    npm install -q
    echo "✓ Installed frontend npm dependencies"
fi

cd ..

echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit backend/.env with your OpenAI API key"
echo ""
echo "2. Initialize database:"
echo "   python backend/setup.py"
echo ""
echo "3. Start both backend and frontend (from FMCG directory):"
echo "   npm run dev"
echo ""
echo "   (or run them separately:)"
echo "   npm run dev:backend    # Terminal 1"
echo "   npm run dev:frontend   # Terminal 2"
echo ""
echo "4. Open: http://localhost:5173"
echo ""
echo "================================================"
echo ""
