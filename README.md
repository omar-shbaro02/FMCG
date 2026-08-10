# Forecast-Augmented Growth Quality Diagnostic

A standalone FMCG decision-intelligence product for Commercial Directors.
It helps leadership identify which apparently positive growth signals require
investigation before they are treated as healthy growth.

> TimesFM forecasts movement. VAI interprets growth quality. Humans validate
> and decide.

## Current status

Task 0 is approved. Task 1 repository initialization is implemented and backend
checks pass; frontend and Compose runtime verification await a host with Node.js
22 and Docker Compose.

No Task 2 functionality will be implemented until Task 1 acceptance is fully
verified. See [PROJECT_TASKS.md](PROJECT_TASKS.md) for the ordered backlog and
[TASK_LOG.md](TASK_LOG.md) for the delivery record.

## Frozen scope

- Buyer: FMCG Commercial Director
- Decision: which apparently positive FMCG growth signal should leadership
  investigate before treating it as healthy growth?
- Primary target: weekly `sell_out_units` at
  `sku_id + channel + region` grain
- Forecast horizon: configurable from 4 to 8 post-promotion weeks
- Output: a leadership-ready, human-reviewed growth-quality diagnostic
- Runtime: deterministic orchestration; no autonomous agents or commercial
  actions

The canonical contract is in [docs/product-canon.md](docs/product-canon.md).
