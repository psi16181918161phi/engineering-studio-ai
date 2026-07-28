"""WHAT: Custom exception hierarchy for the `_playwright_demo_script` package.
WHY: Domain-specific exceptions let callers distinguish server-bootstrap
failures from recording failures instead of catching bare `Exception`
(SOLID SRP: one exception per concern, matching
`scripts/_sync_submodules/exceptions/sync_errors.py`'s shape).
HOW: `PlaywrightDemoError` is the package base class; `ServerStartError`
and `RecordingError` are narrow subclasses raised by `core.server` and
`core.recorder` respectively.
"""

from __future__ import annotations


class PlaywrightDemoError(Exception):
    """WHAT: Base class for all `_playwright_demo_script` errors.
    WHY: Single catch-point for callers wanting broad error handling.
    """


class ServerStartError(PlaywrightDemoError):
    """WHAT: Raised when the demo FastAPI/uvicorn server does not become
    healthy within the startup deadline.
    """


class RecordingError(PlaywrightDemoError):
    """WHAT: Raised when a single (theme, prompt) screenshot/video
    recording scenario fails.
    """
