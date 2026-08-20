# Single-container production image for the Reflex app.
#
# One container serves BOTH the compiled Reflex frontend (static files) and the
# Reflex backend (event websocket + upload endpoints) on ONE port, so it fits
# hosts that expose a single $PORT: Render, Railway, Fly.io, Cloud Run, Docker.
#
# Layout inside the image:
#   Caddy  -> listens on $PORT (default 8080), serves .web/build/client and
#             reverse-proxies backend paths to 127.0.0.1:8000 (WebSockets pass
#             through automatically).
#   Reflex -> `reflex run --env prod --backend-only` on 127.0.0.1:8000.
#
# Python 3.12 slim is used deliberately: it matches the runtime pinned in
# vercel.json (`python3.12`) and is the version Reflex and its dependency set
# are most widely tested against, so container and serverless runs agree.
#
# Build (bake the public URL into the frontend bundle):
#   docker build --build-arg API_URL=https://your-domain.com -t inolas-messenger .
# Run:
#   docker run -p 8080:8080 --env-file .env -e API_URL=https://your-domain.com inolas-messenger

FROM caddy:2-alpine AS caddy_bin

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    NODE_OPTIONS=--max-old-space-size=2048 \
    TELEMETRY_ENABLED=false \
    PORT=8080 \
    BACKEND_PORT=8000

# `reflex export` downloads and runs bun/node to build the frontend, so curl,
# unzip and git must be present at build time.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl unzip git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=caddy_bin /usr/bin/caddy /usr/bin/caddy

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Public base URL of the deployment. It is baked into the exported frontend so
# the browser knows where to open the backend websocket. When the domain is only
# known at runtime, leave it empty and start the container with
# REFLEX_EXPORT_ON_START=1 plus API_URL set.
ARG API_URL=""
ENV API_URL=${API_URL}

# Compile the frontend once at build time (fast, deterministic cold starts).
RUN reflex export --frontend-only --no-zip

RUN mkdir -p /etc/caddy /app/uploaded_files \
    && cp Caddyfile /etc/caddy/Caddyfile \
    && chmod +x start.sh

EXPOSE 8080

CMD ["./start.sh"]
