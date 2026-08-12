# Implementation Task Register

This register follows the supplied build brief in order. A task is complete only after its acceptance criteria and relevant tests pass. Existing files are evidence of prior work, not proof of completion.

Machine-transfer and exact continuation instructions are maintained in `LEGION_HANDOFF.md`.

## Current baseline audit

- Repository: clean `main` branch tracking `origin/main` before this audit.
- Existing product: a six-agent “Trade Promotion Distortion Intelligence” prototype.
- Contract fit: noncompliant. It uses autonomous-style sequential agents, the wrong product name and classifications, direct recommendations, SQLite, a Vite JavaScript frontend, and no forecast adapter or TimesFM integration.
- Frontend: production build passes after installing dependencies with `npm ci`.
- Backend: Python source compiles, but clean startup is not yet verified because dependencies are absent from the current Python environment.
- Tests: no backend, frontend unit, contract, integration, security, or end-to-end suites are present.
- Security baseline: npm reports eight known vulnerabilities, including five high-severity findings.
- GitHub CI, Docker Compose, migrations, PostgreSQL, Redis worker, authentication, RBAC, uploads, exports, and required operational documentation are absent.

## Ordered tasks

| Task | Title | Status | Gate / current finding |
|---:|---|---|---|
| 0 | Freeze project contract | COMPLETE | Approved by the project owner on 2026-08-10. |
| 1 | Initialize repository | COMPLETE | Full Compose stack and local checks pass on 2026-08-10. |
| 2 | Authentication and roles | COMPLETE | Signed authentication and RBAC pass 6 backend tests. |
| 3 | Database and migrations | COMPLETE | PostgreSQL migration upgrade/downgrade/reapply and schema-drift checks pass. |
| 4 | Dataset upload | COMPLETE | Non-root container upload, persistence, audit, volume, and duplicate smoke checks pass. |
| 5 | Data validation engine | COMPLETE | Structured CSV/XLSX validation, persistence, audit, and 20-test suite pass. |
| 6 | Demo data generator | COMPLETE | Eight seeded synthetic scenarios and machine-readable truth pass tests. |
| 7 | Case management | BLOCKED | Legacy promotion cases do not meet the diagnostic contract. |
| 8 | Baseline engine | BLOCKED | Not implemented. |
| 9 | Forecast Adapter interface | BLOCKED | Not implemented. |
| 10 | TimesFM adapter | BLOCKED | Not implemented. |
| 11 | Forecast evidence derivation | BLOCKED | Not implemented. |
| 12 | Kamal review: Forecast Adapter | BLOCKED | Mandatory human gate. |
| 13 | FMCG interpretation engine | BLOCKED | Legacy agent output is noncompliant. |
| 14 | Growth-quality classifier | BLOCKED | Frozen classes and rules absent. |
| 15 | Kamal review: commercial realism | BLOCKED | Mandatory human gate. |
| 16 | Investigation planner | BLOCKED | Not implemented. |
| 17 | Decision simulation engine | BLOCKED | Not implemented. |
| 18 | Executive output generator | BLOCKED | Required output contract absent. |
| 19 | Frontend workflow | BLOCKED | Only three legacy pages exist. |
| 20 | Human review and feedback | BLOCKED | Partial legacy approval flow is not compliant or audited. |
| 21 | PDF, Markdown, JSON exports | BLOCKED | Not implemented. |
| 22 | Audit and admin health | BLOCKED | Legacy agent log is insufficient. |
| 23 | Security hardening | BLOCKED | Not started; dependency findings are open. |
| 24 | Performance and reliability | BLOCKED | Not started. |
| 25 | End-to-end scenario testing | BLOCKED | No required scenario suite. |
| 26 | Custom GPT creation | BLOCKED | External workspace configuration and tests required. |
| 27 | Documentation | BLOCKED | Existing docs describe the wrong product. |
| 28 | Deployment package | BLOCKED | Not implemented. |
| 29 | Final Kamal review | BLOCKED | Mandatory final human gate. |

## Task completion record template

For every task, append a dated record containing:

- Acceptance criteria and result.
- Tests run and exact result.
- Files changed.
- Unresolved assumptions.
- Boundary check: FMCG-only, diagnostic-only, no optimization, no execution, mandatory human review.

## Task 0 completion record

- Completed: frozen buyer, decision, wedge, boundaries, forecast target, output contract, owner model, architecture constraints, and review gates.
- Tests: document review against Sections 0–5, 11–19, 23, 29, and 31–32 of the supplied brief.
- Files changed: `docs/product-canon.md`, `IMPLEMENTATION_TASKS.md`.
- Unresolved assumptions: none; the project owner approved the gate.
- Boundary check: preserved; no domain functionality was added.
- Acceptance: passed by project-owner approval on 2026-08-10.

## Task 1 verification record — 2026-08-10

- Completed: required modular-monolith directories, Next.js/TypeScript frontend, FastAPI package, environment template, Dockerfiles, Docker Compose services, Makefile, linting, strict type checking, unit-test runners, and GitHub Actions CI.
- Passed: frontend ESLint, TypeScript, Vitest (1 test), and production build.
- Passed: backend Ruff, strict MyPy, Pytest (1 test), API health smoke coverage, and Python packaging install in a clean local virtual environment.
- Passed after installing a local Docker-compatible runtime: Compose configuration, PostgreSQL readiness, Redis `PONG`, API health, and frontend HTTP 200.
- Files changed: repository tooling, `frontend/`, `backend/app/`, `backend/tests/`, container definitions, CI, and environment template.
- Unresolved assumptions: none for Task 1.
- Boundary check: preserved; the legacy autonomous-agent frontend was removed from the runnable application and no commercial action capability was added.
- Acceptance: passed. All required services start and all Task 1 code checks pass.

