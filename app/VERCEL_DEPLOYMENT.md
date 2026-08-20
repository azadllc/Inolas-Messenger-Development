# Vercel deployment (Python serverless entrypoint)

The Reflex backend crashed on Vercel because the serverless function imported
`app.app`, which exposes an `rx.App` instance — not an ASGI application. The
Vercel Python runtime requires a module-level ASGI/WSGI callable named `app`
(or `handler`).

`app/vercel_asgi.py` fixes that: it imports the existing Reflex app, resolves
the underlying ASGI application in a version-tolerant way, and exports it as
both `app` and `handler`. Nothing about the UI, routes, state, auth flows or
messenger interface changes.

## Repository-root files to add

Vercel requires these two files at the repository root (they cannot be created
inside `app/`):

`api/index.py`

```python
from app.vercel_asgi import app  # noqa: F401
```

`vercel.json`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": { "runtime": "python3.12", "maxLambdaSize": "50mb" }
    }
  ],
  "rewrites": [{ "source": "/(.*)", "destination": "/api/index.py" }]
}
```

The catch-all rewrite keeps every existing route working, including `/`,
`/onboarding`, `/home` and the OAuth callback at `/auth/callback`.

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
