"""WHAT: Public API surface for the `_professional_video_demo` package.
WHY: SOLID OCP — downstream importers (and tests) depend on this stable
surface rather than reaching into submodules directly.
HOW: Re-exports from `core`, `exceptions`, and `util` subpackages.
"""

from __future__ import annotations

from .core.pacing import DISCLAIMER, STAGE_CAPTIONS, STAGE_ORDER, VIEWPORT, Pacing
from .core.recorder import record_one_video
from .core.scenario import record_scenario
from .exceptions.errors import PacingError, ProfessionalDemoError
from .util.pipeline import ProfessionalDemoRunner, build_professional_demo_runner

__all__ = [
    "DISCLAIMER",
    "PacingError",
    "Pacing",
    "ProfessionalDemoError",
    "ProfessionalDemoRunner",
    "STAGE_CAPTIONS",
    "STAGE_ORDER",
    "VIEWPORT",
    "build_professional_demo_runner",
    "record_one_video",
    "record_scenario",
]
