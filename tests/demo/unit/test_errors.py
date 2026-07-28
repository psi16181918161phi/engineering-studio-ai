"""WHAT: Unit tests for both packages' exception hierarchies.
WHY: Cheap, direct coverage of every exception class's inheritance
chain, matching the "one base + narrow subclasses" convention.
HOW: Instantiates and raises/catches each exception.
"""

from __future__ import annotations

import pytest

from demo._playwright_demo_script.exceptions.errors import (
    PlaywrightDemoError,
    RecordingError,
    ServerStartError,
)
from demo._professional_video_demo.exceptions.errors import (
    PacingError,
    ProfessionalDemoError,
)


def test_playwright_error_hierarchy() -> None:
    assert issubclass(ServerStartError, PlaywrightDemoError)
    assert issubclass(RecordingError, PlaywrightDemoError)
    with pytest.raises(PlaywrightDemoError):
        raise ServerStartError("boom")
    with pytest.raises(PlaywrightDemoError):
        raise RecordingError("boom")


def test_professional_error_hierarchy() -> None:
    assert issubclass(PacingError, ProfessionalDemoError)
    with pytest.raises(ProfessionalDemoError):
        raise PacingError("boom")
