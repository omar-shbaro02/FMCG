#!/usr/bin/env sh
set -eu
test "$#" -eq 1 || { echo "usage: restore.sh BACKUP.sql.gz" >&2; exit 2; }
test -n "${DATABASE_URL:-}" || { echo "DATABASE_URL is required" >&2; exit 2; }
test -f "$1" || { echo "backup file not found" >&2; exit 2; }
gzip -dc "$1" | psql -v ON_ERROR_STOP=1 "$DATABASE_URL"
