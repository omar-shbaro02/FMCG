# API guide

OpenAPI is served at `/docs` and `/openapi.json`. Obtain a bearer token from
`POST /api/auth/login`; send it as `Authorization: Bearer <token>`. APIs cover
datasets, cases, baselines, forecasts, decision intelligence, human reviews,
feedback, exports, and admin operations. Long outputs remain tied to one case.

Managers create and progress cases; specialist reviewers review; read-only
executives view; admins manage uploads and operational metadata. Errors never
return stack traces. Requests are rate-limited, responses use security headers,
and audit/admin endpoints omit raw payloads and secrets.
