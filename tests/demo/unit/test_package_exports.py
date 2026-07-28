"""WHAT: Confirms both packages' top-level `__init__.py` re-export
surfaces import cleanly and match their declared `__all__`.
WHY: Exercises the two otherwise test-uncovered top-level `__init__.py`
modules for the 100%-coverage gate.
"""

from __future__ import annotations

import demo._playwright_demo_script as playwright_pkg
import demo._professional_video_demo as professional_pkg


def test_playwright_package_exports_match_all() -> None:
    for name in playwright_pkg.__all__:
        assert hasattr(playwright_pkg, name)


def test_professional_package_exports_match_all() -> None:
    for name in professional_pkg.__all__:
        assert hasattr(professional_pkg, name)
