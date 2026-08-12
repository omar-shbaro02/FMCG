# Legion Development Handoff

Last updated: 2026-08-10  
Repository branch: `main`  
Last committed revision: `6cdf75e Initial commit`  
Current implementation phase: Task 12 — Forecast Adapter Review Gate

## Read this first

The work described here is currently **uncommitted** on the original laptop. The Legion will not receive it by cloning or pulling until these changes are committed and pushed from the original laptop, or the working directory is transferred directly.

Before switching machines:

```bash
git status --short
git add -A
git commit -m "Rebuild foundation through dataset upload"
git push origin main
```

Review the diff before committing. Do not commit `.env`, `.venv`, `node_modules`, `.next`, uploaded datasets, or generated database files; these are ignored.

## Authoritative project documents

Read these in order on the Legion:

1. `docs/product-canon.md` — approved product contract and non-negotiable boundaries.
2. `IMPLEMENTATION_TASKS.md` — Tasks 0–29, status, acceptance evidence, and completion records.
3. `LEGION_HANDOFF.md` — this operational continuation guide.
4. The original complete build brief supplied outside the repository, if available.

The approved product is **VAI FMCG Forecast-Augmented Growth Quality Diagnostic**. The legacy six-agent “Trade Promotion Distortion Intelligence” prototype is not the target product.

## Frozen boundaries

- FMCG only.
- Primary buyer and final reviewer: FMCG Commercial Director.
- Core question: which apparently positive FMCG growth signal should leadership investigate before treating it as healthy growth?
- TimesFM predicts movement; VAI interprets growth quality; humans validate and decide.
- No autonomous agents, optimization, automatic recommendations, or commercial execution.
- Forecast logic must remain behind a replaceable `ForecastAdapter`.
- Every final output requires explicit human review.

## Completed work

### Task 0 — Product contract: COMPLETE

- Product canon, buyer, exact decision, wedge, boundaries, primary forecast target, output contract, human owners, architecture constraints, and review gates are frozen.
- Project owner approved the gate on 2026-08-10.

Primary artifact: `docs/product-canon.md`.

### Task 1 — Repository initialization: COMPLETE

- Next.js 14, React, TypeScript, Tailwind, ESLint, strict TypeScript, and Vitest frontend foundation.
- FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL, Redis, Ruff, strict MyPy, and Pytest backend foundation.
- Multi-stage non-root Docker images.
- Docker Compose services for frontend, API, worker placeholder, PostgreSQL, and Redis.
- Makefile and GitHub Actions CI.
- `.env.example` and scoped Docker ignore files.
- Legacy Vite UI files were removed from the runnable application.

Verified before handoff:

- Frontend production build passed.
- Frontend lint, type checking, and one Vitest test passed.
- Backend lint, strict typing, and tests passed.
- PostgreSQL, Redis, API, and frontend containers started successfully.
- API returned healthy status on port 8000.
- Frontend returned HTTP 200 on port 3000.

### Task 2 — Authentication and roles: COMPLETE

- Argon2 password hashing.
- Bounded HS256 bearer tokens.
- Inactive-user rejection.
- Persisted PostgreSQL user repository.
- All frozen roles and reusable RBAC guards.
- Protected authentication, admin, and reviewer access routes.
- Configured development bootstrap administrator.

Development-only credentials come from local environment variables. Defaults are:

```text
email: admin@example.com
password: development-admin-only
```

These must never be used in production.

### Task 3 — Database and migrations: COMPLETE

- All 15 required tables are modeled with UUID keys and timezone-aware timestamps.
- Financial and rate values use fixed-precision `NUMERIC`, not floating point.
- Weekly grain uniqueness is enforced for `week_start_date + sku_id + channel + region`.
- Foreign keys and useful indexes are present.
- Initial Alembic migration is in `backend/alembic/versions/`.
- API startup runs `alembic upgrade head` before Uvicorn.

Migration verification passed against PostgreSQL:

1. Upgrade from empty database to head.
2. Downgrade from head to base.
3. Re-upgrade from base to head.
4. `alembic check` reported no schema drift.

### Task 4 — Dataset upload: IN PROGRESS

Implemented:

- Admin-only multipart upload endpoint: `POST /api/datasets`.
- CSV and XLSX extension/MIME allowlists.
- Simple-filename enforcement against traversal and absolute paths.
- Configurable upload-size limit.
- UTF-8 CSV and real XLSX content checks.
- SHA-256 content-addressed local storage.
- Explicit HTTP 409 behavior for exact duplicate content.
- Dataset metadata record and `DATASET_UPLOADED` audit event in one database transaction.
- Unit tests for safe storage, traversal, MIME mismatch, oversized data, and duplicates.
- Persistent Compose upload volume was added.

Current test state: **15 backend tests pass**.

## Exact stopping point

Tasks 4–11 are complete. Task 12 is a mandatory project-lead review gate; the
packet is `docs/forecast-adapter-review.md`. Do not begin Task 13 without approval.

## First actions on the Legion

### 1. Install prerequisites

- Git
- Docker Desktop with Docker Compose
- Node.js 24 and npm 11+
- Python 3.12

On Windows, run commands from PowerShell, Git Bash, or WSL. Docker Desktop must be running with Linux containers enabled.

### 2. Pull the handoff commit

