# Deployment guide

## Environment checklist

- `ENVIRONMENT=production`
- Unique `SECRET_KEY` of at least 32 characters
- Unique bootstrap credential or disabled/bootstrap replacement process
- Managed PostgreSQL and Redis URLs with TLS
- Exact HTTPS `FRONTEND_URL` and API origin
- Persistent upload storage, encryption, retention, malware scanner
- `FORECAST_ADAPTER=timesfm` only after model provenance and capacity validation
- Edge TLS, distributed rate limiting, request-size limit, logs/metrics/alerts
- Tested backup destination and restore credentials

## Release

Build immutable images, run dependency/secret scans and all checks, migrate a
staging database, start API, then frontend. Run `scripts/smoke-test.sh <api-url>
<frontend-url>`. Deploy migration before compatible application code; never run
two incompatible schemas. Example reverse proxy is `deploy/nginx.conf`.

## Backup, restore, rollback

Take a database backup before migration. `scripts/backup.sh` and
`scripts/restore.sh` require `DATABASE_URL`. To roll back, stop writes, restore
the pre-release backup if the migration is not backward-compatible, deploy the
previous immutable image tags, verify `/health`, login, case retrieval, and one
draft export. Preserve audit records and incident notes.

The included worker command truthfully reports unconfigured until distributed
jobs are implemented; do not advertise asynchronous processing in production.
