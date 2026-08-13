@echo off
setlocal
cd /d "%~dp0"

python --version >nul 2>&1 || (echo Python 3.11-3.13 is required. & exit /b 1)
node --version >nul 2>&1 || (echo Node.js 24 or newer is required. & exit /b 1)
npm --version >nul 2>&1 || (echo npm 10 or newer is required. & exit /b 1)

python -c "import sys; raise SystemExit(0 if (3,11) <= sys.version_info[:2] < (3,14) else 1)" || (echo Python 3.11-3.13 is required. & exit /b 1)
node -e "if(Number(process.versions.node.split('.')[0])<24)process.exit(1)" || (echo Node.js 24 or newer is required. & exit /b 1)

python -m venv --clear .venv || exit /b 1
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip || exit /b 1
python -m pip install -e ".\backend[dev]" || exit /b 1
call npm ci || exit /b 1
call npm --prefix frontend ci || exit /b 1

if not exist .env (
  copy .env.example .env >nul
  echo Created .env. Replace development secrets before shared or production use.
)

echo Setup complete. Run "call .venv\Scripts\activate.bat" and then "make check".
echo For the full stack, run "docker compose up --build" and open http://localhost:3000.
endlocal
