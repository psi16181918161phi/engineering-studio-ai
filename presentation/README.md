# presentation/ — Role 6 (Documentation, Paper & Presentation)

WHAT: Owned exclusively by Role 6. Slide deck outline/source and any
supporting presentation assets.
WHY: Keeps presentation-prep work isolated from `docs/` and `paper/`
edits so Role 6 can iterate the pitch without touching the technical
paper — see `../SCAFFOLDING.md` §2.
HOW: Fill in `slides-outline.md` first (content plan), then build the
actual slide deck (PowerPoint/Google Slides/Marp/etc. — tool choice not
prescribed) from that outline.

## Files in this folder

| File | Purpose |
|---|---|
| `slides-outline.md` | Slide-by-slide content plan for the final pitch. |
| `slides.html` | Self-contained, dependency-free HTML slide deck built from `slides-outline.md`, styled to match `../promotions/` Variant A/B art (pink/black/rose-gold palette). Open directly in a browser; arrow keys or the on-screen Prev/Next buttons navigate. |
| `export_slides_to_png.py` | Playwright script that steps through `slides.html` and screenshots each slide to `slides_png/NN-slug.png`. Re-run after any `slides.html` content change (`python export_slides_to_png.py` from this folder, or with the repo's `.venv` activated). |
| `slides_png/` | Generated output of the script above — one PNG per slide, for judges/readers who want static stills (e.g. inline in `../docs/JUDGES_GUIDE.md`) without opening the HTML deck. Regenerated wholesale on each run; do not hand-edit. |
