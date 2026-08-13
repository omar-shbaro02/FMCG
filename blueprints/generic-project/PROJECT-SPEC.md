# {{PROJECT_NAME}} — project specification

Status: `DRAFT | APPROVED | SUPERSEDED`  
Owner: `{{PROJECT_OWNER}}`  
Last updated: `{{YYYY-MM-DD}}`  
Spec version: `{{VERSION}}`

This is the primary project-specific input. Complete it before adapting the other
blueprint files. Use exact, testable language. Write `UNKNOWN` when a fact is not
known; do not convert an assumption into a requirement.

## 1. Problem and outcome

- Problem: `{{WHAT_PAIN_OR_RISK_EXISTS}}`
- Desired outcome: `{{MEASURABLE_OR_OBSERVABLE_OUTCOME}}`
- Why now: `{{URGENCY_OR_TRIGGER}}`
- Product name: `{{PROJECT_NAME}}`
- One-sentence product definition: `{{DEFINITION}}`
- Product wedge or differentiator: `{{WEDGE}}`

## 2. Users, buyers, and decisions

| Role | Description | Decisions owned | Access needed |
| --- | --- | --- | --- |
| Primary user | `{{PRIMARY_USER}}` | `{{DECISION}}` | `{{ACCESS}}` |
| Buyer/sponsor | `{{BUYER}}` | `{{PURCHASE_OR_APPROVAL}}` | `{{ACCESS}}` |
| Reviewer | `{{REVIEWER}}` | `{{REVIEW_DECISION}}` | `{{ACCESS}}` |
| Administrator | `{{ADMIN}}` | `{{ADMIN_DECISION}}` | `{{ACCESS}}` |

Exact decision the product improves:

> {{DECISION_QUESTION}}

The product must not make or execute these decisions:

- `{{PROHIBITED_DECISION_1}}`
- `{{PROHIBITED_DECISION_2}}`

## 3. Scope

### In scope

- `{{CAPABILITY_1}}`
- `{{CAPABILITY_2}}`
- `{{CAPABILITY_3}}`

### Explicitly out of scope

- `{{OUT_OF_SCOPE_1}}`
- `{{OUT_OF_SCOPE_2}}`
- `{{OUT_OF_SCOPE_3}}`

### Non-goals

- `{{NON_GOAL_1}}`
- `{{NON_GOAL_2}}`

## 4. Primary workflow

`{{INPUT}} → {{VALIDATION}} → {{CORE_PROCESS}} → {{OUTPUT}} → {{HUMAN_REVIEW_OR_ACTION}}`

For every stage define:

| Stage | Input | Output | Owner | Failure behavior | Audit requirement |
| --- | --- | --- | --- | --- | --- |
| `{{STAGE}}` | `{{INPUT}}` | `{{OUTPUT}}` | `{{OWNER}}` | `{{FAILURE}}` | `{{AUDIT}}` |

## 5. Inputs and data

- Input sources: `{{SOURCES}}`
- Required fields and types: `{{FIELDS_OR_SCHEMA_LINK}}`
- Record grain/identity: `{{GRAIN}}`
- Units, currency, timezone, and date rules: `{{CONVENTIONS}}`
- Required history or sample size: `{{MINIMUM_EVIDENCE}}`
- Missing, duplicate, invalid, and late-data behavior: `{{RULES}}`
- Sensitive data classes: `{{CLASSIFICATION}}`
- Retention/deletion requirements: `{{RETENTION}}`
- Data residency or compliance requirements: `{{COMPLIANCE}}`

## 6. Business/domain rules

List every frozen class, state, threshold, priority, or decision rule. Each rule
must have a stable identifier and a test fixture.

| Rule ID | Rule | Inputs | Output/state | Versioned? | Human override? |
| --- | --- | --- | --- | --- | --- |
| `{{RULE_ID}}` | `{{RULE}}` | `{{INPUTS}}` | `{{OUTPUT}}` | yes/no | `{{POLICY}}` |

## 7. Outputs and human control

- Primary output: `{{OUTPUT}}`
- Required sections/fields: `{{FIELDS}}`
- Draft/review/approved labels: `{{LABELS}}`
- Confidence and uncertainty vocabulary: `{{VOCABULARY}}`
- Evidence traceability requirement: `{{TRACEABILITY}}`
- Final human owner: `{{HUMAN_OWNER}}`
- Exact mandatory disclaimer or review statement: `{{STATEMENT}}`
- Supported export formats: `{{FORMATS}}`
- Prohibited claims/actions: `{{PROHIBITIONS}}`

