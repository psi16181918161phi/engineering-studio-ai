# `engineering_studio/webapp/` — web application instance (reserved)

WHAT: Reserved package for the ASGI/WSGI application instance (e.g. a
FastAPI `app = FastAPI()`) that would mount the routes defined in
[`../api/`](../api/README.md), if the demo needs a browser-facing
surface fed directly by this package rather than root
[`frontend/`](../../../frontend/README.md).
WHY: Keeps "there is a runnable web app" (this package) separate from
"here are the routes it serves" (`../api/`) and from Role 5's
[`frontend/`](../../../frontend/README.md) (client-side UI/dashboard),
per `AGENTS.md` §1 (single-responsibility modules).
HOW: Currently an empty placeholder (`__init__.py` only) — a valid end
state if the demo ships CLI-only or `../cli/`-driven. When populated,
this module constructs and configures the app instance; `../api/`
supplies the route handlers it mounts.

## Ownership

Role 3 (AI Pipeline & Backend Engineering) — see
[`SCAFFOLDING.md`](../../../SCAFFOLDING.md) §2 and §3.3. Role 5
(Frontend) is the primary *consumer* of this surface, not its owner.

## Related

- [`../api/README.md`](../api/README.md) — the routes this app would mount.
- [`../../../frontend/README.md`](../../../frontend/README.md) — the
  client-side UI this app would serve or be consumed by.
