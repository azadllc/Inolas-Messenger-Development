import os

import reflex as rx


def _origin(*names: str, default: str) -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            if not value.startswith(("http://", "https://")):
                value = f"https://{value}"
            return value.rstrip("/")
    return default


_backend_port = os.environ.get("BACKEND_PORT", "8000").strip() or "8000"

# Public backend/API origin (baked into the exported frontend bundle).
API_URL = _origin("API_URL", default=f"http://localhost:{_backend_port}")
# Public frontend origin.
DEPLOY_URL = _origin(
    "APP_BASE_URL",
    "DEPLOY_URL",
    "RENDER_EXTERNAL_URL",
    "RAILWAY_PUBLIC_DOMAIN",
    default="http://localhost:3000",
)

config = rx.Config(
    app_name="app",
    api_url=API_URL,
    deploy_url=DEPLOY_URL,
    plugins=[rx.plugins.SitemapPlugin(), rx.plugins.TailwindV4Plugin()],
)
