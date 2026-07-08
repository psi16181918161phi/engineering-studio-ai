"""WHAT: Package marker for the HTTP/SSE API layer.
WHY: Reserves the import path (`engineering_studio.api`) for the route
modules that live alongside this file; keeps transport code separate
from `agents.orchestrator` per AGENTS.md SS1.
HOW: No routes are defined here -- `webapp/app.py` imports the `router`
objects directly from `api.health` and `api.runs` and includes them on
the shared FastAPI instance. See `README.md` in this folder for the
current route inventory.
"""
