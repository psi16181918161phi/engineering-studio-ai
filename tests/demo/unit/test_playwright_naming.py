"""WHAT: Unit tests for `demo._playwright_demo_script.core.naming.slugify`.
WHY: Pure function — trivially unit tested in isolation (FP §3).
HOW: Table-driven cases covering truncation, casing, and punctuation
stripping.
"""

from __future__ import annotations

import pytest

from demo._playwright_demo_script.core.naming import slugify


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hello World", "hello-world"),
        (
            "Create a Python script that automates backups",
            "create-a-python-script-that",
        ),
        ("Multi!!  Punctuation,, Here.", "multi-punctuation-here"),
        ("", ""),
        ("ONE", "one"),
    ],
)
def test_slugify(text: str, expected: str) -> None:
    assert slugify(text) == expected
