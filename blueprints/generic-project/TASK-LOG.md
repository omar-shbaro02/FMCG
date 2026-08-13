# {{PROJECT_NAME}} — task delivery log

Append records; do not rewrite failed or superseded history. A task is not
complete until its record contains concrete evidence.

## Task {{NUMBER}} — {{TITLE}}

**Status:** `IN_PROGRESS | BLOCKED | AWAITING_APPROVAL | COMPLETE`  
**Date:** `{{YYYY-MM-DD}}`  
**Owner:** `{{NAME_OR_ROLE}}`  
**Spec/canon version:** `{{VERSION}}`

### Acceptance results

| Criterion | Result | Evidence |
| --- | --- | --- |
| `{{CRITERION}}` | Pass/Fail/Not run | `{{TEST, FILE, URL, SCREENSHOT, OR LOG}}` |

### Completed work

- `{{IMPLEMENTED_ITEM}}`

### Changed files

- `{{PATH}}` — `{{WHY}}`

### Verification

- Command/check: `{{COMMAND_OR_MANUAL_CHECK}}`
- Environment: `{{OS_RUNTIME_DATABASE_PROVIDER}}`
- Result: `{{EXACT_COUNTS_AND_STATUS}}`
- Warnings: `{{WARNINGS_OR_NONE}}`

### Assumptions and residual risks

- `{{ASSUMPTION_OR_RISK}}`

### Canon/boundary confirmation

- User/buyer unchanged: yes/no
- Exact decision unchanged: yes/no
- Scope and prohibited actions preserved: yes/no
- Human ownership/review preserved: yes/no/not applicable
- Explanation: `{{DETAIL}}`

### Gate decision

- Decision: `APPROVED | CHANGES_REQUIRED | NOT_APPLICABLE`
- Approver: `{{NAME_OR_ROLE}}`
- Date: `{{YYYY-MM-DD}}`
- Comments: `{{COMMENTS}}`

---

## Release-readiness audit — {{YYYY-MM-DD}}

**Status:** `{{STATUS}}`

### Passed

- `{{CHECK_AND_EXACT_RESULT}}`

### Failed or not run

- `{{CHECK}}` — `{{CAUSE}}` — `{{OWNER/NEXT_STEP}}`

### Remaining gates

- `{{GATE}}`

