#!/usr/bin/env bash
# Production entrypoint: Reflex backend (0.0.0.0:$BACKEND_PORT) behind Caddy on $PORT.
set -euo pipefail

export PORT="${PORT:-8080}"
export BACKEND_PORT="${BACKEND_PORT:-8000}"

# Public origin used by the frontend bundle and OAuth callbacks.
export API_URL="${API_URL:-http://localhost:${PORT}}"
export APP_BASE_URL="${APP_BASE_URL:-${DEPLOY_URL:-$API_URL}}"
export DEPLOY_URL="${DEPLOY_URL:-$APP_BASE_URL}"

echo "[start] PORT=${PORT} BACKEND_PORT=${BACKEND_PORT}"
echo "[start] API_URL=${API_URL}"
echo "[start] APP_BASE_URL=${APP_BASE_URL}"

# Some hosts only reveal the public domain after the first deploy: rebuild the
# frontend at boot with the real API_URL when asked.
if [ "${REFLEX_EXPORT_ON_START:-0}" = "1" ]; then
  echo "[start] re-exporting frontend with API_URL=${API_URL}"
  API_URL="${API_URL}" APP_BASE_URL="${APP_BASE_URL}" \
    reflex export --frontend-only --no-zip --loglevel info
fi

FRONTEND_DIR="${FRONTEND_DIR:-/app/.web/build/client}"
export FRONTEND_DIR

start_backend() {
  exec reflex run \
    --env prod \
    --backend-only \
    --backend-host 0.0.0.0 \
    --backend-port "${BACKEND_PORT}" \
    --loglevel info
}

if command -v caddy >/dev/null 2>&1 && [ -f /app/Caddyfile ]; then
  caddy start --config /app/Caddyfile --adapter caddyfile
  trap 'caddy stop || true' EXIT INT TERM
  start_backend
else
  # No front door available: serve the backend directly on the public port.
  echo "[start] caddy/Caddyfile unavailable - binding backend to public PORT"
  export BACKEND_PORT="${PORT}"
  start_backend
fi
