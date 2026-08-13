#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$project_dir"

command -v python3 >/dev/null || { echo "Python 3.11-3.13 is required." >&2; exit 1; }
command -v node >/dev/null || { echo "Node.js 24 or newer is required." >&2; exit 1; }
command -v npm >/dev/null || { echo "npm 10 or newer is required." >&2; exit 1; }

python3 - <<'PY'
import sys
if not ((3, 11) <= sys.version_info[:2] < (3, 14)):
    raise SystemExit(
        f"Python 3.11-3.13 is required; found {sys.version_info.major}.{sys.version_info.minor}."
    )
PY

node -e 'const major=Number(process.versions.node.split(".")[0]); if (major < 24) { console.error(`Node.js 24 or newer is required; found ${process.versions.node}.`); process.exit(1) }'

python3 -m venv --clear .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e './backend[dev]'
npm ci
npm --prefix frontend ci

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env. Replace development secrets before shared or production use."
fi

echo "Setup complete. Run 'source .venv/bin/activate && make check'."
echo "For the full stack, run 'docker compose up --build' and open http://localhost:3000."
