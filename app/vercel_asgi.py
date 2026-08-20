"""Vercel-compatible Python serverless entrypoint for the Reflex backend.

Vercel's Python runtime imports a module and looks for a module-level
``app`` (or ``handler``) object that is a WSGI/ASGI application. Reflex's
``rx.App`` is not itself the ASGI application: the ASGI app lives on the
``rx.App`` instance (``api`` / ``_api`` / ``asgi_app`` depending on the
Reflex version). Importing ``app.app`` directly therefore crashes on
Vercel with "issue with ASGI application" / "no attribute" errors.

This module resolves the real ASGI application in a version-tolerant way
and exposes it as both ``app`` and ``handler`` so it can be used as the
serverless function entrypoint, e.g. in ``api/index.py``::

    from app.vercel_asgi import app  # noqa: F401

All environment variables (SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY,
REFLEX_DB_URL, OAuth base-URL overrides, ...) are read at runtime by the
existing app code, so nothing needs to be duplicated here. No UI, route,
state or auth behavior is modified by this module.
"""

import logging

from app.app import app as reflex_app

_ASGI_ATTRS: tuple[str, ...] = ("api", "_api", "asgi_app", "_asgi_app")


def _resolve_asgi_app(reflex_application: object) -> object:
    """Return the ASGI callable served by a Reflex application object."""
    for attr in _ASGI_ATTRS:
        candidate = getattr(reflex_application, attr, None)
        if candidate is not None and callable(candidate):
            logging.info(
                f"Vercel entrypoint: serving Reflex ASGI app via '{attr}'"
            )
            return candidate
    if callable(reflex_application):
        logging.info(
            "Vercel entrypoint: serving Reflex application object directly"
        )
        return reflex_application
    raise RuntimeError(
        "Unable to resolve the Reflex ASGI application from rx.App; "
        f"tried attributes: {', '.join(_ASGI_ATTRS)}"
    )


def _prepare(reflex_application: object) -> None:
    """Best-effort state/route setup so cold starts serve a ready app."""
    for method_name in ("_enable_state", "_apply_decorated_pages"):
        method = getattr(reflex_application, method_name, None)
        if callable(method):
            try:
                method()
            except Exception as e:
                logging.exception(
                    f"Vercel entrypoint: {method_name} skipped: {e}"
                )


_prepare(reflex_app)

# ASGI application exposed to the Vercel Python runtime.
app = _resolve_asgi_app(reflex_app)

# Some Vercel templates look for `handler` instead of `app`.
handler = app

__all__ = ["app", "handler"]
