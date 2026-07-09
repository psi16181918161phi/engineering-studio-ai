"""WHAT: The FastAPI application instance serving the command-and-control
API and the static frontend dashboard.
WHY: Single-process, single-command deploy story: `uvicorn
engineering_studio.webapp:app` serves both the JSON/SSE API under /api and
the frontend/ static assets at "/" — one URL, one running process, per the
"one central engineering interface" requirement.
HOW: API routers are registered before the catch-all StaticFiles mount so
/api/* always resolves to a route handler first; the frontend/ directory
is only mounted if it exists (keeps CLI-only / test environments working
without it). `.env` is loaded here too — mirrors cli.py's `load_dotenv()`
call so FIREWORKS_API_KEY etc. are picked up whether the pipeline is
launched via the CLI or via uvicorn.
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from engineering_studio.api.downloads import router as downloads_router
from engineering_studio.api.health import router as health_router
from engineering_studio.api.runs import router as runs_router

load_dotenv()

# WHAT: Path to the sibling root-level frontend/ folder.
# HOW: src/engineering_studio/webapp/app.py -> parents[0]=webapp,
# [1]=engineering_studio, [2]=src, [3]=repo root (mirrors task_specs.py's
# parents[2]-from-src/engineering_studio/task_specs.py convention).
_FRONTEND_DIR = Path(__file__).resolve().parents[3] / "frontend"

app = FastAPI(title="Engineering Studio AI — Command & Control")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(runs_router)
app.include_router(downloads_router)

if _FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=_FRONTEND_DIR, html=True), name="frontend")