```bash
git clone <repository-url>
cd fmcg-trade-promotion-distortion-intelligence
```

If already cloned:

```bash
git switch main
git pull --ff-only origin main
```

Confirm `LEGION_HANDOFF.md` exists. If it does not, the original laptop changes were not pushed.

### 3. Create local environment configuration

PowerShell:

```powershell
Copy-Item .env.example .env
```

Git Bash / WSL:

```bash
cp .env.example .env
```

Keep `FORECAST_ADAPTER=mock` until the TimesFM task. Replace `SECRET_KEY` and the bootstrap password before any shared deployment.

### 4. Install local development dependencies

PowerShell:

```powershell
npm ci
npm --prefix frontend ci
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -e ".\backend[dev]"
```

Git Bash / WSL:

```bash
npm ci
npm --prefix frontend ci
python3 -m venv .venv
.venv/bin/pip install -e './backend[dev]'
```

### 5. Build the corrected containers

```bash
docker compose down
docker compose up -d --build database redis api frontend
docker compose ps
```

Expected:

- `database`: healthy
- `redis`: healthy
- `api`: healthy
- `frontend`: running

Verify:

```bash
curl http://localhost:8000/health
curl -I http://localhost:3000
```

### 6. Re-run automated checks

PowerShell backend:

```powershell
Set-Location backend
$env:DATABASE_URL = "postgresql+psycopg://fmcg:fmcg@localhost:5432/fmcg"
..\.venv\Scripts\ruff check app tests
..\.venv\Scripts\mypy app
..\.venv\Scripts\pytest
Set-Location ..
```

Git Bash / WSL backend:

```bash
cd backend
DATABASE_URL='postgresql+psycopg://fmcg:fmcg@localhost:5432/fmcg' ../.venv/bin/ruff check app tests
DATABASE_URL='postgresql+psycopg://fmcg:fmcg@localhost:5432/fmcg' ../.venv/bin/mypy app
DATABASE_URL='postgresql+psycopg://fmcg:fmcg@localhost:5432/fmcg' ../.venv/bin/pytest
cd ..
```

Frontend:

```bash
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend test
npm --prefix frontend run build
```

### 7. Complete the Task 4 smoke test

Use the tracked `fixtures/upload_smoke.csv` file.

First sign in:

```http
POST http://localhost:8000/api/auth/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "development-admin-only"
}
```

Use the returned bearer token:

```http
POST http://localhost:8000/api/datasets
Authorization: Bearer <token>
Content-Type: multipart/form-data

name = Upload smoke test
file = fixtures/upload_smoke.csv (text/csv)
```

Acceptance expectations:

- First upload returns HTTP 201 and dataset metadata.
- Database contains one corresponding `datasets` row.
- Database contains one `DATASET_UPLOADED` audit event.
- Re-uploading identical content returns HTTP 409.
- Uploaded file exists in the `uploads_data` volume.
- API remains healthy.

Useful checks:

```bash
docker compose exec database psql -U fmcg -d fmcg -c "select id,name,original_filename,upload_status from datasets order by created_at desc limit 5;"
docker compose exec database psql -U fmcg -d fmcg -c "select event_type,entity_type,entity_id from audit_events order by created_at desc limit 5;"
docker compose exec api ls -la /app/var/uploads
```

When these pass, change Task 4 to `COMPLETE` in `IMPLEMENTATION_TASKS.md` and append its completion record.

## Next implementation task

Review **Task 12 — Forecast Adapter** using `docs/forecast-adapter-review.md`.
Confirm the input/output structure, evidence usability, uncertainty honesty,
failure behavior, and adapter replaceability before approving Task 13.

## Known issues and deferred work

- Frontend dependency audit previously reported 14 findings: 5 moderate, 8 high, and 1 critical. Resolve during Task 23 or sooner if an upgrade is non-breaking. Do not run `npm audit fix --force` blindly.
- Next.js is currently 14.2.35. Framework upgrades require full lint/type/test/build verification.
- Pytest emits a Starlette warning about `httpx`/`TestClient`; tests still pass.
- The Compose `worker` is intentionally a placeholder and exits until bounded job processing is implemented.
- TimesFM is not implemented. `FORECAST_ADAPTER=mock` is the only valid current setting.
- Ingestion of validated rows into `weekly_fmcg_sales` is deferred to the case/data
  workflow; validation itself is complete.
- The frontend currently contains only the compliant product landing foundation, not the full workflow.
- The legacy top-level documentation files still describe the old prototype and must be rewritten during documentation work. Treat `docs/product-canon.md` and `IMPLEMENTATION_TASKS.md` as authoritative.
- Uploaded local files use a named Docker volume and are not transferred through Git.

## Current repository-change summary

The working tree intentionally contains a broad replacement of the legacy prototype:

- Modified root package/tooling files.
- Deleted legacy Vite frontend and legacy backend setup hook.
- Added Next.js application foundation.
- Added modular FastAPI application.
- Added PostgreSQL models and Alembic migration.
- Added authentication/RBAC and dataset-upload modules.
- Added Docker/Compose, CI, tests, product canon, and task register.

Do not discard these changes with `git reset --hard` or checkout commands.

## Handoff definition

The Legion continuation point is:

> Obtain explicit Task 12 approval, record it, then start Task 13 interpretation.
