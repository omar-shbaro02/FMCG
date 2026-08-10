# Frozen executive output contract

Every executive output contains these sections in this order:

1. Growth signal summary
2. Forecast evidence
3. Growth-quality judgment
4. Primary and secondary risk classification
5. Structured investigation plan
6. Neutral decision simulations
7. Priority
8. Recommended human owner
9. Evidence confidence
10. Decision affected
11. Exact next verification actions
12. Final human-review statement

Allowed priorities are `HEALTHY_CANDIDATE`, `MONITOR`,
`INVESTIGATION_RECOMMENDED`, and `P1_COMMERCIAL_REVIEW`. Evidence confidence is
separate and is one of `STRONG`, `MEDIUM`, `WEAK`, or `INSUFFICIENT`.

Simulations are limited to repeat immediately, scale budget, reward as healthy
growth, pause and monitor, investigate first, redesign before repeat, and
escalate for P1 review. They state conditional benefits, risks, assumptions,
evidence gaps, affected functions, uncertainty, and the human-review requirement.
They never rank, select, optimize, or execute an option.

Unreviewed exports must say `DRAFT — HUMAN REVIEW PENDING`; reviewed exports must
say `HUMAN REVIEW COMPLETED`. Every output ends with exactly:

> This output supports leadership review. It does not make or execute the final
> commercial decision.

