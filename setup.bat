@echo off
REM FMCG Trade Promotion Intelligence - Setup Script for Windows

echo.
echo ================================================
echo FMCG Trade Promotion Intelligence - Setup
echo ================================================
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3 is required but not installed.
    exit /b 1
)
python --version

REM Check Node
echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is required but not installed.
    exit /b 1
)
node --version

REM Backend setup
echo.
echo Setting up backend...
cd backend

if not exist "venv" (
    python -m venv venv
    echo Created virtual environment
)

call venv\Scripts\activate.bat
pip install -q -r requirements.txt
echo Installed Python dependencies

if not exist ".env" (
    copy .env.example .env
    echo Created .env file
    echo.
    echo IMPORTANT: Edit backend\.env and add your OpenAI API key
    echo Then run: python setup.py
    echo.
)

cd ..

REM Root npm setup (for concurrently)
echo.
echo Setting up root npm (concurrently)...
if not exist "node_modules" (
    npm install -q
    echo Installed root npm dependencies
)

REM Frontend setup
echo.
echo Setting up frontend...
cd frontend

if not exist "node_modules" (
    npm install -q
    echo Installed frontend npm dependencies
)

cd ..

echo.
echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo Next steps:
echo.
echo 1. Edit backend\.env with your OpenAI API key
echo.
echo 2. Initialize database:
echo    python backend\setup.py
echo.
echo 3. Start both backend and frontend (from FMCG directory):
echo    npm run dev
echo.
echo    (or run them separately:)
echo    npm run dev:backend    (Terminal 1)
echo    npm run dev:frontend   (Terminal 2)
echo.
echo 4. Open: http://localhost:5173
echo.
echo ================================================
echo.
pause
