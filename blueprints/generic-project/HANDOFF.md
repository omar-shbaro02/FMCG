# {{PROJECT_NAME}} — continuation handoff

Update this file before moving work to another machine, person, or long-lived
session. It describes current reality; it is not a substitute for Git history.

## Repository state

- Repository/path: `{{PATH_OR_URL}}`
- Branch: `{{BRANCH}}`
- HEAD commit: `{{COMMIT}}`
- Remote tracking: `{{REMOTE}}`
- Worktree status: `{{CLEAN_OR_LIST_CHANGES}}`
- Unpushed commits: `{{COUNT_OR_NONE}}`

## Product state

- Active spec version: `{{VERSION}}`
- Active canon version: `{{VERSION}}`
- Current task: `{{TASK}}`
- Last completed task: `{{TASK}}`
- Next mandatory gate: `{{GATE}}`
- Product boundary warning: `{{CRITICAL_BOUNDARY}}`

## What was completed

- `{{ITEM_WITH_FILE_OR_COMMIT_REFERENCE}}`

## What is in progress

- `{{ITEM}}`
- Exact stopping point: `{{FILE_SYMBOL_COMMAND_OR_UI_STEP}}`

## Verification state

| Check | Last result | Environment/date |
| --- | --- | --- |
| Backend tests | `{{RESULT}}` | `{{ENV_DATE}}` |
| Frontend checks/build | `{{RESULT}}` | `{{ENV_DATE}}` |
| Migrations | `{{RESULT}}` | `{{ENV_DATE}}` |
| Live smoke | `{{RESULT}}` | `{{ENV_DATE}}` |
| Security/dependencies | `{{RESULT}}` | `{{ENV_DATE}}` |

## Running services and local state

- Services/ports: `{{SERVICES}}`
- Database/storage: `{{LOCATION_AND_SAFETY}}`
- Test credentials: `{{REFERENCE_TO_ENV_NOT_SECRET}}`
- Background process/session IDs: `{{IDS_OR_NONE}}`
- Required local tools: `{{TOOLS_AND_VERSIONS}}`

## Known issues and assumptions

- `{{ISSUE_OR_ASSUMPTION}}`

## Exact next steps

1. `{{COMMAND_OR_ACTION}}`
2. `{{COMMAND_OR_ACTION}}`
3. Append results to `TASK-LOG.md` and update `PROJECT-TASKS.md` only if the
   acceptance criteria genuinely pass.

## Do not do

- Do not overwrite uncommitted user changes.
- Do not skip a pending human gate.
- Do not mark a task complete based only on existing files.
- Do not expose or commit secrets, real customer data, or local state.
- Do not broaden scope beyond the approved canon without change approval.