## 8. Functional requirements

Give every requirement an ID so tasks, tests, commits, and release evidence can
reference it.

| ID | Requirement | Priority | Acceptance criterion | Owner |
| --- | --- | --- | --- | --- |
| `FR-001` | `{{REQUIREMENT}}` | Must/Should/Could | `{{OBSERVABLE_RESULT}}` | `{{OWNER}}` |

## 9. Non-functional requirements

| Area | Requirement | Measurement/limit |
| --- | --- | --- |
| Security | `{{REQUIREMENT}}` | `{{MEASURE}}` |
| Privacy | `{{REQUIREMENT}}` | `{{MEASURE}}` |
| Availability | `{{REQUIREMENT}}` | `{{SLO}}` |
| Performance | `{{REQUIREMENT}}` | `{{LIMIT}}` |
| Reliability | `{{REQUIREMENT}}` | `{{LIMIT}}` |
| Accessibility | `{{REQUIREMENT}}` | `{{STANDARD}}` |
| Observability | `{{REQUIREMENT}}` | `{{SIGNALS}}` |
| Portability | `{{REQUIREMENT}}` | `{{TARGETS}}` |

## 10. Architecture and technology constraints

- Architecture style: `{{STYLE}}`
- Frontend: `{{STACK_OR_UNKNOWN}}`
- Backend: `{{STACK_OR_UNKNOWN}}`
- Database/storage: `{{STACK_OR_UNKNOWN}}`
- External integrations: `{{INTEGRATIONS}}`
- Replaceable adapters: `{{ADAPTERS}}`
- Background jobs: `{{BOUNDARY}}`
- AI/model use: `{{MODEL_BOUNDARY_OR_NONE}}`
- Hosting/deployment: `{{TARGET}}`
- Prohibited architectural patterns: `{{PROHIBITIONS}}`

## 11. Environments and operations

- Local: `{{LOCAL_SETUP}}`
- Test: `{{TEST_ENVIRONMENT}}`
- Staging: `{{STAGING}}`
- Production: `{{PRODUCTION}}`
- Secrets provider: `{{PROVIDER}}`
- Backup/restore targets: `{{RPO_RTO}}`
- Monitoring and alert ownership: `{{OWNER}}`
- Rollback method: `{{METHOD}}`

## 12. Test scenarios

| Scenario ID | Input/condition | Expected result | Failure that must be prevented |
| --- | --- | --- | --- |
| `SCN-A` | `{{CONDITION}}` | `{{EXPECTED}}` | `{{FAILURE}}` |

Include happy path, invalid input, insufficient evidence, permissions, boundary
drift, dependency outage, retry/idempotency, concurrency, export, recovery, and
end-to-end human review where applicable.

## 13. Human gates

| Gate | Owner | Required evidence | Approval wording | Status |
| --- | --- | --- | --- | --- |
| Contract freeze | `{{OWNER}}` | Canon and backlog | `APPROVED` | Pending |
| Domain realism | `{{OWNER}}` | Representative scenarios | `APPROVED` | Pending |
| Release readiness | `{{OWNER}}` | Full release packet | `APPROVED` | Pending |

## 14. Assumptions, risks, and open decisions

| ID | Type | Statement | Impact | Owner | Due | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `A-001` | Assumption/Risk/Decision | `{{STATEMENT}}` | `{{IMPACT}}` | `{{OWNER}}` | `{{DATE}}` | Open |

## 15. Definition of done

The project is done only when:

- all Must requirements have passing acceptance evidence;
- all ordered tasks and mandatory human gates are complete;
- end-to-end scenarios pass in a production-like environment;
- security, privacy, dependency, performance, reliability, backup, and rollback
  evidence is recorded;
- documentation matches the released implementation;
- monitoring and operational ownership are assigned;
- known limitations and residual risks are accepted by the project owner;
- the final release approval is dated and attributable.

## Approval record

- Reviewer: `{{NAME}}`
- Decision: `APPROVED | CHANGES_REQUIRED | REJECTED`
- Date: `{{YYYY-MM-DD}}`
- Spec version: `{{VERSION}}`
- Comments: `{{COMMENTS}}`

