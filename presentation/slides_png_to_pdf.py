"""Combine presentation/slides_png/*.png into a single ordered PDF.

WHAT: Small standalone script that collects every ``NN-slug.png`` in
``presentation/slides_png/``, sorts them by their numeric prefix, and writes
them into one multi-page PDF (``presentation/engineering-studio-ai-slides.pdf``),
one slide per page in deck order.
WHY: Judges and reviewers often want a single portable artifact they can
scroll, print, or attach to an email without opening the HTML deck or
browsing nine separate image files; a PDF preserves slide order and prints
cleanly.
HOW: Uses Pillow (already available in the dev environment) to open each PNG,
convert to RGB, and save the first image with ``save_all=True`` plus the
remaining images as ``append_images``. Slides are ordered by their filename
numeric prefix so the on-disk naming convention (01-, 02-, ...) is the single
source of truth for page order. Re-run any time the PNGs are regenerated.
"""

from __future__ import annotations

import functools
import logging
from collections.abc import Callable
from pathlib import Path
from typing import ParamSpec, TypeVar

from PIL import Image

PRESENTATION_DIR = Path(__file__).resolve().parent
SLIDES_PNG_DIR = PRESENTATION_DIR / "slides_png"
OUTPUT_PDF = PRESENTATION_DIR / "engineering-studio-ai-slides.pdf"

_LOGGER = logging.getLogger(__name__)

_P = ParamSpec("_P")
_R = TypeVar("_R")


class SlideDeckError(Exception):
    """Base exception for slide-deck-to-PDF failures.

    WHAT: Common ancestor for every domain error this module raises so callers
    can catch the whole family with one ``except``.
    WHY: SOLID/Four-Elements mandates a dedicated exception hierarchy instead of
    reusing broad built-ins, keeping error semantics explicit and testable.
    HOW: Subclassed by the concrete error conditions below; never raised directly.
    """


class NoSlidesFoundError(SlideDeckError):
    """Raised when no numbered ``NN-slug.png`` slides exist in the source dir.

    WHAT: Signals an empty or mis-named slide directory.
    WHY: A distinct type lets tests and callers distinguish "nothing to convert"
    from other I/O failures without string-matching messages.
    HOW: Constructed with the searched directory to give an actionable message.
    """

    def __init__(self, slides_dir: Path) -> None:
        super().__init__(f"No numbered PNG slides found in {slides_dir}")
        self.slides_dir = slides_dir


def log_step(func: Callable[_P, _R]) -> Callable[_P, _R]:
    """Decorator that logs entry/exit of a pipeline step.

    WHAT: Wraps a function to emit a debug log before and after it runs.
    WHY: Centralizes cross-cutting observability so each step stays a pure,
    single-responsibility unit (SOLID) free of scattered logging noise.
    HOW: Uses ``functools.wraps`` to preserve identity, logs the call name,
    invokes the wrapped callable, then logs completion and returns its result.
    """

    @functools.wraps(func)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        _LOGGER.debug("start: %s", func.__name__)
        result = func(*args, **kwargs)
        _LOGGER.debug("done: %s", func.__name__)
        return result

    return wrapper


class SlideCollector:
    """Discovers and orders slide PNGs by their numeric filename prefix.

    WHAT: Encapsulates the rules for finding ``NN-slug.png`` files and sorting
    them into deck order.
    WHY: Isolating discovery from rendering (single responsibility) lets each be
    tested in isolation and keeps filename convention the single source of truth.
    HOW: Globs the given directory, filters to numeric-prefixed names, and sorts
    by the parsed integer prefix.
    """

    def __init__(self, slides_dir: Path) -> None:
        self._slides_dir = slides_dir

    @staticmethod
    def _numeric_prefix(path: Path) -> int:
        """Return the leading integer of a ``NN-slug.png`` filename for sorting.

        WHAT: Parses the ``NN`` portion of the stem into an int.
        WHY: Numeric ordering must not depend on lexical string sort (e.g. so
        ``10-`` follows ``9-``).
        HOW: Splits the stem on the first hyphen and converts the head to ``int``.
        """
        prefix = path.stem.split("-", 1)[0]
        return int(prefix)

    @staticmethod
    def _has_numeric_prefix(path: Path) -> bool:
        """Return whether a path's stem starts with a numeric prefix.

        WHAT: Predicate identifying valid deck slides.
        WHY: Guards ``_numeric_prefix`` against non-conforming files so parsing
        never throws mid-sort.
        HOW: Inspects the pre-hyphen head of the stem with ``str.isdigit``.
        """
        return path.stem.split("-", 1)[0].isdigit()

    @log_step
    def collect(self) -> list[Path]:
        """Return all slide PNGs sorted by their numeric filename prefix.

        WHAT: Produces the ordered list of slide image paths.
        WHY: Callers need a deterministic, deck-ordered sequence to render.
        HOW: Globs ``*.png``, filters by numeric prefix, raises if empty,
        otherwise returns the list sorted by prefix.
        """
        pngs = [p for p in self._slides_dir.glob("*.png") if self._has_numeric_prefix(p)]
        if not pngs:
            raise NoSlidesFoundError(self._slides_dir)
        return sorted(pngs, key=self._numeric_prefix)


class PdfBuilder:
    """Renders an ordered list of PNGs into one multi-page PDF.

    WHAT: Encapsulates the Pillow-specific rendering of slides into a PDF.
    WHY: Separating rendering from discovery (single responsibility) keeps the
    Pillow dependency confined to one class and independently testable.
    HOW: Opens each PNG as RGB, saves the first page with ``save_all`` plus the
    remainder as ``append_images``, and closes every handle afterward.
    """

    @log_step
    def build(self, png_paths: list[Path], output_pdf: Path) -> None:
        """Write the ordered PNGs into a single multi-page PDF (one slide/page).

        WHAT: Emits the combined PDF artifact to ``output_pdf``.
        WHY: A single portable file is what reviewers want to scroll/print.
        HOW: Converts each image to RGB, saves page one with the rest appended,
        then releases all image handles.
        """
        images = [Image.open(p).convert("RGB") for p in png_paths]
        try:
            first, rest = images[0], images[1:]
            first.save(output_pdf, save_all=True, append_images=rest)
        finally:
            for img in images:
                img.close()


def main() -> None:
    """Entry point: collect slides in order and write the combined PDF.

    WHAT: Orchestrates ``SlideCollector`` and ``PdfBuilder`` end to end.
    WHY: Provides a single runnable command to regenerate the artifact.
    HOW: Collects ordered paths, prints the plan, builds the PDF, and reports
    the output location.
    """
    logging.basicConfig(level=logging.INFO)
    png_paths = SlideCollector(SLIDES_PNG_DIR).collect()
    print(f"Collecting {len(png_paths)} slides in order:")
    for p in png_paths:
        print(f"  {p.name}")
    PdfBuilder().build(png_paths, OUTPUT_PDF)
    print(f"\nWrote {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
