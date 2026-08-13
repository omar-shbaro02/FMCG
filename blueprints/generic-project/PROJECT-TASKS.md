# {{PROJECT_NAME}} — ordered implementation backlog

Source: `PROJECT-SPEC.md` and `PRODUCT-CANON.md`  
Rule: complete tasks in order; a checked box requires a `TASK-LOG.md` record.

## Delivery protocol

At the end of every task:

1. Verify every acceptance criterion.
2. Run proportionate automated and manual tests.
3. Record changed files and exact results.
4. Record unresolved assumptions and residual risk.
5. Confirm the product canon remains preserved.
6. Stop if acceptance fails or a human gate is pending.

## Ordered backlog

- [ ] **Task 0 — Freeze the project contract** (`HUMAN_GATE`)
  - Approve problem, outcome, users, buyer, exact decision, scope, boundaries,
    workflow, terminology, output contract, ownership, and definition of done.
- [ ] **Task 1 — Initialize the repository and toolchain**
  - Repository structure, supported runtimes, dependency locks, environment
    template, linting, formatting, typing, tests, CI, containers, health check.
- [ ] **Task 2 — Authentication, authorization, and ownership**
  - Identities, sessions/tokens, roles, permissions, tenant/record ownership,
    unauthorized tests, attributable actors, production credential policy.
- [ ] **Task 3 — Persistence schema and migrations**
  - Stable IDs, timestamps, enums, constraints, indexes, precision, relations,
    clean upgrade/downgrade, schema-drift check, backup compatibility.
- [ ] **Task 4 — Input ingestion**
  - Supported formats/APIs, size/type/path controls, storage boundary, duplicate
    behavior, metadata, idempotency, audit, and non-root persistence.
- [ ] **Task 5 — Input validation and data-quality engine**
  - Schema/type/range/grain/time/duplicate/completeness rules, visible warnings,
    blocking errors, transformation log, no silent record loss.
- [ ] **Task 6 — Deterministic fixtures and scenario truth**
  - Seeded synthetic happy, edge, risk, invalid, and insufficient scenarios with
    machine-readable expected outcomes that runtime code cannot read.
- [ ] **Task 7 — Core record/case/work-item management**
  - Create/read/update/list, scope, readiness, legal state transitions, access,
    pagination, idempotency, and audit.
- [ ] **Task 8 — Reference, baseline, or comparison engine**
  - Explicit methods, assumptions, exclusions, quality score, versioning,
    persistence, replacement behavior, and insufficiency handling.
- [ ] **Task 9 — External/provider adapter interface**
  - Typed provider-neutral request/response/error contracts, registry,
    deterministic mock, metadata, health, substitution tests.
- [ ] **Task 10 — Primary provider implementation**
  - Isolated SDK/imports, configuration, timeout, retries, normalization,
    provenance, structured failures, resource limits, no silent fallback.
- [ ] **Task 11 — Evidence/feature derivation**
  - Deterministic derived evidence with traceability, uncertainty, data-quality
    notes, persistence, versioning, and tests.
- [ ] **Task 12 — Provider/evidence review** (`HUMAN_GATE`)
  - Review representative inputs, outputs, uncertainties, failures, provenance,
    replacement proof, and downstream usability.
- [ ] **Task 13 — Interpretation or synthesis engine**
  - Separate facts from interpretation, cite supplied evidence, expose ambiguity,
    use bounded schema validation for any optional LLM component.
- [ ] **Task 14 — Classification/decision-rule engine**
  - Versioned frozen states/classes, primary and secondary results, separate
    confidence/priority, exclusions, contradictions, fixture expectations.
- [ ] **Task 15 — Domain realism review** (`HUMAN_GATE`)
  - Domain owner evaluates representative and adversarial scenarios before UI or
    workflow presentation locks in misleading behavior.
- [ ] **Task 16 — Investigation/follow-up planner**
  - Exact questions, why they matter, required/available/missing evidence, human
    owner, affected decision, urgency, confidence, early-action risk.
- [ ] **Task 17 — Neutral option/simulation engine**
  - Compare only approved options; show assumptions, evidence, benefits, risks,
    gaps, affected functions, and uncertainty; never silently select or execute.
- [ ] **Task 18 — Final output generator**
  - Frozen ordered output contract, draft status, traceability, uncertainty,
    ownership, exact review statement, structured and rendered forms.
- [ ] **Task 19 — End-user workflow**
  - Only approved pages/flows, responsive and accessible states, honest loading/
    error/empty status, no unauthorized or out-of-scope controls.
- [ ] **Task 20 — Human review, correction, and feedback**
  - Approve/correct/reject/request-evidence states, original preservation,
    attribution, comments, separate product feedback, immutable audit trail.
- [ ] **Task 21 — Exports and interoperability**
  - Access-controlled approved formats, stable schema/version, review labels,
    content parity, injection/escaping checks, round-trip tests.
- [ ] **Task 22 — Audit, administration, and health**
  - Material event audit, safe operational metadata, jobs/provider/version health,
    admin-only access, no secrets or sensitive payload leakage.
- [ ] **Task 23 — Security and privacy hardening**
  - Threat model, dependency/secret scans, authz, tenant isolation, uploads,
    injection, SSRF, rate limits, logging/privacy, production-default rejection.
- [ ] **Task 24 — Performance and reliability**
  - Representative size/concurrency tests, bounded retries/timeouts, indexes,
    idempotency, recovery, observability, dependency outage, truthful status.
- [ ] **Task 25 — End-to-end scenario verification**
  - Execute all specification scenarios through the real workflow and assert
    evidence, state, ownership, output, review, audit, and prohibited behavior.
- [ ] **Task 26 — Optional specialist review workspaces**
  - If useful, configure bounded read-only reviewers and test in-scope, drift,
    insufficient evidence, misleading evidence, forbidden action, false certainty.
- [ ] **Task 27 — Documentation and setup dry run**
  - README, architecture, data/API/provider/testing/security/deployment guides,
    limitations, runbook, backup/restore, clean-machine setup verification.
- [ ] **Task 28 — Deployment and rollback package**
  - Immutable builds, migrations, health checks, TLS/proxy example, environment
    checklist, smoke test, backup/restore scripts, release and rollback records.
- [ ] **Task 29 — Final pilot/production approval** (`HUMAN_GATE`)
  - Present representative source scenarios and a complete auditable journey;
    answer readiness questions, accept residual risks, record explicit approval.

## Definition of done

Every task and mandatory gate is complete; Must requirements and end-to-end
scenarios pass; security, operations, recovery, documentation, limitations, and
ownership are verified; the released product still matches the approved canon.

