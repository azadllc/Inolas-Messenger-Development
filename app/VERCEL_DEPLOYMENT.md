# Vercel deployment (Python serverless entrypoint)

The Reflex backend crashed on Vercel because the serverless function imported
`app.app`, which exposes an `rx.App` instance — not an ASGI application. The
Vercel Python runtime requires a module-level ASGI/WSGI callable named `app`
(or `handler`).

`app/vercel_asgi.py` fixes that: it imports the existing Reflex app, resolves
the underlying ASGI application in a version-tolerant way, and exports it as
both `app` and `handler`. Nothing about the UI, routes, state, auth flows or
messenger interface changes.

## Create the project-root files (one command)

Vercel reads the function entrypoint and its configuration only from the
project root — in this workspace that is the current directory containing
`rxconfig.py` — and this workspace can only write files under `app/`. Run the
root-generation helper once from that directory:

```bash
python -m app.vercel_setup          # add --force to overwrite existing files
python -m app.vercel_setup --root /path/to/project   # explicit root
```

The helper resolves the project root from `Path.cwd()` (walking up only if
needed until it finds `rxconfig.py`), never relative to the `app` package, and
prints the root it used. It writes:

- `api/index.py` — resolves the repository root, adds it to `sys.path` safely,
  and re-exports the ASGI application from `app/vercel_asgi.py` as both `app`
  and `handler`.
- `vercel.json` — builds `api/index.py` with `@vercel/python` on the supported
  `python3.12` runtime (50 MB lambda size) and rewrites every path to that
  function.

The generated files are copied straight from the canonical, reviewable sources
kept in this package: `app/api/index.py` (imports `app.vercel_asgi`) and
`app/vercel.json.txt`. An existing but **empty** root `vercel.json` is filled in
automatically, without `--force`.

If you prefer copying by hand:

```bash
mkdir -p api
cp app/api/index.py api/index.py
cp app/vercel.json.txt vercel.json
```

The required root `vercel.json` content is exactly:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "runtime": "python3.12",
        "maxLambdaSize": "50mb"
      }
    }
  ],
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/api/index.py"
    }
  ]
}
```

After generation the project root contains:

```
vercel.json
api/index.py
requirements.txt
rxconfig.py
app/...
```

The catch-all rewrite (`/(.*)` → `/api/index.py`) keeps every existing route
working, including `/`, `/onboarding`, `/home` and the OAuth callback at
`/auth/callback`.

Deploying is then just: push the repository and import it into a Vercel project
(or run `vercel --prod`). Dependencies are installed from the existing root
`requirements.txt`.

## Environment variables

Set the app's existing variables in the Vercel project (Settings →
Environment Variables). No values are hardcoded anywhere:

- `SUPABASE_URL`, `SUPABASE_KEY`
- `OPENAI_API_KEY`
- `REFLEX_DB_URL` (if used)
- Google OAuth credentials already configured for the app

## OAuth base URL

The callback resolver in `app/states/auth_state.py` already reads hosting
base-URL variables in priority order, including Vercel's automatically
provided `VERCEL_PROJECT_PRODUCTION_URL` and `VERCEL_URL`. For a stable
custom domain, set an explicit override so previews and production agree with
the Supabase redirect allow-list:

```
OAUTH_REDIRECT_URL=https://your-domain.com/auth/callback
```

or

```
APP_BASE_URL=https://your-domain.com
```

Add the resulting `https://<host>/auth/callback` URL to the Supabase Auth
redirect URLs list.
