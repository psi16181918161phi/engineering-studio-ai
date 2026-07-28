# demo/_archive/ — Retired Flat-File Demo Scripts

WHAT: The original, pre-refactor versions of the Playwright demo
tooling: `playwright_demo_script.py` (short-form screenshot/video
capture), `professional_video_demo.py` (long-form captioned 1080p
walkthrough videos), and its sibling asset `professional_video_overlay.js`.

WHY: Archived (2026-07-21, `DEMO_REFACTOR_PLAN.md`) rather than deleted —
kept for history/reference. Both were rebuilt as `scripts/_*`-style
packages (`__init__.py`/`__main__.py`/`main.py` + `core/`/`exceptions/`/
`util/`) with a 100%-covered mocked test suite plus a separate
real-browser e2e/performance smoke suite, per
`coding_stds/MOST_CITED_STANDARDS.md`.

HOW: These files are frozen — do not edit them further. Use the
replacements instead:

| Archived file | Replacement package |
|---|---|
| `playwright_demo_script.py` | `demo/_playwright_demo_script/` (`python -m demo._playwright_demo_script`) |
| `professional_video_demo.py` | `demo/_professional_video_demo/` (`python -m demo._professional_video_demo`) |
| `professional_video_overlay.js` | `demo/_professional_video_demo/assets/overlay.js` |
