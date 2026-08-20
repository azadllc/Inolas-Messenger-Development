"""Project-root deployment files: committed content + optional regeneration.

The portable deployment files live at the **project root** (next to
``rxconfig.py``) in the saved project: ``Dockerfile``, ``.dockerignore``,
``start.sh``, ``Caddyfile``, ``docker-compose.yml``, ``render.yaml``,
``railway.json``, ``fly.toml``, ``.env.example``, ``DEPLOYMENT.md`` and
``vercel.json``. They are materialized automatically on app startup by
:func:`ensure_deployment_files` (called from ``app/app.py``) from the reviewable
sources in ``app/deploy/*.txt``, so a checkout of the saved project already
contains every file a host needs. Existing non-empty root files are never
overwritten, and ``api/index.py`` is left completely untouched.

Running this module by hand is **optional** — it is a convenience for
regenerating or force-refreshing those files, not a prerequisite for deploying::

    python -m app.deploy_setup             # optional; add --force to overwrite
    python -m app.deploy_setup --root /path/to/project

It copies the canonical sources in ``app/deploy/*.txt`` to their real root
filenames:

- ``Dockerfile``          single-container production image (frontend + backend)
- ``.dockerignore``       build-context excludes
- ``start.sh``            entrypoint: Caddy on ``$PORT`` + Reflex backend
- ``Caddyfile``           single-port front door, WebSocket pass-through
- ``docker-compose.yml``  local/VPS run
- ``render.yaml``         Render blueprint
- ``railway.json``        Railway service config
- ``fly.toml``            Fly.io machine config
- ``.env.example``        every environment variable the app reads
- ``DEPLOYMENT.md``       the supported deployment guide
- ``vercel.json``         best-effort serverless config (NOT the primary target)

Nothing about the application itself (UI, routes, state, Supabase, Google
OAuth, OpenAI, database access or messenger behavior) is touched.
"""

import argparse
import logging
import stat
import sys
from pathlib import Path

from app.vercel_setup import project_root, vercel_json_source

_PACKAGE_DIR = Path(__file__).resolve().parent
_DEPLOY_DIR = _PACKAGE_DIR / "deploy"

# canonical source (relative to app/) -> project-root destination
FILE_MAP: tuple[tuple[str, str], ...] = (
    ("deploy/Dockerfile.txt", "Dockerfile"),
    ("deploy/dockerignore.txt", ".dockerignore"),
    ("deploy/start.sh.txt", "start.sh"),
    ("deploy/Caddyfile.txt", "Caddyfile"),
    ("deploy/docker-compose.yml.txt", "docker-compose.yml"),
    ("deploy/render.yaml.txt", "render.yaml"),
    ("deploy/railway.json.txt", "railway.json"),
    ("deploy/fly.toml.txt", "fly.toml"),
    ("deploy/env.example.txt", ".env.example"),
    ("DEPLOYMENT.md", "DEPLOYMENT.md"),
)

EXECUTABLE_TARGETS: frozenset[str] = frozenset({"start.sh"})


def _read_source(relative_path: str) -> str | None:
    source = _PACKAGE_DIR / relative_path
    try:
        return source.read_text()
    except OSError as e:
        logging.exception(f"Error reading {source}: {e}")
        return None


def _make_executable(path: Path) -> None:
    try:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError as e:
        logging.exception(f"Error setting exec bit on {path}: {e}")


def _write(path: Path, content: str, force: bool) -> str:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not force:
            existing = path.read_text()
            if existing == content:
                result = f"unchanged: {path}"
            elif not existing.strip():
                # An empty placeholder is never a valid config: fill it in.
                path.write_text(content)
                result = f"wrote (was empty): {path}"
            else:
                return f"skipped (exists, use --force): {path}"
        else:
            path.write_text(content)
            result = f"wrote: {path}"
        if path.name in EXECUTABLE_TARGETS:
            _make_executable(path)
        return result
    except OSError as e:
        logging.exception(f"Error writing {path}: {e}")
        return f"failed: {path} ({e})"


def generate(force: bool = False, root: Path | None = None) -> list[str]:
    """Materialize every deployment file at the project root."""
    target = root.resolve() if root is not None else project_root()
    results = [f"project root: {target}"]
    for relative_source, destination in FILE_MAP:
        content = _read_source(relative_source)
        if content is None:
            results.append(f"failed: missing source {relative_source}")
            continue
        results.append(_write(target / destination, content, force))
    # Keep the root vercel.json valid rather than an empty, misleading file.
    results.append(_write(target / "vercel.json", vercel_json_source(), force))
    return results


def ensure_deployment_files(root: Path | None = None) -> list[str]:
    """Materialize missing/empty root deployment files (safe, non-destructive).

    Called once at app import time so the saved project root always contains the
    real deployment files. Existing non-empty files win, ``force`` is never
    used, and any failure is logged instead of breaking app startup.
    """
    try:
        return generate(force=False, root=root)
    except Exception as e:
        logging.exception(f"Error ensuring deployment files: {e}")
        return [f"failed: ensure_deployment_files ({e})"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Optional helper: (re)write the portable single-container deployment files "
            "(Dockerfile, Caddyfile, start.sh, host configs, DEPLOYMENT.md) "
            "to the project root."
        )
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing root deployment files.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Explicit project root (defaults to the detected cwd root).",
    )
    args = parser.parse_args()
    results = generate(
        force=args.force,
        root=Path(args.root) if args.root else None,
    )
    for line in results:
        print(line)
    return 1 if any(line.startswith("failed") for line in results) else 0


if __name__ == "__main__":
    sys.exit(main())
