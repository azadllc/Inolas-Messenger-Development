"""Vercel serverless function entrypoint (canonical source of ``api/index.py``).

Vercel's Python runtime imports the module at ``api/index.py`` in the
repository root and serves its module-level ``app`` object as an ASGI
application. This file is byte-identical to what
``python -m app.vercel_setup`` writes to that path; it lives under ``app/``
because this workspace can only write files there.

The root resolution below walks up to the directory containing ``rxconfig.py``
(the repository root), so the module imports ``app.vercel_asgi`` correctly both
from ``<root>/api/index.py`` and from ``<root>/app/api/index.py``.

No UI, route, state, Supabase, Google OAuth or messenger behavior is changed
here: this module only re-exports the already resolved ASGI app plus a
``handler`` alias for Vercel templates that look for that name.
"""

import sys
from pathlib import Path


def _project_root() -> Path:
    """Locate the project root (the nearest parent holding ``rxconfig.py``)."""
    here = Path(__file__).resolve()
    for candidate in here.parents:
        if (candidate / "rxconfig.py").exists():
            return candidate
    for candidate in here.parents:
        if (candidate / "app" / "vercel_asgi.py").exists():
            return candidate
    return here.parent.parent


_ROOT = str(_project_root())
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app.vercel_asgi import app, handler  # noqa: E402,F401

__all__ = ["app", "handler"]
