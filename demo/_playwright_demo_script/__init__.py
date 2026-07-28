"""WHAT: Public API surface for the `_playwright_demo_script` package.
WHY: SOLID OCP — downstream importers (including
`demo._professional_video_demo`) depend on this stable surface rather
than reaching into submodules directly.
HOW: Re-exports from `core`, `exceptions`, and `util` subpackages.
"""

from __future__ import annotations

from .core.naming import slugify
from .core.recorder import record_scenario
from .core.server import free_port, start_server
from .exceptions.errors import PlaywrightDemoError, RecordingError, ServerStartError
from .util.pipeline import PlaywrightDemoRunner, build_playwright_demo_runner

__all__ = [
    "PlaywrightDemoError",
    "PlaywrightDemoRunner",
    "RecordingError",
    "ServerStartError",
    "build_playwright_demo_runner",
    "free_port",
    "record_scenario",
    "slugify",
    "start_server",
]
