# {{PROJECT_NAME}} — output contract

Status: `DRAFT — APPROVAL REQUIRED`

## Output states

| State | Meaning | Who can set it | Allowed next states |
| --- | --- | --- | --- |
| `DRAFT` | Generated but not reviewed | System | `IN_REVIEW`, `REJECTED` |
| `IN_REVIEW` | Human review underway | Reviewer | `APPROVED`, `CHANGES_REQUIRED`, `REJECTED` |
| `APPROVED` | Approved for its stated use | Authorized human | `SUPERSEDED` |
| `SUPERSEDED` | Preserved historical version | System/human | none |

Adapt these states to `PROJECT-SPEC.md`; never imply approval without an
authenticated approval record.

## Required ordered sections/fields

1. `{{SUMMARY}}`
2. `{{SUPPLIED_FACTS_OR_INPUTS}}`
3. `{{DERIVED_EVIDENCE}}`
4. `{{INTERPRETATION_OR_RESULT}}`
5. `{{UNCERTAINTY_AND_LIMITATIONS}}`
6. `{{MISSING_INFORMATION}}`
7. `{{FOLLOW_UP_OR_VERIFICATION}}`
8. `{{HUMAN_OWNER}}`
9. `{{STATUS_AND_VERSION}}`
10. `{{MANDATORY_FINAL_STATEMENT}}`

## Structured schema

```json
{
  "output_id": "opaque ID",
  "source_record_id": "opaque ID",
  "schema_version": "semantic version",
  "status": "DRAFT|IN_REVIEW|APPROVED|SUPERSEDED",
  "facts": [{"evidence_key": "string", "value": "typed value"}],
  "result": {},
  "uncertainty": [],
  "missing_evidence": [],
  "human_owner": "role|null",
  "review": {
    "reviewer_id": null,
    "reviewed_at": null,
    "decision": null
  }
}
```

Replace the generic `result` with a strict project schema. Reject unknown fields
where silent expansion could change meaning.

## Traceability and language rules

- Derived claims cite supplied evidence keys or source records.
- Facts, calculations, interpretation, assumptions, and uncertainty remain
  distinguishable.
- Missing information is explicit; `null` is preferred to guessing.
- Confidence is not impact, urgency, priority, or approval.
- Draft and approved versions remain separately retrievable.
- Exports preserve content, schema version, review status, and attribution.
- Prohibited claims/actions: `{{PROHIBITIONS}}`.
- Exact final statement: `{{MANDATORY_STATEMENT}}`.

## Contract tests

- required fields and ordering;
- invalid/unknown field rejection;
- evidence-reference integrity;
- state-transition legality;
- draft/approved label truthfulness;
- rendered/structured/export parity;
- escaping and injection safety;
- backward compatibility or explicit version rejection.

