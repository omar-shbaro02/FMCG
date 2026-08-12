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
| 7 | Case management | COMPLETE | Typed CRUD, readiness, transitions, authorization, audit, and tests pass. |
| 8 | Baseline engine | COMPLETE | Configurable traceable calculations, persistence, audit, and tests pass. |
| 9 | Forecast Adapter interface | COMPLETE | Strict contracts, registry, deterministic mock, and substitution boundary pass. |
| 10 | TimesFM adapter | COMPLETE | Current 2.5 API isolated; normalized inference and structured failures pass. |
| 11 | Forecast evidence derivation | COMPLETE | Deterministic evidence, persistence, API, audit, and tests pass. |
| 12 | Project-lead review: Forecast Adapter | COMPLETE | Approved by user direction to continue on 2026-08-12. |
| 13 | FMCG interpretation engine | COMPLETE | Deterministic synthesis and controlled LLM boundary pass. |
| 14 | Growth-quality classifier | COMPLETE | Versioned frozen classes, priority, exclusions, and fixtures pass. |
| 15 | Kamal review: commercial realism | AWAITING APPROVAL | Review packet ready; mandatory human gate. |
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

## Task 7 completion record — 2026-08-12

- Completed: typed create/update/list/view endpoints, pagination, draft-only edits,
  4–8 week horizon and promotion-window constraints, legal status-transition map,
  validated-dataset and selected-series eligibility checks, exact grain evidence,
  promoted-observation readiness, submit-to-ready flow, RBAC, and audited create,
  update, and submit events.
- Tests: Ruff, format, strict MyPy, and all 26 backend tests pass on Python 3.12
  with PostgreSQL. Tests cover CRUD/list, readiness, submit, invalid scope, horizon,
  promotion window, and illegal transitions.
- Files: case domain, typed schemas, API router/wiring, and case tests.
- Unresolved assumptions: reviewers do not own cases in the MVP; Admin and
  Commercial Director manage them, while reviewer assignment arrives with the
  investigation workflow. Case submission advances deterministically through
  `DATA_VALIDATION` to `READY_FOR_FORECAST` after readiness passes.
- Boundary check: preserved; cases select evidence scope and never initiate a
  forecast or commercial action automatically.
- Acceptance: passed.

## Task 8 completion record — 2026-08-12

- Completed: recent pre-promotion average, median, prior-year seasonal,
  model-supplied, and controlled-fallback baselines; chronological inputs;
  configurable recent window; promotion and out-of-stock exclusions; assumptions,
  input/output snapshots, exclusion reasons, distortion notes, quality score,
  persistence, API, RBAC, and audit.
- Tests: Ruff, format, strict MyPy, and all 30 backend tests pass. Unit tests cover
  average, median, fallback, seasonal insufficiency, model-value validation,
  distortion exclusion, and quality scoring; API test persists a six-week result.
- Files: baseline domain, schemas, API/wiring, tests, and task documentation.
- Unresolved assumptions: seasonal matching uses exact month/day in the prior
  year and refuses unsupported dates rather than fabricating history. The model
  method accepts only already-controlled numeric baseline output; forecasting is
  implemented separately.
- Boundary check: preserved; positive baseline movement is never labeled healthy.
- Acceptance: passed.

## Task 9 completion record — 2026-08-12

- Completed: abstract six-method `ForecastAdapter`, strict weekly sell-out request
  and normalized response contracts, frozen enums, finite values and valid
  intervals, chronological unique history, exact series/context grain, 4–8 week
  horizon, deterministic mock, explicit adapter registry, health/metadata, and
  structured adapter-error schema.
- Tests: Ruff, format, strict MyPy, and all 34 backend tests pass. Contract tests
  prove deterministic mock behavior and rejection of malformed/non-finite output,
  unknown fields, forbidden commercial recommendation fields, mismatched grain,
  nonchronological history, and silent TimesFM-to-mock fallback.
