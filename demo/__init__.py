"""WHAT: Marks `demo/` as a regular importable Python package.
WHY: Enables `demo._playwright_demo_script` / `demo._professional_video_demo`
(and their shared import of `demo.run_demo_sequence._load_prompts`) to be
imported normally by tests and by each other, replacing the previous
manual `sys.path.insert(0, ...)` trick used by the archived scripts.
HOW: Intentionally empty beyond this docstring — no package-level state.
"""

from __future__ import annotations
