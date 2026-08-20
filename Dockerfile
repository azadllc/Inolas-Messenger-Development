# Single-container production image for a full, stateful Reflex app.
# Serves the exported frontend and the Reflex backend behind ONE public port
# via Caddy, so WebSockets (/_event) and HTTP share the same origin.

FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    NODE_OPTIONS=--max-old-space-size=2048 \
    PORT=8080 \
    BACKEND_PORT=8000

# Build-time public origin: baked into the exported frontend bundle.
ARG API_URL=http://localhost:8080
ARG APP_BASE_URL=${API_URL}
ENV API_URL=${API_URL} \
    APP_BASE_URL=${APP_BASE_URL}

# System deps: curl/unzip for the Reflex bun/node bootstrap, caddy as front door.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        build-essential curl unzip ca-certificates gnupg debian-keyring debian-archive-keyring apt-transport-https \
 && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
        | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg \
 && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
        > /etc/apt/sources.list.d/caddy-stable.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends caddy \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencies first for layer caching.
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Application source (rxconfig.py + the `app` package are already part of the
# project, so no scaffolding/initialization step is needed or wanted here).
COPY . .

# Export the static frontend bundle into .web/build/client.
# API_URL/APP_BASE_URL come from the build args above and are baked in.
RUN API_URL=${API_URL} APP_BASE_URL=${APP_BASE_URL} \
    reflex export --frontend-only --no-zip --loglevel info

RUN chmod +x ./start.sh || true

EXPOSE 8080

# Caddy on $PORT + `reflex run --env prod --backend-only` on $BACKEND_PORT.
CMD ["bash", "./start.sh"]