- Files: forecast adapter interface/schemas/mock/registry and contract tests.
- Unresolved assumptions: the mock uses a transparent recent-level and linear
  slope solely for deterministic development; its output is explicitly labeled
  non-commercial evidence.
- Boundary check: preserved; adapters output numeric evidence only, and strict
  schemas prohibit commercial classes, owners, priorities, or actions.
- Acceptance: passed.

## Task 10 completion record — 2026-08-12

- Completed: TimesFM 2.5 PyTorch adapter using the current official
  `TimesFM_2p5_200M_torch`/`ForecastConfig` API; lazy model loading; configurable
  model ID, context, horizon, batch, device metadata, timeout, and quantile bounds;
  provider-array normalization; finite/shape/interval validation; latency and
  model metadata; health check; and explicit unavailable, length, malformed,
  timeout, memory, model, and non-finite failure categories.
- Tests: all 38 backend tests plus lint/format/strict typing pass. TimesFM contract
  tests use provider-shaped point/quantile arrays and cover success, metadata,
  latency, context rejection, non-finite output, timeout, unavailable runtime,
  and registry selection without mock fallback.
- Files: TimesFM adapter/config/tests, registry, optional dependency group, and
  environment template.
- Unresolved assumptions: production installs `backend[timesfm]` and provisions
  the configured Hugging Face weights/cache. Model weights are external deployment
  data and are not downloaded into or committed with the application. The current
  confidence interval uses official q10/q90 indices (80% interval).
- Boundary check: preserved; TimesFM imports/provider fields remain inside the
  adapter package and it emits no commercial classification or action.
- Acceptance: passed at the replaceable adapter contract and inference boundary.

## Task 11 completion record — 2026-08-12

- Completed: deterministic direction, baseline comparison, post-promotion
  retention, decay, interval-width uncertainty, and sell-in/sell-out divergence;
  explicit insufficiency for missing/misaligned baselines; traceable numeric
  evidence keys; data-quality note preservation; forecast-run and evidence
  persistence; adapter/model/version/latency metadata; failure state; protected
  run/evidence APIs; case transition; and audit.
- Tests: lint, format, strict MyPy, and all 41 backend tests pass. Tests cover
  sustained/above-baseline, strong decline/decay, high uncertainty, loading
  divergence, insufficiency, and the full case → baseline → forecast run → stored
  evidence API path.
- Files: forecast-evidence domain/tests, forecast-run schemas/API/wiring, and case
  integration coverage.
- Unresolved assumptions: version-one deterministic thresholds are >5% for
  above/below baseline and direction, ≥10% for sustained retention, <85% for
  collapsed retention, and interval width ratios of 20%/50% for low/medium/high.
  These must receive commercial review and later be versioned with classifier
  rules; they do not constitute commercial classification.
- Boundary check: preserved; evidence describes numeric movement and uncertainty
  only. It does not recommend, prioritize, assign an owner, or execute.
- Acceptance: passed.

## Tasks 13–14 completion record — 2026-08-12

- Completed: deterministic FMCG interpretation with facts separated from
  candidate meaning, supporting/contradicting/missing evidence and uncertainty;
  strict controlled-LLM schemas, evidence-key validation, forbidden-action
  rejection and bounded retries; all ten frozen classifier labels; one primary
  and multiple secondary outcomes; explicit exclusions; separate confidence and
  priority; P1 convergence; auditable definitions/owners; and versioned rules.
- Tests: Ruff lint and format, strict MyPy, fresh Alembic migration, and all 55
  backend Pytest tests pass against PostgreSQL on Python 3.12.
- Files: interpretation domain/tests, controlled LLM boundary/tests,
  classification domain/tests, and commercial-realism review packet.
- Unresolved assumption: version-one ordering and P1 sensitivity require the
  mandatory Task 15 commercial review before investigation planning begins.
- Boundary check: preserved; LLM prose cannot set classification, the classifier
  cannot recommend or execute action, and every result remains subject to human
  review.
- Acceptance: implementation passed; Task 15 approval remains open.
