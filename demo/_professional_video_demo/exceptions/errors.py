"""WHAT: Custom exception hierarchy for the `_professional_video_demo`
package.
WHY: Domain-specific exceptions matching
`scripts/_sync_submodules/exceptions/sync_errors.py`'s shape.
HOW: `ProfessionalDemoError` is the package base class; `PacingError`
replaces the original script's bare `assert` inside
`Pacing.from_target_seconds` (an `AssertionError` is not a documented
public contract, so it is now a real, catchable, raised exception).
"""

from __future__ import annotations


class ProfessionalDemoError(Exception):
    """WHAT: Base class for all `_professional_video_demo` errors."""


class PacingError(ProfessionalDemoError):
    """WHAT: Raised when a computed `Pacing` would fall outside the
    mandatory [100, 320] second sanity band.
    """
