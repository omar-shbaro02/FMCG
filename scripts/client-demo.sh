#!/usr/bin/env bash
set -euo pipefail

repository_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repository_dir"

runtime=""
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  compose=(docker compose)
  runtime="compose"
elif command -v podman-compose >/dev/null 2>&1; then
  compose=(podman-compose)
  runtime="compose"
elif command -v podman >/dev/null 2>&1; then
  runtime="podman"
else
  echo "Docker Compose v2 or Podman is required." >&2
  exit 1
fi

command_name="${1:-start}"

if [[ "$runtime" == "compose" ]]; then
  demo_compose=("${compose[@]}" -p fmcg-client-demo -f docker-compose.yml -f docker-compose.demo.yml)
  case "$command_name" in
    start)
      if [[ ! -f .env ]]; then
        cp .env.example .env
        echo "Created .env from the safe local-development example."
      fi
      "${demo_compose[@]}" up -d --build --wait database redis api frontend
      "${demo_compose[@]}" exec -T api env PYTHONPATH=/app python /demo/scripts/prepare_client_demo.py prepare
      echo
      echo "Client demo is ready at http://localhost:3000"
      echo "Login: admin@example.com / development-admin-only"
      ;;
    check)
      "${demo_compose[@]}" exec -T api env PYTHONPATH=/app python /demo/scripts/prepare_client_demo.py check
      ;;
    logs)
      "${demo_compose[@]}" logs -f api frontend
      ;;
    stop)
      "${demo_compose[@]}" down
      ;;
    reset)
      "${demo_compose[@]}" down --volumes --remove-orphans
      echo "Removed only the isolated fmcg-client-demo containers and volumes."
      ;;
    *)
      echo "Usage: $0 {start|check|logs|stop|reset}" >&2
      exit 2
      ;;
  esac
  exit 0
fi

network="fmcg-client-demo"
database_container="fmcg-client-demo-database"
redis_container="fmcg-client-demo-redis"
api_container="fmcg-client-demo-api"
frontend_container="fmcg-client-demo-frontend"
database_volume="fmcg-client-demo-postgres"
uploads_volume="fmcg-client-demo-uploads"

remove_demo_containers() {
  for container in "$frontend_container" "$api_container" "$redis_container" "$database_container"; do
    if podman container exists "$container"; then
      podman rm -f "$container" >/dev/null
    fi
  done
}

wait_for_api() {
  for _ in $(seq 1 60); do
    if podman exec "$api_container" python -c \
      "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" \
      >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  echo "API did not become healthy. Run: make demo-logs" >&2
  return 1
}

case "$command_name" in
  start)
    remove_demo_containers
    podman network exists "$network" || podman network create "$network" >/dev/null
    podman volume exists "$database_volume" || podman volume create "$database_volume" >/dev/null
    podman volume exists "$uploads_volume" || podman volume create "$uploads_volume" >/dev/null
    podman build -t localhost/fmcg-client-demo-api backend
    podman build -t localhost/fmcg-client-demo-frontend frontend
    podman run -d --name "$database_container" --network "$network" --network-alias database \
      -e POSTGRES_DB=fmcg -e POSTGRES_USER=fmcg -e POSTGRES_PASSWORD=fmcg \
      -v "$database_volume:/var/lib/postgresql/data" postgres:16-alpine >/dev/null
    podman run -d --name "$redis_container" --network "$network" --network-alias redis \
      redis:7-alpine >/dev/null
    podman run -d --name "$api_container" --network "$network" --network-alias api \
      -p 8000:8000 \
      -e ENVIRONMENT=development \
      -e DATABASE_URL=postgresql+psycopg://fmcg:fmcg@database:5432/fmcg \
      -e REDIS_URL=redis://redis:6379/0 \
      -e FRONTEND_URL=http://localhost:3000 \
      -e SECRET_KEY=local-client-demo-secret-key-at-least-32-characters \
      -e BOOTSTRAP_ADMIN_EMAIL=admin@example.com \
      -e BOOTSTRAP_ADMIN_PASSWORD=development-admin-only \
      -e FORECAST_ADAPTER=mock \
      -e UPLOAD_DIRECTORY=/app/var/uploads \
      -v "$uploads_volume:/app/var/uploads" \
      -v "$repository_dir/fixtures:/demo/fixtures:ro,z" \
      -v "$repository_dir/scripts:/demo/scripts:ro,z" \
      localhost/fmcg-client-demo-api >/dev/null
    wait_for_api
    podman run -d --name "$frontend_container" --network "$network" \
      -p 3000:3000 -e API_INTERNAL_URL=http://api:8000 \
      localhost/fmcg-client-demo-frontend >/dev/null
    podman exec "$api_container" env PYTHONPATH=/app \
      python /demo/scripts/prepare_client_demo.py prepare
    echo
    echo "Client demo is ready at http://localhost:3000"
    echo "Login: admin@example.com / development-admin-only"
    ;;
  check)
    podman exec "$api_container" env PYTHONPATH=/app \
      python /demo/scripts/prepare_client_demo.py check
    ;;
  logs)
    echo "Following API logs. Frontend logs: podman logs $frontend_container" >&2
    podman logs -f "$api_container"
    ;;
  stop)
    for container in "$frontend_container" "$api_container" "$redis_container" "$database_container"; do
      podman stop "$container" >/dev/null 2>&1 || true
    done
    ;;
  reset)
    remove_demo_containers
    podman network rm "$network" >/dev/null 2>&1 || true
    podman volume rm "$database_volume" "$uploads_volume" >/dev/null 2>&1 || true
    echo "Removed only the isolated fmcg-client-demo containers and volumes."
    ;;
  *)
    echo "Usage: $0 {start|check|logs|stop|reset}" >&2
    exit 2
    ;;
esac
