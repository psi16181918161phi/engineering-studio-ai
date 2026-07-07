# `engineering_studio/webapp/` — FastAPI + Jinja2 server-rendered app (W6a)

WHAT: `create_app()` in [`__init__.py`](__init__.py) builds a FastAPI app
with two human-facing routes — `GET /` (a brief-submission form) and
`POST /run` (submits it) — plus `GET /pipeline/{id}` to re-view a prior
result. Every route consumes [`../api/`](../api/README.md)'s app
in-process (via an `httpx.AsyncClient` over `httpx.ASGITransport` — no
real socket, no separate server process); this package never calls the
SDK or orchestrator directly.
WHY: Keeps "there is a runnable web app" (this package) separate from
"here are the routes it serves" (`../api/`) and from Role 5's
[`frontend/`](../../../frontend/README.md) (client-side UI/dashboard),
per `AGENTS.md` §1 (single-responsibility modules).
HOW: Server-rendered [`templates/`](templates/) (Jinja2, no separate JS
build toolchain per PREPLAN Q4), styled exclusively from
`utils.palette.PALETTE_B` (Variant B interface-surface palette) passed
into the template context — no template hard-codes a color literal.
100% test coverage in
[`../../../tests/test_webapp.py`](../../../tests/test_webapp.py).

## Ownership

Role 3 (AI Pipeline & Backend Engineering) — see
[`SCAFFOLDING.md`](../../../SCAFFOLDING.md) §2 and §3.3. Role 5
(Frontend) is the primary *consumer* of this surface, not its owner.

## Related

- [`../api/README.md`](../api/README.md) — the routes this app would mount.
- [`../../../frontend/README.md`](../../../frontend/README.md) — the
  client-side UI this app would serve or be consumed by.
