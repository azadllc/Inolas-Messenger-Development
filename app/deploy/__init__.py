"""Canonical deployment file sources.

Each ``*.txt`` file in this package is the reviewable source of a
project-root deployment file (``Dockerfile``, ``.dockerignore``,
``start.sh``, ``Caddyfile``, ``docker-compose.yml``, ``render.yaml``,
``railway.json``, ``fly.toml``, ``.env.example``).

Run ``python -m app.deploy_setup`` from the project root to materialize them.
They exist here as ``.txt`` because this workspace can only write text files
inside the ``app/`` package.
"""
