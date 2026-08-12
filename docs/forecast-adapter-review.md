# Task 12 — Forecast Adapter commercial review packet

Status: awaiting project-lead approval  
Review scope: structure and commercial usability of forecast evidence—not model
accuracy certification or a commercial decision.

## Control boundary

TimesFM forecasts numeric movement. Deterministic VAI rules derive business-neutral
evidence. Later FMCG logic interprets growth quality. Humans validate and decide.

The adapter contract rejects unknown output fields, including commercial
recommendations. It cannot output a risk class, priority, owner, budget,
promotion choice, or action.

## Sample input

```json
{
  "forecast_target": "sell_out_units",
  "series_id": "SKU-1|MODERN_TRADE|NORTH",
  "time_grain": "weekly",
  "horizon": 6,
  "history": [
    {"week_start_date": "2026-01-05", "value": 100},
    {"week_start_date": "2026-01-12", "value": 103},
    {"week_start_date": "2026-01-19", "value": 108},
    {"week_start_date": "2026-01-26", "value": 105}
  ],
  "covariates": {
    "promo_flag": [false, false, true, true],
    "discount_depth": [0, 0, 0.2, 0.2],
    "out_of_stock_flag": [false, false, false, false]
  },
  "context": {
    "sku_id": "SKU-1",
    "channel": "MODERN_TRADE",
    "region": "NORTH",
    "promotion_start_week": "2026-01-19",
    "promotion_end_week": "2026-01-26"
  }
}
```

Production readiness requires at least the configured history minimum; the short
input above exists only to make the contract readable.

## Sample normalized adapter output

```json
{
  "forecast_target": "sell_out_units",
  "forecast_horizon": 6,
  "series_id": "SKU-1|MODERN_TRADE|NORTH",
  "forecast_direction": "DECLINING",
  "forecasted_values": [
    {
      "week_start_date": "2026-02-02",
      "point_forecast": 101.0,
      "lower_bound": 86.0,
      "upper_bound": 116.0
    }
  ],
  "confidence_interval": {"level": 0.8, "available": true},
  "baseline_comparison": "INSUFFICIENT",
  "post_promo_retention_status": "INSUFFICIENT",
  "decay_signal": "UNCERTAIN",
  "uncertainty_level": "MEDIUM",
  "data_quality_notes": [],
  "adapter_metadata": {
    "adapter_name": "timesfm",
    "adapter_version": "2.5-contract-1",
    "generated_at": "UTC_TIMESTAMP"
  }
}
```

Baseline comparison, retention, decay, and final uncertainty are recalculated by
deterministic VAI evidence rules after the adapter returns. The raw adapter never
claims that growth is healthy.

## Sample derived evidence

For forecasts `[130, 110, 90, 70]`, baseline `[110, 110, 110, 110]`, q10/q90
interval width of 80 units, actual sell-out 80, and sell-in 130:

```json
{
  "forecast_direction": "STRONGLY_DECLINING",
  "baseline_comparison": "BELOW_BASELINE",
  "post_promo_retention_status": "WEAK",
  "decay_signal": "STRONG",
  "uncertainty_level": "HIGH",
  "sell_in_sell_out_divergence": "MATERIAL_SELL_IN_EXCESS",
  "evidence_values": {
    "forecast_mean": 100.0,
    "baseline_mean": 110.0,
    "forecast_to_baseline_ratio": 0.9091,
    "decay_percent": 0.4615,
    "sell_in_to_sell_out_ratio": 1.625
  }
}
```

This is evidence for later FMCG interpretation, not a loading or pull-forward
classification by itself.

## Uncertainty examples

- `LOW`: mean interval width is at most 20% of point movement.
- `MEDIUM`: width is above 20% and at most 50%.
- `HIGH`: width exceeds 50%.
- `INSUFFICIENT`: interval is unavailable, baseline is missing/misaligned, or
  evidence cannot support the calculation.

These initial thresholds require review and later rule versioning.

## Structured failures

| Category | Example | Retryable |
|---|---|---:|
| `MODEL_UNAVAILABLE` | Package/checkpoint unavailable | Depends on load failure |
| `UNSUPPORTED_SERIES_LENGTH` | History exceeds configured context | No |
| `MALFORMED_DATA` | Prepared input is non-finite/not 1-D | No |
| `TIMEOUT` | Inference exceeds configured bound | Yes |
| `MEMORY_FAILURE` | Model/inference exhausts memory | Yes |
| `MODEL_FAILURE` | Provider runtime exception | Yes |
| `MALFORMED_OUTPUT` | Wrong shape, non-finite values, invalid intervals | No |

There is no production fallback from TimesFM to mock. Failed runs store the
structured error, mark the case failed, and return no forecast evidence.

## Replacement demonstration

`FORECAST_ADAPTER=mock` and `FORECAST_ADAPTER=timesfm` resolve through the same
six-method interface and strict request/response models. All downstream evidence
rules accept only `ForecastResponse`; no domain module imports TimesFM. The mock
is deterministic and labeled non-commercial. Contract tests prove both the
provider-shaped TimesFM output and mock output normalize into the same domain
contract.

## Approval questions

1. Is weekly sell-out at SKU + channel + region the correct primary evidence?
2. Is the 4–8 week structured horizon commercially usable?
3. Are direction, baseline, retention, decay, divergence, and uncertainty clearly
   separated from growth-quality interpretation?
4. Are uncertainty and insufficient evidence visible enough?
5. Are failure states preferable to silent fallback?
6. Is the evidence packet ready for Task 13 FMCG interpretation?

Approval must be explicit. Task 13 does not begin until this gate is approved.
