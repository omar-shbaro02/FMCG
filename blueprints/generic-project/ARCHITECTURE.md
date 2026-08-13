# {{PROJECT_NAME}} — architecture contract

Source: approved `PROJECT-SPEC.md` and `PRODUCT-CANON.md`.

## System context

- Users: `{{USERS}}`
- System responsibility: `{{RESPONSIBILITY}}`
- External systems: `{{SYSTEMS}}`
- Trust boundaries: `{{BOUNDARIES}}`

## Request and data flow

`{{CLIENT}} → {{AUTH}} → {{API}} → {{DOMAIN}} → {{DATABASE}} → {{OUTPUT}} → {{REVIEW}}`

Describe every asynchronous branch separately. State where retries, idempotency,
timeouts, audit events, and human approval occur.

## Components

| Component | Responsibility | Owns authoritative state? | Dependencies | Failure behavior |
| --- | --- | --- | --- | --- |
| `{{COMPONENT}}` | `{{RESPONSIBILITY}}` | yes/no | `{{DEPENDENCIES}}` | `{{BEHAVIOR}}` |

## Data ownership

| Entity | System of record | Identity/grain | Retention | Access boundary |
| --- | --- | --- | --- | --- |
| `{{ENTITY}}` | `{{STORE}}` | `{{IDENTITY}}` | `{{RETENTION}}` | `{{ACCESS}}` |

## Adapter boundaries

Each external provider must expose a typed provider-neutral contract, structured
errors, provenance, health, timeout, and deterministic test substitute. Provider
SDK types must not leak into domain or output schemas.

## AI/model boundary

State `NONE` if the project does not use AI. Otherwise specify:

- exact allowed task;
- supplied evidence and permitted tools;
- schema and evidence-reference validation;
- model/prompt/version audit fields;
- retry and timeout bounds;
- forbidden decisions/actions;
- deterministic fallback or explicit failure behavior;
- human review requirement.

## Security model

- Authentication: `{{METHOD}}`
- Authorization and tenancy: `{{METHOD}}`
- Secret handling: `{{METHOD}}`
- Encryption: `{{METHOD}}`
- Input/output controls: `{{CONTROLS}}`
- Audit and privacy: `{{CONTROLS}}`

## Operational model

- Environments: `{{ENVIRONMENTS}}`
- Health/readiness: `{{ENDPOINTS_OR_CHECKS}}`
- Logs/metrics/traces: `{{SIGNALS}}`
- Backup/restore: `{{METHOD_AND_TARGETS}}`
- Deployment/rollback: `{{METHOD}}`

## Architecture decision record template

### ADR-{{NUMBER}} — {{TITLE}}

- Status: Proposed/Accepted/Superseded
- Context: `{{WHY_A_DECISION_IS_NEEDED}}`
- Decision: `{{CHOICE}}`
- Alternatives: `{{ALTERNATIVES}}`
- Consequences: `{{POSITIVE_AND_NEGATIVE}}`
- Canon impact: none or `{{IMPACT_AND_APPROVAL}}`

