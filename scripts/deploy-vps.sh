#!/usr/bin/env sh
set -eu

APP_DIR="${APP_DIR:-/opt/ms-poc}"
DEPLOY_REF="${DEPLOY_REF:-origin/main}"
WEB_PORT="${WEB_PORT:-8086}"
GITHUB_REPO="${GITHUB_REPO:-farukzahra/ms-poc}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

cd "$APP_DIR"

sync_repo() {
  if [ -n "${GITHUB_TOKEN:-}" ]; then
    git fetch "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git" \
      "+refs/heads/*:refs/remotes/origin/*" --prune
  else
    git fetch --all --prune
  fi
  git reset --hard "$DEPLOY_REF"
}

ensure_docker() {
  if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    return 0
  fi
  echo "Docker or Docker Compose not found on VPS." >&2
  exit 1
}

ensure_env() {
  if [ ! -f .env ]; then
    echo "Missing .env in $APP_DIR - copy from .env.production.example and fill Azure keys." >&2
    exit 1
  fi
}

deploy_stack() {
  docker compose -f "$COMPOSE_FILE" build
  docker compose -f "$COMPOSE_FILE" up -d --remove-orphans
}

health_check() {
  for i in 1 2 3 4 5 6; do
    if curl -fsS "http://127.0.0.1:${WEB_PORT}/api/health" | grep -q '"status":"ok"'; then
      curl -fsS "http://127.0.0.1:${WEB_PORT}/" | grep -q "Enterprise AI Sales Intelligence"
      echo "OK: ms-poc on 127.0.0.1:${WEB_PORT}"
      return 0
    fi
    sleep 10
  done
  echo "Health check failed after 60s" >&2
  exit 1
}

sync_repo
ensure_docker
ensure_env
deploy_stack
health_check

docker image prune -f
