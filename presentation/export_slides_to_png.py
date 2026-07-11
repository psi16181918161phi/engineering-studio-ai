"""Export presentation/slides.html into one PNG per slide.

WHAT: Headless-Chromium (Playwright) script that opens slides.html locally,
steps through all 9 slides via the deck's own Prev/Next navigation, and
screenshots each active `<section class="slide">` to
presentation/slides_png/NN-slug.png.
WHY: Judges reviewing docs/JUDGES_GUIDE.md need static image thumbnails they
can view inline (e.g. in a GitHub markdown preview) without opening the
HTML deck in a browser; PNGs also survive anywhere HTML+JS execution isn't
convenient (PDF exports, printed handouts).
HOW: Reuses the same Playwright dependency already pinned in pyproject.toml
for the e2e test suite. Waits for the Mermaid diagram's <svg> to appear
before capturing the Architecture slide so the export never races the
CDN-loaded Mermaid render. Re-run any time slides.html content changes;
output directory is deleted and regenerated each run for a clean diff.
"""

from __future__ import annotations

import functools
import shutil
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Final, TypeVar

from playwright.sync_api import Page, sync_playwright

# --- Configuration constants ------------------------------------------------
# WHAT: Frozen path/geometry inputs the whole export depends on.
# WHY: Tier 1 (Functional Programming) — determinism starts with immutable,
#      single-source-of-truth inputs rather than scattered magic values.
# HOW: `Final` marks them read-only; derived from this file's own location so
#      the script is runnable from any working directory.
PRESENTATION_DIR: Final[Path] = Path(__file__).resolve().parent
SLIDES_HTML: Final[Path] = PRESENTATION_DIR / "slides.html"
OUTPUT_DIR: Final[Path] = PRESENTATION_DIR / "slides_png"
VIEWPORT: Final[dict[str, int]] = {"width": 1920, "height": 1080}
ACTIVE_SLIDE_SELECTOR: Final[str] = ".slide.active"
MERMAID_SVG_SELECTOR: Final[str] = f"{ACTIVE_SLIDE_SELECTOR} .mermaid svg"
MERMAID_SLUG: Final[str] = "04-architecture"
MERMAID_TIMEOUT_MS: Final[int] = 10_000
NEXT_BUTTON_SELECTOR: Final[str] = "#nextBtn"

# One slug per slide, in deck order (must match slides.html's 9 <section>s).
SLIDE_SLUGS: Final[tuple[str, ...]] = (
    "01-title",
    "02-problem",
    "03-solution",
    "04-architecture",
    "05-live-demo",
    "06-amd-ecosystem-usage",
    "07-results-validation",
    "08-startup-roadmap",
    "09-team-thanks",
)

F = TypeVar("F", bound=Callable[..., object])


# --- Exceptions -------------------------------------------------------------
class SlideExportError(RuntimeError):
    """Base class for all slide-export failures.

    WHAT: Domain-specific root exception for this module.
    WHY: FOUR-elements standard — expose an explicit exception element so
         callers can catch this module's failures without swallowing
         unrelated ``RuntimeError``s.
    HOW: Subclass ``RuntimeError`` so it stays catchable by broad handlers
         while remaining narrowly identifiable by type.
    """


class MissingActiveSlideError(SlideExportError):
    """Raised when the deck has no active ``.slide`` element to capture.

    WHAT: Signals the DOM invariant (exactly one active slide) was violated.
    WHY: Replaces a bare ``assert`` with a typed, always-on guard so the
         failure survives ``python -O`` and names the offending index.
    HOW: Carry the failing slide index for actionable diagnostics.
    """

    def __init__(self, index: int) -> None:
        self.index = index
        super().__init__(f"no active slide at index {index}")


# --- Decorators -------------------------------------------------------------
def logs_output(func: F) -> F:
    """Print the relative path a capture function returned.

    WHAT: Cross-cutting logging wrapper around any ``Path``-returning capture.
    WHY: FOUR-elements standard — isolate the side-effect (printing) from the
         pure capture logic so the wrapped function stays single-purpose.
    HOW: ``functools.wraps`` preserves identity; the returned ``Path`` is made
         relative to ``PRESENTATION_DIR`` for a clean, portable log line.
    """

    @functools.wraps(func)
    def wrapper(*args: object, **kwargs: object) -> object:
        result = func(*args, **kwargs)
        if isinstance(result, Path):
            print(f"wrote {result.relative_to(PRESENTATION_DIR)}")
        return result

    return wrapper  # type: ignore[return-value]


# --- Value object -----------------------------------------------------------
@dataclass(frozen=True)
class Slide:
    """A single deck slide's export identity.

    WHAT: Immutable pairing of deck position and output filename slug.
    WHY: SOLID/SRP — one small type owns "which slide + where it writes",
         keeping the exporter free of index/slug bookkeeping.
    HOW: ``frozen=True`` makes instances hashable and side-effect free.
    """

    index: int
    slug: str

    @property
    def needs_mermaid(self) -> bool:
        """Whether this slide must wait for a Mermaid ``<svg>`` before capture."""
        return self.slug == MERMAID_SLUG

    @property
    def output_path(self) -> Path:
        """Destination PNG path for this slide."""
        return OUTPUT_DIR / f"{self.slug}.png"


