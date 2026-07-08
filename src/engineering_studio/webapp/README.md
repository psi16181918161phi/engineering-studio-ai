# `engineering_studio/webapp/` — web application instance

WHAT: The ASGI application instance (`app.py`, a FastAPI `app = FastAPI()`)
that mounts the routes defined in [`../api/`](../api/README.md) and serves
[`frontend/`](../../../frontend/README.md) as static files at `/`.
WHY: Keeps "there is a runnable web app" (this package) separate from
"here are the routes it serves" (`../api/`) and from Role 5's
[`frontend/`](../../../frontend/README.md) (client-side UI/dashboard),
per `AGENTS.md` §1 (single-responsibility modules).
HOW: `app.py` constructs the FastAPI instance, adds permissive CORS
middleware (safe default for a hackathon demo; tighten `allow_origins`
before any non-demo deployment), includes the `../api/` routers, then
mounts `frontend/` as static files — in that order, so `/api/*` always
resolves to a route handler before the catch-all static mount is
considered. `__init__.py` re-exports `app` so
`uvicorn engineering_studio.webapp:app` finds it directly. Run it with:

```powershell
uvicorn engineering_studio.webapp:app --reload --app-dir src
```

## Ownership

Role 3 (AI Pipeline & Backend Engineering) — see
[`SCAFFOLDING.md`](../../../SCAFFOLDING.md) §2 and §3.3. Role 5
(Frontend) is the primary *consumer* of this surface, not its owner.

## Related

- [`../api/README.md`](../api/README.md) — the routes this app would mount.
- [`../../../frontend/README.md`](../../../frontend/README.md) — the
  client-side UI this app would serve or be consumed by.
