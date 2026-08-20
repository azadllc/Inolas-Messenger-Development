#!/usr/bin/env sh
# Container entrypoint: one port, frontend + backend, WebSockets enabled.
#
#   Caddy   -> $PORT (host-assigned), static frontend + reverse proxy
#   Reflex  -> 127.0.0.1:$BACKEND_PORT, backend only (event websocket)
#
# The frontend is served as static files by Caddy, so there is no Reflex dev
# server and no FRONTEND_PORT to expose: only $PORT is public.
set -eu

PORT="${PORT:-8080}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
export PORT BACKEND_PORT

echo "[start] public port: ${PORT} | backend port: ${BACKEND_PORT}"
echo "[start] API_URL: ${API_URL:-<unset: frontend will use its baked value>}"

# Optional runtime frontend rebuild for hosts where the public domain is only
# known at deploy time (set REFLEX_EXPORT_ON_START=1 and API_URL).
if [ "${REFLEX_EXPORT_ON_START:-0}" = "1" ]; then
    echo "[start] rebuilding frontend for API_URL=${API_URL:-}"
    reflex export --frontend-only --no-zip
fi

if [ ! -d ".web/build/client" ]; then
    echo "[start] frontend build missing, exporting now..."
    reflex export --frontend-only --no-zip
fi

CADDYFILE="/etc/caddy/Caddyfile"
if [ ! -f "$CADDYFILE" ]; then
    CADDYFILE="./Caddyfile"
fi

echo "[start] launching caddy with ${CADDYFILE}"
caddy start --config "$CADDYFILE" --adapter caddyfile

echo "[start] launching reflex backend"
exec reflex run \
    --env prod \
    --backend-only \
    --backend-host 0.0.0.0 \
    --backend-port "$BACKEND_PORT"
