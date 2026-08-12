# Task 15 — Commercial-realism review

Status: `APPROVED BY PROJECT OWNER — 2026-08-12`

Reviewer role: Kamal / designated FMCG commercial lead. The project owner may
approve this gate directly or record Kamal's decision.

## What is being approved

The versioned classifier `fmcg-growth-quality-rules/1.0.0` converts only
structured interpretation candidates into one primary class, optional secondary
classes, a separate priority, and separate evidence confidence. It does not
select, recommend, optimize, or execute a commercial action. A healthy result is
always labelled a candidate pending human validation.

## Seven required commercial patterns

| Pattern | Evidence that keeps it plausible | Exclusion / safety check | Expected outcome |
|---|---|---|---|
| Healthy growth | Above-baseline movement, sustained retention, no decay | Exclude if any material loading, stock, discount, cannibalization, or margin risk remains | `HEALTHY_GROWTH_CANDIDATE`; healthy-candidate priority |
| Temporary uplift | Weak/partial retention and return to expected baseline | Exclude when sustained improvement is supported | `TEMPORARY_UPLIFT`; investigation priority |
| Pull-forward | Below-baseline post-promotion movement with moderate/strong decay | Require an adequate aligned post-promotion horizon | `PULL_FORWARD_RISK`; investigation priority |
| Loading / channel stock | Material sell-in excess; stock evidence strengthens channel-stock pressure | Stock pressure is excluded when stock evidence is absent; loading plus stock converges to P1 | Loading primary, stock secondary, P1 review |
| Discount dependency | Movement tied to high discount and weak retention | Require repeated discount/movement evidence | `DISCOUNT_DEPENDENCY_RISK`; investigation priority |
| Cannibalization | Promoted SKU movement coincides with identified adjacent-series decline | Never classify without adjacent-series evidence | `CANNIBALIZATION_RISK`; investigation priority |
| Margin / value quality | Positive volume with material unit-value or margin compression | Never classify without validated value/margin evidence | `MARGIN_VALUE_QUALITY_RISK`; P1 review |

## Cross-pattern behavior to validate

- One primary class is selected using a fixed, documented risk ordering; other
  credible outcomes remain secondary.
- Healthy growth is excluded whenever a material risk remains unresolved.
- Insufficient evidence produces no risk class, investigation priority, and a
  specific exclusion reason rather than false certainty.
- P1 urgency can arise from converging risks or high business impact with a
  critical evidence gap; urgency does not inflate evidence confidence.
- Supporting, contradicting, missing, and exclusion evidence remain separately
  traceable.
- Controlled LLM prose is optional and cannot change deterministic class or
  priority. Its output must use known evidence keys, avoid action language, pass
  a strict schema, and exhaust at most three attempts.

## Verification evidence

- All ten frozen classes have inspectable definitions, evidence conditions,
  exclusions, priority impact, and human-owner implications.
- Synthetic fixture expectations cover healthy, temporary uplift, pull-forward,
  loading, discount dependency, cannibalization, margin/value risk, and
  insufficient evidence.
- Backend quality gate: Ruff lint/format, strict MyPy, migration, and 55 Pytest
  tests pass against PostgreSQL on Python 3.12.

## Approval decision

Approve only if these patterns match practical FMCG commercial reasoning and the
P1 triggers are neither too sensitive nor too permissive. Approval unlocks Task
16. If changes are required, identify the pattern and threshold/condition; the
rule version will be revised and the fixtures rerun before this gate is presented
again.

Decision recorded: the project owner directed continued progress on 2026-08-12,
approving this gate and unlocking Task 16.
