# Security guide and residual risk

Controls include Argon2 password verification, bounded signed tokens, frozen
RBAC, production-secret validation, CORS allowlisting, API rate limiting, response
security headers, non-root containers, content-addressed uploads, simple filename
and MIME/extension checks, size limits, typed schemas, SQLAlchemy parameters,
LLM evidence-reference/action validation, audit events, and admin payload
redaction.

Run `pip-audit`, `npm audit`, `gitleaks detect --no-git`, and the full test suite
before release. Known residual risks: the in-process rate limiter is per replica;
production needs an edge/Redis distributed limiter. Upload malware scanning is an
integration point, not bundled. RBAC is global because tenant/account isolation
is outside the frozen MVP. Broad dependency ranges should be locked in release
images. TimesFM weights are third-party supply-chain inputs and require checksum/
provenance controls.