# --- Core exporter ----------------------------------------------------------
class SlideExporter:
    """Drive a Playwright page through the deck and screenshot each slide.

    WHAT: Orchestrates navigation + capture for the ordered slide list.
    WHY: SOLID/SRP — separates Playwright interaction from configuration and
         from the CLI entry point, so each concern is independently testable.
    HOW: Holds the live ``Page`` and iterates ``Slide`` value objects, using
         the deck's own Prev/Next navigation between captures.
    """

    def __init__(self, page: Page, slides: tuple[Slide, ...]) -> None:
        self._page = page
        self._slides = slides

    @classmethod
    def from_slugs(cls, page: Page, slugs: tuple[str, ...]) -> "SlideExporter":
        """Build an exporter from an ordered slug tuple.

        WHAT: Named constructor mapping slugs to indexed ``Slide`` objects.
        WHY: Keeps ``__init__`` dependency-only; deck ordering lives here.
        HOW: ``enumerate`` assigns each slug its deck index.
        """
        slides = tuple(Slide(index=i, slug=slug) for i, slug in enumerate(slugs))
        return cls(page, slides)

    def _wait_for_active_slide(self) -> None:
        """Block until the deck has rendered its active slide.

        WHAT: Guards against racing the deck's initial render.
        WHY: The first capture must not fire before any slide is active.
        HOW: Playwright's selector wait on ``.slide.active``.
        """
        self._page.wait_for_selector(ACTIVE_SLIDE_SELECTOR)

    def _wait_for_mermaid(self) -> None:
        """Block until the Architecture slide's Mermaid ``<svg>`` exists.

        WHAT: Prevents capturing the diagram slide mid-render.
        WHY: Mermaid imports async off a CDN; a fixed sleep would be flaky.
        HOW: Wait for the rendered ``<svg>`` output with a bounded timeout.
        """
        self._page.wait_for_selector(MERMAID_SVG_SELECTOR, timeout=MERMAID_TIMEOUT_MS)

    @logs_output
    def _capture(self, slide: Slide) -> Path:
        """Screenshot the currently-active slide to its output path.

        WHAT: Pure-ish capture of one active slide element to a PNG.
        WHY: SRP — isolates the single screenshot from navigation flow.
        HOW: Queries the active element, raising a typed guard if absent,
             then writes the PNG and returns its path for the log decorator.
        """
        element = self._page.query_selector(ACTIVE_SLIDE_SELECTOR)
        if element is None:
            raise MissingActiveSlideError(slide.index)
        element.screenshot(path=str(slide.output_path))
        return slide.output_path

    def _advance(self) -> None:
        """Navigate the deck to the next slide.

        WHAT: Clicks the deck's own Next button.
        WHY: Reuses the deck's navigation instead of re-implementing state.
        HOW: Single Playwright click on ``#nextBtn``.
        """
        self._page.click(NEXT_BUTTON_SELECTOR)

    def run(self) -> None:
        """Capture every slide in deck order.

        WHAT: The full export loop (open -> per-slide capture -> advance).
        WHY: Single public entry point for the exporter's behaviour.
        HOW: Waits for readiness, then per slide optionally waits for Mermaid,
             captures, and advances unless it is the final slide.
        """
        self._wait_for_active_slide()
        for slide in self._slides:
            if slide.needs_mermaid:
                self._wait_for_mermaid()
            self._capture(slide)
            if slide.index < len(self._slides) - 1:
                self._advance()


# --- Module-level orchestration ---------------------------------------------
def _reset_output_dir() -> None:
    """Delete and recreate the PNG output directory.

    WHAT: Ensures a clean, deterministic output tree each run.
    WHY: A fresh directory guarantees a clean diff (no stale PNGs linger).
    HOW: ``shutil.rmtree`` if present, then recreate with parents.
    """
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)


def export() -> None:
    """Export ``slides.html`` to one PNG per slide.

    WHAT: Top-level workflow tying config, browser lifecycle, and exporter.
    WHY: Keeps the ``__main__`` guard trivial and the browser resource scoped.
    HOW: Resets output, launches headless Chromium via a context manager,
         and delegates the capture loop to ``SlideExporter``.
    """
    _reset_output_dir()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page(viewport=VIEWPORT)
            page.goto(SLIDES_HTML.as_uri())
            SlideExporter.from_slugs(page, SLIDE_SLUGS).run()
        finally:
            browser.close()


def main() -> None:
    """CLI entry point.

    WHAT: Thin wrapper invoking ``export``.
    WHY: languages/coding_standards — provide an explicit ``main()`` seam.
    HOW: Delegates directly to ``export``.
    """
    export()


if __name__ == "__main__":
    main()
