# frontend/ — Role 5 (Frontend, Visualization & Demonstration)

WHAT: Owned exclusively by Role 5. Web UI, dashboard, log/artifact
viewer, and any live visualization surface. Now populated with a working
**command-and-control dashboard** for the agent pipeline (see below) —
plain HTML/CSS/JS, no build step, per the framework guidance that follows.
WHY: Isolated from `src/engineering_studio/` (Role 3) so Role 5 can move
fast without touching backend files — see `../SCAFFOLDING.md` §2.
HOW: Framework choice (React/Vue/plain HTML+JS/etc.) is intentionally
**not** prescribed here — pick whatever you can ship fastest in the
hackathon window. Plain HTML/CSS/JS was chosen for the shipped dashboard
for exactly that reason. The one non-negotiable is the locked color
palette in `styles/theme.css`.

## Running the dashboard

The dashboard is a static site that talks to the FastAPI command-and-control
API in `src/engineering_studio/api/` and `src/engineering_studio/webapp/`.
The simplest path serves both from one process:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env   # then fill in FIREWORKS_API_KEY
uvicorn engineering_studio.webapp:app --reload --app-dir src
```

Then open <http://127.0.0.1:8000/>. The FastAPI app mounts this `frontend/`
folder as static files at `/` and exposes the JSON/SSE API under `/api/`
(see `../src/engineering_studio/api/README.md`), so there is exactly one
URL to open — no separate frontend dev server or CORS setup required for
normal use.

If you do want to iterate on the frontend with a separate static server
(e.g. `python -m http.server 5500` from this folder) while `uvicorn` runs
on port 8000, that also works: the API has permissive CORS enabled.

## Files in this folder

| File | Purpose |
|---|---|
| `index.html` | The command-and-control dashboard shell: brief-launch form, live pipeline grid, run history. |
| `app.js` | All client logic — launches runs, subscribes to `/api/runs/{id}/stream` (SSE), renders per-agent status and artifacts. No build step; vanilla JS. |
| `styles/app.css` | Layout and component styles built on top of the locked palette. State (pending/running/done/error/skipped) is conveyed via border style + icon + text, never color alone. |
| `styles/theme.css` | The three **locked** brand colors as CSS custom properties — import this into whatever framework you choose. |

## What the dashboard shows

One card per pipeline stage (Research → Mechanical/Electrical/Firmware/
Simulation in parallel → Cost/Business/Legal → Challenge Division →
Quality Gate), each with a live status badge and a "View output" toggle
that lazily fetches that stage's artifact text. The Quality Gate is the
only stage that can bring the run to certified completion — the banner
above the pipeline grid reflects that once the run finishes.

## Mandatory color palette

Per `../docs/TEAM_QA.md` §4 (and `coding_stds/visualization/aesthetic_standards.txt`
in the private standards repo):

- `#FFAEC9` — foreground or background (soft rose pink)
- `#000000` — background or foreground (near-black)
- `#B76E79` — accents only (rose gold)

Never use a fourth "convenience" color without checking with Role 6/Role 1
first — one consistent palette across every surface (CLI output, web
viewer, diagrams) is part of the aesthetics standard.

## Accessibility

Whatever palette combination you use, verify WCAG 2.1 AA contrast ratios
(4.5:1 for normal text, 3:1 for large text/UI components) — color must
never be the sole means of conveying information (`../docs/TEAM_QA.md` §4).

## What you consume from the backend

Read-only: `src/engineering_studio/artifacts/<discipline>/output.md`
files (written by Role 3's `SpecialistAgent`) and/or the CLI's exported
report. Do not write into `src/engineering_studio/`.
