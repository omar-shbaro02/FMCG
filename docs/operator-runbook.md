# Operator runbook

Check `/health`, then admin `/api/admin/health`, `/jobs`, and `/audit-events`.
For a failed forecast, preserve its structured error, confirm adapter/model
availability, and return the case to a legal retry path; never fabricate output.
For database incidents, stop writes, take a backup, restore into a new database,
run `alembic upgrade head`, smoke test, then redirect traffic. For compromised
credentials, rotate `SECRET_KEY` and user credentials, restart all replicas, and
review audit events. Do not edit reviewed outputs; generate a new version.

Backup: `scripts/backup.sh <destination.sql.gz>`. Restore into a clean target:
`scripts/restore.sh <backup.sql.gz>`. Both require explicit database environment
variables and refuse ambiguous input.
