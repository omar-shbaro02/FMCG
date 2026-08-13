# TimesFM adapter guide

Set `FORECAST_ADAPTER=timesfm` and install `backend[timesfm]`. Configure the
model ID, context length, 4–8 week horizon, batch size, device, timeout, and q10/
q90 indices through environment variables. Weights and cache are external
deployment data and must not be committed.

The adapter lazy-loads TimesFM 2.5, normalizes provider output into the frozen
forecast contract, records model/version/latency metadata, and returns structured
failures. `FORECAST_ADAPTER=mock` is deterministic development behavior and must
be visibly declared; it is not a hidden production fallback.