## Task 2 completion record — 2026-08-10

- Completed: Argon2 password verification, bounded HS256 access tokens, inactive-user rejection, authenticated audit-actor identity, all frozen roles, reusable role guards, protected routes, and development bootstrap administrator configuration.
- Tests: Ruff and strict MyPy pass; Pytest passes 6 tests covering missing authentication, invalid credentials, admin-only authorization, Commercial Director access, and reviewer access.
- Files changed: auth domain/schema/repository/security/API modules, application wiring, settings, dependencies, and auth tests.
- Unresolved assumption: the temporary development repository is replaced by PostgreSQL persistence in Task 3; no production deployment may use the bootstrap password.
- Boundary check: preserved; authentication grants diagnostic access only and adds no autonomous or commercial action.
- Acceptance: passed.

## Task 3 completion record — 2026-08-10

- Completed: all 15 required core tables, frozen enums, UUID keys, UTC-aware timestamps, fixed-precision financial fields, foreign keys, series-grain uniqueness, indexes, SQL-backed user authentication, bootstrap development admin, and Alembic configuration.
- Tests: metadata tests confirm all tables, unique series grain, and fixed-precision money; PostgreSQL migration upgraded from base, downgraded to base, upgraded again, and `alembic check` reported no drift; Ruff, strict MyPy, and 9 Pytest tests pass.
- Files changed: database configuration, persistence entities/repository, Alembic environment and migration, container migration startup, Compose database port, schema tests.
- Unresolved assumptions: none for the frozen core schema; later tasks may add backward-compatible fields through new migrations.
- Boundary check: preserved; persistence records evidence and human decisions only.
- Acceptance: passed.

## Task 4 completion record — 2026-08-12

- Completed: safe admin-only CSV/XLSX upload, extension/MIME/content validation,
  configurable size limit, simple-filename enforcement, SHA-256 content-addressed
  storage, explicit duplicate rejection, metadata persistence, upload audit, and a
  persistent non-root upload volume.
- Tests: upload/storage unit tests pass within the 20-test backend suite. A rebuilt
  Python 3.12 non-root API container returned HTTP 201 for the first upload and
  HTTP 409 for identical content; PostgreSQL contained one dataset and one upload
  audit event; the uploaded file was owned and readable by `appuser`; API health
  remained green.
- Files: dataset upload API/service/schema/tests, API container, Compose upload
  volume, settings, and smoke fixture.
- Unresolved assumptions: malware scanning remains an explicit integration point
  for security hardening; local storage is the development implementation.
- Boundary check: preserved; upload stores FMCG diagnostic evidence only.
- Acceptance: passed.

## Task 5 completion record — 2026-08-12

- Completed: identical CSV/XLSX validation contract; required schema, missing
  values, strict dates, chronology, numeric/boolean/range checks, exact series
  grain duplicates, discount-scale normalization/mixing rejection, currency,
  stock-unit and gross-margin declarations, missing weeks, configurable history
  and promotion viability, forecast eligible/ineligible series, out-of-stock,
  returns and sell-in/sell-out distortion notes, transformation log, explicit
  valid/rejected counts, persisted issues/summary, validation audit, and protected
  POST/GET report endpoints.
- Tests: Ruff, Ruff format, and strict MyPy pass; Pytest passes 20 tests. API smoke
  validation returned `VALID_WITH_WARNINGS`, persisted status/dates/row count and
  issue/audit records, and the stored report round-tripped through the GET API.
- Files: data-quality domain, dataset request/response schemas and API, settings,
  `.env.example`, tests, task documentation, and local-tool ignore rule.
- Unresolved assumptions: safe default minimum history is 12 weekly observations;
  deployment may configure 4–104. Discount percentages above 1 are normalized to
  fractions; mixed scales are critical. Currency uses a required 3-letter code.
- Boundary check: preserved; validation surfaces uncertainty and distortion but
  makes no commercial classification or action.
- Acceptance: passed. Critical errors yield `INVALID`; warnings remain visible as
  `VALID_WITH_WARNINGS`; no invalid row is silently discarded.

## Task 6 completion record — 2026-08-12

- Completed: deterministic generator and synthetic weekly datasets for healthy
  growth, temporary uplift, pull-forward, loading risk, discount dependency,
  cannibalization, margin/value-quality risk, and insufficient evidence. Every
  scenario has a fixed seed and machine-readable truth containing the expected
  later-stage class, priority, confidence, grain, and commercial rationale.
- Tests: generation is byte-for-byte deterministic; all eight scenarios pass the
  Task 5 schema without critical errors; supported scenarios meet viability and
  insufficient evidence remains explicitly ineligible. Ruff, format, strict
  MyPy, and all 22 backend tests pass on Python 3.12 with PostgreSQL.
- Files: `scripts/seed_demo_data.py`, scenario CSV/truth fixtures,
  `fixtures/README.md`, and demo-data tests.
- Unresolved assumptions: synthetic currency is USD, stock is units, and gross
  margin is an amount. Later classifier thresholds must be versioned and tested
  against, but must never read, the truth labels at runtime.
- Boundary check: preserved; fixtures model only frozen FMCG diagnostic evidence,
  contain no real client data, and execute no action.
- Acceptance: passed.
