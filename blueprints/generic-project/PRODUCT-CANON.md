# {{PROJECT_NAME}} — product canon

Status: `DRAFT — APPROVAL REQUIRED`  
Source: `PROJECT-SPEC.md` version `{{VERSION}}`

This file freezes the identity and boundary of the product. Do not copy unknowns
from the specification as facts. Resolve them or keep implementation blocked.

## Product identity

- Name: `{{PROJECT_NAME}}`
- Product family: `{{PRODUCT_FAMILY}}`
- Primary user: `{{PRIMARY_USER}}`
- Buyer/sponsor: `{{BUYER}}`
- Exact decision: `{{DECISION_QUESTION}}`
- Product wedge: `{{WEDGE}}`
- Control line: `{{WHAT_SYSTEM_DOES}}. {{WHAT_HUMANS_DO}}.`

## Required workflow

`{{ORDERED_WORKFLOW}}`

Every transition must define its input, output, failure state, owner, and audit
record. No downstream stage may silently repair or reinterpret invalid input.

## Frozen domain vocabulary

| Term | Exact meaning | Allowed values | Prohibited interpretation |
| --- | --- | --- | --- |
| `{{TERM}}` | `{{MEANING}}` | `{{VALUES}}` | `{{PROHIBITION}}` |

## Human ownership

| Role | Owns | May approve | May not do through this product |
| --- | --- | --- | --- |
| `{{ROLE}}` | `{{RESPONSIBILITY}}` | `{{APPROVAL}}` | `{{BOUNDARY}}` |

## Explicit boundaries

This product is not:

- `{{OUT_OF_SCOPE_CAPABILITY}}`

It must never:

- `{{PROHIBITED_ACTION_OR_CLAIM}}`

## Architecture constraints

- `{{CONSTRAINT}}`
- Deterministic, testable rules own reproducible business state.
- External providers are isolated behind typed, replaceable adapters.
- AI output cannot silently change authoritative state or bypass human review.
- Material transitions, versions, and corrections are auditable.

## Change control

Any change to the user, buyer, exact decision, product family, frozen vocabulary,
required workflow, prohibited scope, output contract, or human approval model is
a canon change. Stop implementation, update `PROJECT-SPEC.md`, assess migration
impact, obtain owner approval, and record the decision in `TASK-LOG.md`.

## Approval

- Owner: `{{PROJECT_OWNER}}`
- Status: `PENDING | APPROVED`
- Date: `{{YYYY-MM-DD}}`
- Canon version: `{{VERSION}}`

