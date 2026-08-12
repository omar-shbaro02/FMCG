# Ordered implementation backlog

This backlog is derived from the complete standalone build brief. Tasks must be
completed in order. Each task is closed only after its acceptance criteria pass
and its completion record is added to `TASK_LOG.md`.

## Delivery protocol

At the end of every task:

1. Run relevant tests.
2. Record completed work and changed files.
3. Record unresolved assumptions.
4. Confirm the frozen product boundaries remain preserved.
5. Do not start the next task when acceptance criteria fail.

Human gates at Tasks 0, 12, 15, and 29 require explicit Kamal approval.

## Backlog

- [x] **Task 0 — Freeze project contract** (`APPROVED_BY_PROJECT_LEAD`)
  - [x] Freeze product canon, buyer, decision, wedge, and boundaries.
  - [x] Freeze primary forecast target and horizon.
  - [x] Freeze executive output contract and review gates.
  - [x] Verify FMCG-only scope and absence of strategy drift.
  - [x] Obtain explicit approval from the project lead acting as approval owner.
- [x] **Task 1 — Initialize repository**
  - Create the prescribed repository structure, Next.js frontend, FastAPI
    backend, Docker Compose environment, lint/format/type/test tooling, and CI.
  - Verify clean install; frontend, API, and database startup; test execution.
- [x] **Task 2 — Authentication and roles**
  - Implement users, secure authentication, RBAC, protected routes, and audit
    actor attribution.
  - Test unauthorized rejection and Commercial Director/reviewer permissions.
- [x] **Task 3 — Database and migrations**
  - Implement all core tables, UUID keys, UTC timestamps, enums, references,
    grain constraints, and fixed-precision financial types.
  - Test clean upgrade and development downgrade.
- [x] **Task 4 — Dataset upload**
  - Implement safe CSV/XLSX upload, local/S3-compatible storage boundary,
    metadata, ingestion job, duplicate behavior, and upload audit.
- [x] **Task 5 — Data validation engine**
  - Implement schema, type, grain, missing-week, duplicate, range, chronology,
    transformation-log, distortion, and forecast-viability rules.
  - Ensure critical errors block analysis and no rows disappear silently.
- [x] **Task 6 — Demo data generator**
  - Add deterministic synthetic fixtures for healthy growth, temporary uplift,
    pull-forward, loading, discount dependency, cannibalization, margin risk,
    and insufficient evidence; document scenario truth.
- [x] **Task 7 — Case management**
  - Implement create/update/list/view, scope, promotion window, legal status
    transitions, series-grain enforcement, and readiness validation.
- [x] **Task 8 — Baseline engine**
  - Implement explicit configurable baselines, stored assumptions/exclusions,
    out-of-stock and promotion-contamination notes, and unit tests.
- [x] **Task 9 — Forecast Adapter interface**
  - Implement typed contracts, abstract adapter, registry, deterministic mock,
    output validation, and implementation-substitution contract tests.
- [ ] **Task 10 — TimesFM adapter** (`IN_PROGRESS`)
  - Isolate TimesFM imports/configuration inside the adapter; support the
    primary target, 4–8 week horizon, structured errors, metadata, latency,
    and explicit non-production fallback behavior.
- [ ] **Task 11 — Forecast evidence derivation**
  - Deterministically derive direction, baseline comparison, retention, decay,
    uncertainty, and supported sell-in/sell-out divergence with traceability.
- [ ] **Task 12 — Kamal forecast-adapter review gate**
  - Present sample inputs/outputs, failure and uncertainty cases, and adapter
    replacement proof; obtain approval before Task 13.
- [ ] **Task 13 — FMCG interpretation engine**
  - Implement deterministic synthesis plus a controlled, schema-validated LLM
    gateway with evidence references, bounded retries, and explicit uncertainty.
- [ ] **Task 14 — Growth-quality classifier**
  - Implement/version all ten classes, primary/secondary outcomes, confidence,
    separate priority logic, exclusions, and fixture expectations.
- [ ] **Task 15 — Kamal commercial-realism review gate**
  - Review the seven required commercial patterns and obtain approval.
- [ ] **Task 16 — Investigation planner**
  - Generate precise questions, evidence, gaps, owner, affected decision,
    early-action risk, urgency, and confidence; reject vague language.
- [ ] **Task 17 — Decision simulation engine**
  - Compare all seven approved options neutrally without selecting, optimizing,
    recommending, or executing one; require human review.
- [ ] **Task 18 — Executive output generator**
  - Generate the frozen 12-section structured/rendered output with approved
    language, owner, confidence, and mandatory human-review statement.
- [ ] **Task 19 — Frontend workflow**
  - Build only the 11 workflow pages in the brief; make evidence, draft status,
    and uncertainty clear; provide no execution controls or generic dashboard.
- [ ] **Task 20 — Human review and feedback**
  - Add evidence, validation/correction/rejection, separate feedback, original
    output preservation, and audited human attribution.
- [ ] **Task 21 — Exports**
  - Produce access-controlled PDF, Markdown, and JSON exports whose content and
    draft/review labels match the stored output.
- [ ] **Task 22 — Audit and admin health**
  - Audit all material transitions and expose admin-only jobs, system health,
    prompt/classifier/adapter versions without secrets.
- [ ] **Task 23 — Security hardening**
  - Run dependency, authorization, upload, injection, prompt-injection, leakage,
    rate-limit, cross-case access, and secret scans; document residual risk.
- [ ] **Task 24 — Performance and reliability**
  - Test size/concurrency limits, idempotent retries, timeouts, indexes, exports,
    unavailable models, recoverability, observability, and truthful UI status.
- [ ] **Task 25 — End-to-end scenario testing**
  - Verify scenarios A–I against documented truth, correct human ownership,
    honest insufficiency, neutral simulations, and absence of autonomous action.
- [ ] **Task 26 — Custom GPT creation**
  - Configure the six specified design/review workspaces and test in-scope,
    boundary, insufficiency, misleading forecast, action, and certainty cases.
  - These are not runtime infrastructure or autonomous agents.
- [ ] **Task 27 — Documentation**
  - Complete setup, architecture, data/API/adapter/prompt/testing/security/
    deployment guides, backup/restore, runbook, and limitations; dry-run setup.
- [ ] **Task 28 — Deployment package**
  - Add production containers, migration/worker startup, health checks, proxy
    example, environment checklist, backup/restore scripts, release checklist,
    smoke test, and rollback documentation.
- [ ] **Task 29 — Final Kamal review gate**
  - Present three source scenarios and a full auditable human-reviewed journey;
    answer all ten pilot-readiness questions and obtain approval.

## Definition of done

The project is complete only when every task and human gate above is closed and
the full definition of done in the build brief is satisfied. In particular,
TimesFM stays replaceable, simulations stay non-executable, every final output
requires human review, and the product never becomes forecasting software.
