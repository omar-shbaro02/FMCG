#!/usr/bin/env sh
set -eu
test "$#" -eq 2 || { echo "usage: smoke-test.sh API_URL FRONTEND_URL" >&2; exit 2; }
curl --fail --silent --show-error "$1/health" >/dev/null
curl --fail --silent --show-error "$1/openapi.json" >/dev/null
curl --fail --silent --show-error "$2" >/dev/null
echo "smoke test passed"
