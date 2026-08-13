# Architecture

The system is a deterministic modular monolith. HTTP requests enter FastAPI,
pass signed authentication and role guards, and write PostgreSQL entities and
audit events. The case pipeline is dataset validation → exact series scope →
baseline → replaceable forecast adapter → numeric forecast evidence → FMCG
interpretation → versioned classifier → exact investigation plan → seven neutral
simulations → draft executive output → attributed human review → export.

Forecast provider code is isolated under `app/adapters/forecast`. Optional LLM
prose is isolated under `app/adapters/llm`, must cite supplied evidence keys, and
cannot set class or priority. Business rules live under `app/domain`. The Next.js
UI has no execution control. PostgreSQL is authoritative; Redis is reserved for
later distributed-job operation and is not required for synchronous correctness.
