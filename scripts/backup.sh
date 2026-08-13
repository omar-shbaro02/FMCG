#!/usr/bin/env sh
set -eu
test "$#" -eq 1 || { echo "usage: backup.sh DESTINATION.sql.gz" >&2; exit 2; }
test -n "${DATABASE_URL:-}" || { echo "DATABASE_URL is required" >&2; exit 2; }
case "$1" in *.sql.gz) ;; *) echo "destination must end in .sql.gz" >&2; exit 2;; esac
pg_dump "$DATABASE_URL" | gzip -c > "$1"
