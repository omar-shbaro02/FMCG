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
| 4 | Dataset upload | IN PROGRESS | Implementing safe CSV/XLSX storage, metadata, and audit events. |
| 5 | Data validation engine | BLOCKED | Not implemented. |
| 6 | Demo data generator | BLOCKED | Required deterministic scenarios absent. |
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
