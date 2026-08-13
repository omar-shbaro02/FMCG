# Generic project delivery blueprint

This directory is a reusable, technology-neutral version of the delivery method
used to build the VAI FMCG project. It turns an idea into an ordered,
acceptance-driven implementation with visible assumptions, human gates, tests,
security checks, operational documentation, and a final approval record.

## Start here

1. Copy this entire directory into the new repository.
2. Rename placeholders written as `{{PLACEHOLDER_NAME}}`.
3. Complete `PROJECT-SPEC.md`. This is the only project-specific intake file.
4. Derive and approve `PRODUCT-CANON.md` before implementation begins.
5. Adapt `PROJECT-TASKS.md` without removing its ordering or acceptance rules.
6. Append evidence to `TASK-LOG.md` after every task.
7. Keep `ARCHITECTURE.md` and `OUTPUT-CONTRACT.md` synchronized with approved
   changes to the specification.
8. Run `QUALITY-AND-RELEASE.md` before claiming pilot or production readiness.
9. Use `HANDOFF.md` whenever work moves between machines, people, or sessions.

## File map

| File | Purpose |
| --- | --- |
| `PROJECT-SPEC.md` | Single source for project-specific facts and requirements. |
| `PRODUCT-CANON.md` | Frozen product identity, users, decisions, scope, and boundaries. |
| `PROJECT-TASKS.md` | Ordered implementation backlog and approval gates. |
| `TASK-LOG.md` | Evidence-backed completion record for every task. |
| `ARCHITECTURE.md` | System boundaries, components, data flow, and constraints. |
| `OUTPUT-CONTRACT.md` | Required outputs, states, schemas, and prohibited claims. |
| `REVIEW-WORKSPACES.md` | Optional read-only specialist reviewer definitions. |
| `QUALITY-AND-RELEASE.md` | Testing, security, reliability, deployment, and release gates. |
| `HANDOFF.md` | Exact continuation state for another machine or collaborator. |

## Operating rules

- Files and code are evidence of work, not evidence of completion.
- A task closes only when its acceptance criteria and relevant tests pass.
- Do tasks in order unless the project owner explicitly approves a dependency
  change and records it.
- Stop at human gates. Silence is not approval.
- Preserve user changes and unrelated work.
- Never hide failed tests, missing infrastructure, assumptions, or residual risk.
- Prefer deterministic rules and typed contracts for decisions that must be
  reproducible. Use AI only behind explicit, validated boundaries.
- Do not let review agents become unbounded runtime infrastructure unless that is
  explicitly part of the approved product.

## Status vocabulary

- `NOT_STARTED`
- `IN_PROGRESS`
- `BLOCKED`
- `AWAITING_APPROVAL`
- `COMPLETE`
- `SUPERSEDED` — retained for history with a pointer to the replacement

