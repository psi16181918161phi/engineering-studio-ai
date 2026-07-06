"""WHAT: Unit tests for the utils.palette module.
WHY: The palette tokens are the single source of truth every future GUI/
webapp/CLI surface must draw from — must reach 100% coverage and must
enforce aesthetic_standards.txt §1.2's surface->variant mapping.
HOW: Pure value/lookup assertions; no rendering, no I/O.
"""

from __future__ import annotations

import pytest

from engineering_studio.utils.palette import (
    PALETTE_A,
    PALETTE_A_ACCENT,
    PALETTE_B,
    PALETTE_B_HIGHLIGHT,
    Palette,
    PaletteVariant,
    get_palette,
    get_palette_for_surface,
)


def test_palette_a_has_no_highlight_or_muted_tokens() -> None:
    assert PALETTE_A.highlight is None
    assert PALETTE_A.muted is None


def test_palette_b_has_highlight_and_muted_tokens() -> None:
    assert PALETTE_B.highlight == PALETTE_B_HIGHLIGHT
    assert PALETTE_B.muted is not None


def test_get_palette_accepts_enum_and_string() -> None:
    assert get_palette(PaletteVariant.A) == PALETTE_A
    assert get_palette("B") == PALETTE_B


def test_get_palette_rejects_unknown_variant() -> None:
    with pytest.raises(ValueError):
        get_palette("C")


@pytest.mark.parametrize(
    "surface_kind,expected",
    [
        ("plot", PALETTE_A),
        ("Chart", PALETTE_A),
        ("gui", PALETTE_B),
        ("TUI", PALETTE_B),
        ("webapp", PALETTE_B),
        ("cli", PALETTE_B),
        ("applet", PALETTE_B),
    ],
)
def test_get_palette_for_surface_matches_aesthetic_standard(
    surface_kind: str, expected: Palette
) -> None:
    assert get_palette_for_surface(surface_kind) == expected


def test_get_palette_for_surface_rejects_unknown_surface() -> None:
    with pytest.raises(ValueError, match="unknown surface_kind"):
        get_palette_for_surface("holodeck")


def test_variant_a_and_b_share_the_same_accent_hex_but_are_separately_named() -> None:
    assert PALETTE_A.accent == PALETTE_A_ACCENT
    assert PALETTE_A.accent == PALETTE_B.accent
