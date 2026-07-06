"""WHAT: Variant A ("Plot/Data Surface") and Variant B ("Interface Surface")
color palette tokens, grounded in
`coding_stds/visualization/aesthetic_standards.txt` §1.2.
WHY: Every plot/chart (Variant A) and every GUI window, TUI surface, web
interface background, or applet host chrome (Variant B) in this project
must draw its colors from exactly one named constant here — never a
hard-coded hex literal at the call site — so the palette can be audited
and changed in one place, and so §1.2.4's "never mix A and B on one
surface layer" rule is enforced by which constant a module imports.
HOW: Two flat `Palette` NamedTuples (`PALETTE_A`, `PALETTE_B`) built from
individually-named module-level constants (so call sites can import the
single token they need, e.g. `PALETTE_A_ACCENT`), plus a
`get_palette_for_surface()` lookup so GUI/webapp/CLI code declares its
surface kind once and receives the mandated variant rather than choosing
one itself.
"""

from __future__ import annotations

from enum import Enum
from typing import NamedTuple

# --- Variant A: Plot/Data Surface Palette -----------------------------------
# Applies to all plots/charts regardless of host surface (aesthetic_standards
# .txt §1.2, Table R.1). Near-black background, rose pink foreground, rose
# gold accent.
PALETTE_A_BACKGROUND = "#0D0D0D"
PALETTE_A_FOREGROUND_PRIMARY = "#E8A0A8"
PALETTE_A_ACCENT = "#B76E79"

# --- Variant B: Interface Surface Palette -----------------------------------
# Applies to all GUI windows, TUI surfaces, web interface backgrounds,
# applet host chrome, toolbars, menus, dialogs, and panels (aesthetic_
# standards.txt §1.2). Deep dark background, near-white rose text, rose gold
# accent (shared value with Variant A, separately named per §1.2.3.3), rose
# pink highlight, desaturated rose-grey muted tone.
PALETTE_B_BACKGROUND = "#110E0F"
PALETTE_B_FOREGROUND_PRIMARY = "#F5E6E8"
PALETTE_B_ACCENT = "#B76E79"
PALETTE_B_HIGHLIGHT = "#C47A82"
PALETTE_B_MUTED = "#5A4A4C"

# --- Semantic status colors --------------------------------------------------
# aesthetic_standards.txt defers success/warning/error/info hues to the
# consuming module; these are tuned to sit visually within the rose/
# near-black family used by both variants above.
PALETTE_SEMANTIC_SUCCESS = "#4CAF6D"
PALETTE_SEMANTIC_WARNING = "#D9A441"
PALETTE_SEMANTIC_ERROR = "#C4453D"
PALETTE_SEMANTIC_INFO = "#6E8AA8"


class PaletteVariant(str, Enum):
    """WHAT: The two mutually-exclusive surface palette variants.

    WHY: A plain string Enum (not a bare string) so `get_palette_for_surface`
    and callers get a closed, typo-proof set of values.
    """

    A = "A"
    B = "B"


class Palette(NamedTuple):
    """WHAT: An immutable bundle of color tokens for one palette variant.

    ATTRIBUTES:
        background (str): Hex color for the surface background.
        foreground_primary (str): Hex color for primary text/data ink.
        accent (str): Hex color for the shared rose-gold accent.
        highlight (str | None): Hex color for hover/selection states;
            `None` for Variant A, which has no highlight token defined.
        muted (str | None): Hex color for de-emphasized text/borders;
            `None` for Variant A, which has no muted token defined.
    """

    background: str
    foreground_primary: str
    accent: str
    highlight: str | None = None
    muted: str | None = None


PALETTE_A = Palette(
    background=PALETTE_A_BACKGROUND,
    foreground_primary=PALETTE_A_FOREGROUND_PRIMARY,
    accent=PALETTE_A_ACCENT,
)

PALETTE_B = Palette(
    background=PALETTE_B_BACKGROUND,
    foreground_primary=PALETTE_B_FOREGROUND_PRIMARY,
    accent=PALETTE_B_ACCENT,
    highlight=PALETTE_B_HIGHLIGHT,
    muted=PALETTE_B_MUTED,
)

# aesthetic_standards.txt §1.2: plots/charts always use Variant A; every
# other named surface kind uses Variant B. A plot embedded inside a GUI is
# the sole permitted A/B co-occurrence (§1.2.4) — the *embedded plot widget*
# still looks itself up as "plot", not as "gui".
_SURFACE_TO_VARIANT: dict[str, PaletteVariant] = {
    "plot": PaletteVariant.A,
    "chart": PaletteVariant.A,
    "gui": PaletteVariant.B,
    "tui": PaletteVariant.B,
    "webapp": PaletteVariant.B,
    "cli": PaletteVariant.B,
    "applet": PaletteVariant.B,
}


def get_palette(variant: PaletteVariant | str) -> Palette:
    """WHAT: Returns the `Palette` for an explicit variant.

    ARGS:
        variant (PaletteVariant | str): `"A"`/`PaletteVariant.A` or
            `"B"`/`PaletteVariant.B`.

    RETURNS:
        Palette: `PALETTE_A` or `PALETTE_B`.

    RAISES:
        ValueError: If `variant` is not a recognized value.
    """
    return PALETTE_A if PaletteVariant(variant) is PaletteVariant.A else PALETTE_B


def get_palette_for_surface(surface_kind: str) -> Palette:
    """WHAT: Returns the mandated `Palette` for a named surface kind.

    ARGS:
        surface_kind (str): One of `"plot"`, `"chart"`, `"gui"`, `"tui"`,
            `"webapp"`, `"cli"`, `"applet"` (case-insensitive).

    RETURNS:
        Palette: The variant mandated by aesthetic_standards.txt §1.2 for
        that surface kind.

    RAISES:
        ValueError: If `surface_kind` is not a recognized surface name —
        callers must name a real surface rather than guessing a variant.

    WHY: Centralizing this lookup means a GUI/webapp/CLI module never has
    to decide "am I an A surface or a B surface" itself; it just states
    what it is and gets the correct palette, enforcing §1.2.4 by
    construction.
    """
    key = surface_kind.lower()
    if key not in _SURFACE_TO_VARIANT:
        raise ValueError(
            f"unknown surface_kind={surface_kind!r}; expected one of "
            f"{sorted(_SURFACE_TO_VARIANT)}"
        )
    return get_palette(_SURFACE_TO_VARIANT[key])


__all__ = [
    "PALETTE_A_BACKGROUND",
    "PALETTE_A_FOREGROUND_PRIMARY",
    "PALETTE_A_ACCENT",
    "PALETTE_B_BACKGROUND",
    "PALETTE_B_FOREGROUND_PRIMARY",
    "PALETTE_B_ACCENT",
    "PALETTE_B_HIGHLIGHT",
    "PALETTE_B_MUTED",
    "PALETTE_SEMANTIC_SUCCESS",
    "PALETTE_SEMANTIC_WARNING",
    "PALETTE_SEMANTIC_ERROR",
    "PALETTE_SEMANTIC_INFO",
    "PaletteVariant",
    "Palette",
    "PALETTE_A",
    "PALETTE_B",
    "get_palette",
    "get_palette_for_surface",
]
