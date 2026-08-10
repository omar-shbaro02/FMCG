# Forecast Adapter doctrine

Forecasting strengthens only the Predict layer. It is evidence for the product,
not the product itself.

TimesFM is the first forecast implementation and must remain replaceable. Its
imports, configuration, failures, and provider-specific output stay inside the
adapter package. Domain services consume only the versioned Forecast Adapter
request, normalized forecast evidence, and structured error contracts.

The adapter may produce numeric movement, direction, intervals, baseline
comparison inputs, retention/decay evidence, uncertainty, data-quality notes,
latency, and model metadata. It may not produce a growth-quality class, priority,
investigation recommendation, human owner, promotion/budget decision, or any
commercial action.

There is no silent TimesFM-to-mock fallback in production. Adapter failure is a
visible, auditable state. Replacement contract tests must prove that identical
normalized evidence produces identical domain outcomes regardless of adapter.

The prohibited paths are `forecast → direct recommendation`, `forecast →
automated action`, `LLM → unverified business decision`, and `dashboard alert →
commercial workflow`.

