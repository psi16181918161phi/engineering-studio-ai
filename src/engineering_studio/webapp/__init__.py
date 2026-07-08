"""WHAT: Package marker for the web application instance; re-exports `app`.
WHY: Separates "the runnable app" (this package) from "the routes it
serves" (`engineering_studio.api`), per AGENTS.md SS1 single-responsibility
modules, while still letting `uvicorn engineering_studio.webapp:app` find
the FastAPI instance without reaching into `webapp.app` directly.
HOW: The actual `FastAPI()` construction lives in `webapp/app.py`; this
file just re-exports it.
"""

from engineering_studio.webapp.app import app

__all__ = ["app"]
