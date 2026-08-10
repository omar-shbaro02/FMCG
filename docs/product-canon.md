# Forecast-Augmented Growth Quality Diagnostic — Product Canon

Status: FROZEN, approved by project owner  
Scope: FMCG only  
Primary user and buyer: FMCG Commercial Director

## Exact decision

The product helps a Commercial Director answer:

> Which apparently positive FMCG growth signal should leadership investigate before treating it as healthy growth?

It prioritizes investigation. It does not make or execute a commercial decision.

## Product wedge

Forecast-augmented commercial growth-quality investigation prioritization.

## Control line

TimesFM forecasts movement. VAI interprets growth quality. Humans validate before leadership acts.

## Primary forecast target

Weekly `sell_out_units` at the exact grain:

`sku_id + channel + region`

The supported post-promotion horizon is configurable from four to eight weeks. Secondary targets may run only after the primary target passes validation and the required data exists.

## Required decision flow

Business signals → replaceable Forecast Adapter → FMCG interpretation → growth-quality classification → investigation planning → neutral decision simulation → leadership-ready output → human review → feedback.

Forecast evidence and business interpretation must remain separate and traceable. No forecast may directly produce a recommendation or action.

## Frozen growth-quality classes

- `HEALTHY_GROWTH_CANDIDATE`
- `TEMPORARY_UPLIFT`
- `PULL_FORWARD_RISK`
- `LOADING_RISK`
- `CHANNEL_STOCK_PRESSURE`
- `CANNIBALIZATION_RISK`
- `DISCOUNT_DEPENDENCY_RISK`
- `MARGIN_VALUE_QUALITY_RISK`
- `INVESTIGATION_RECOMMENDED`
- `P1_COMMERCIAL_REVIEW`

Healthy growth is always a candidate judgment pending human validation, never a final declaration.

## Output contract

Every leadership output must contain:

1. Growth signal summary.
2. Forecast evidence.
3. Growth-quality judgment, with facts separated from interpretation.
4. Primary and secondary risk classifications.
5. A specific investigation plan.
6. Neutral decision simulations that cannot be executed.
7. Priority.
8. Recommended human owner.
9. Evidence confidence and explicit uncertainty.
10. The decision affected.
11. Exact next verification actions.
12. A statement that the output requires final human review.

Draft and unreviewed outputs must be visibly marked. Approved exports must preserve review status.

## Human ownership

- Commercial Director: final review and validation.
- Trade Marketing: promotion mechanic, discount depth, and execution evidence.
- Sales Operations: sell-in, sell-out, channel movement, returns, and execution evidence.
- Commercial Finance: sales value, margin, discount cost, and commercial value quality.
- Category / Brand: cannibalization and portfolio effects.
- Key Account / Distributor Manager: loading, customer concentration, channel stock, and account behavior.

The application may recommend a defined human owner. It may not assign final responsibility or trigger work outside the diagnostic.

## Explicit boundaries

This standalone application is not demand planning, sales forecasting, promotion or pricing optimization, trade promotion management, replenishment, distributor management, ERP/SAP/CRM integration, workflow automation, a generic dashboard, a chatbot, an autonomous-agent system, or a TimesFM demonstration.

It must never change prices, discounts, budgets, stock, campaigns, messages, customer activity, or any other commercial state. It must not contact external parties, select a final option, claim a forecast proves a conclusion, hide uncertainty, or fabricate missing evidence.

## Architecture constraints

- Modular monolith; no unneeded microservices.
- PostgreSQL with migrations and fixed-precision financial types.
- TimesFM behind a replaceable `ForecastAdapter`; TimesFM-specific fields stay inside the adapter.
- Deterministic rules first; controlled schema-validated LLM synthesis second.
- No autonomous agent loops or external-action tools.
- Every material transition, model version, rule version, prompt version, and human correction is auditable.
- Human review is mandatory before a final output is treated as reviewed.

## Review gates

Work stops for Kamal approval at:

1. Task 0 — frozen product contract (this document).
2. Task 12 — Forecast Adapter structure and commercial usability.
3. Task 15 — classification realism for FMCG decisions.
4. Task 29 — final controlled-pilot readiness.

## Task 0 approval record

- Reviewer: project owner acting as final product approver
- Status: APPROVED
- Approval date: 2026-08-10
- Comments: “you can continue it i approve this step, i need it be finished”

Task 1 and subsequent implementation may proceed in the specified order.
