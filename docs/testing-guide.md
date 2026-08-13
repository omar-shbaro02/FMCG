# Testing guide

Run `make check` after installing development dependencies. CI runs Ruff, full
strict MyPy, PostgreSQL-backed Pytest with coverage, frontend production
dependency audit, ESLint, strict TypeScript, Vitest, and a production build.

For local checks, start PostgreSQL with `docker compose up -d database`; the
test target applies the current Alembic migration before Pytest. Use a disposable
development database because integration tests create and remove fixture data.

Backend tests cover authentication/RBAC, schema migrations, uploads and data
quality, deterministic demo fixtures, cases/readiness, baselines, forecast
adapter contracts and TimesFM normalization/failure, evidence, interpretation,
classification, investigation, simulations, executive output, attributed review,
feedback, exports, admin metadata, security configuration, idempotency, and A–I
scenario journeys.

Use a disposable PostgreSQL database. Tests never require TimesFM weights or real
client data; provider integration remains isolated behind the adapter. Before a
release, build both container images, run `scripts/smoke-test.sh`, audit production
Python/npm dependencies, scan secrets, and rehearse backup/restore in staging.
