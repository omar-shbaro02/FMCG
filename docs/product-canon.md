# Frozen product canon

## Identity

- Product family: **VAI FMCG Commercial Decision Intelligence**
- MVP: **FMCG Growth Quality Diagnostic**
- Working product name: **Forecast-Augmented Growth Quality Diagnostic**
- Primary buyer and user: **FMCG Commercial Director**
- Core wedge: **forecast-augmented commercial growth-quality investigation
  prioritization**

## Exact decision

Which apparently positive FMCG growth signal should leadership investigate
before treating it as healthy growth?

The product improves that decision by predicting relevant movement, interpreting
commercial meaning, classifying growth quality and risk, creating an exact
investigation plan, neutrally simulating approved leadership options, and
producing a leadership-ready output for human review.

## Control line

TimesFM forecasts movement. VAI interprets growth quality. Humans validate before
leadership acts.

## Forecast boundary

- Primary target: weekly `sell_out_units`
- Series grain: `sku_id + channel + region`
- Primary horizon: configurable from 4 to 8 weeks after promotion
- Secondary targets run only after the primary target is valid and supported by
  available data.
- Baseline calculation and commercial interpretation are separate from TimesFM.
- TimesFM is the first implementation behind a replaceable `ForecastAdapter`.

## Correct architecture

Business signals → Forecast Adapter → FMCG interpretation → growth-quality
classification → investigation planning → decision simulation → leadership-ready
output → human review → feedback learning.

Forecast evidence never flows directly to a recommendation or action.

## Allowed scope

The application may:

- ingest and validate weekly FMCG sales data;
- calculate traceable expected baselines;
- forecast structured numeric movement with visible uncertainty;
- interpret validated forecast and commercial evidence;
- classify frozen candidate growth-quality risks;
- request specific evidence from mapped human functions;
- compare only the approved decision options without choosing one;
- generate draft and human-reviewed executive briefs;
- record review feedback and an audit trail.

## Forbidden scope

The application is not demand planning, sales forecasting, promotion or pricing
optimization, trade-promotion management, replenishment, distributor management,
ERP/SAP/CRM integration, budget optimization, stock allocation, campaign
execution, customer communication, a generic dashboard/chatbot, or a TimesFM
demonstration. It is not a reusable multi-industry platform.

It must never change a price, discount, budget, promotion, stock level, or
commercial workflow; contact an account, distributor, or customer; claim a
forecast proves a conclusion; hide uncertainty; assign final responsibility
without the frozen owner logic; choose a final commercial option; or execute a
simulated option.

## Human ownership

The Commercial Director performs final review. Trade Marketing, Sales Operations,
Commercial Finance, Category/Brand, and Account/Distributor reviewers supply the
evidence defined by their functions. A read-only executive may view approved
outputs. Humans validate and decide; the system does not execute.

## Review gates

Work stops for explicit Kamal review after:

1. Task 0 — frozen project contract;
2. Task 12 — commercially usable Forecast Adapter evidence;
3. Task 15 — commercially realistic classification;
4. Task 29 — controlled-pilot readiness.

No gate is inferred from technical test success.

## Task 0 acceptance checklist

- [x] The product remains FMCG only.
- [x] The buyer remains the FMCG Commercial Director.
- [x] The exact leadership decision is unchanged.
- [x] The wedge is investigation prioritization, not forecasting.
- [x] The primary target, grain, and horizon are explicit.
- [x] Forecast evidence is separated from commercial interpretation.
- [x] Direct recommendations and automated actions are prohibited.
- [x] The executive output and human-review requirement are frozen.
- [x] The project lead has reviewed and approved this contract.
