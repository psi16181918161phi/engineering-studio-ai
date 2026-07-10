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

import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

PRESENTATION_DIR = Path(__file__).resolve().parent
SLIDES_HTML = PRESENTATION_DIR / "slides.html"
OUTPUT_DIR = PRESENTATION_DIR / "slides_png"

# One slug per slide, in deck order (must match slides.html's 9 <section>s).
SLIDE_SLUGS = [
    "01-title",
    "02-problem",
    "03-solution",
    "04-architecture",
    "05-live-demo",
    "06-amd-ecosystem-usage",
    "07-results-validation",
    "08-startup-roadmap",
    "09-team-thanks",
]


def export() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(SLIDES_HTML.as_uri())

        # First slide has no Mermaid diagram; wait for the deck's own active
        # slide to be present before doing anything else.
        page.wait_for_selector(".slide.active")

        for index, slug in enumerate(SLIDE_SLUGS):
            if slug == "04-architecture":
                # Mermaid renders async off a CDN import; wait for its <svg>
                # output rather than a fixed sleep.
                page.wait_for_selector(".slide.active .mermaid svg", timeout=10_000)

            active_slide = page.query_selector(".slide.active")
            assert active_slide is not None, f"no active slide at index {index}"
            out_path = OUTPUT_DIR / f"{slug}.png"
            active_slide.screenshot(path=str(out_path))
            print(f"wrote {out_path.relative_to(PRESENTATION_DIR)}")

            if index < len(SLIDE_SLUGS) - 1:
                page.click("#nextBtn")

        browser.close()


if __name__ == "__main__":
    export()
