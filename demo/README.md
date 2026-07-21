# demo/ — Role 5 &amp; Role 6 (Frontend/Visualization + Documentation shared)

WHAT: The live demo script and any recorded demo video/assets.
WHY: Co-owned deliberately (unlike other zones): Role 6 writes the
narration/beats, Role 5 wires the corresponding live actions in the UI —
see `../SCAFFOLDING.md` §2.
HOW: Fill in `demo-script.md` together; Role 5 also drops any recorded
demo video file here once produced (large binaries — consider Git LFS per
`../.gitattributes`).

## Files in this folder

| File | Purpose |
|---|---|
| `demo-script.md` | Beat-by-beat narration + corresponding on-screen action, mapped to the Demo Flow sequence diagram. |
| `demo_prompts.json` | The 3 confirmed, software-first demo prompts (single source of truth), consumed by `playwright_demo_script.py`, `tests/e2e/test_pipeline_stream.py`, and `run_demo_sequence.py`. |
| `run_demo_sequence.py` | CLI-only (no browser) rehearsal launcher: runs each confirmed prompt through the pipeline in order, writing timestamped artifacts + a `manifest.json` for presenter handoff. Complements the browser-based `playwright_demo_script.py`. |
| `professional_video_demo.py` | Long-form (2-5 minute), captioned, headless, 1080p screen-recording script for polished/"YouTube-grade" full-pipeline walkthrough videos (Light Mode + Dark Mode). Silent ("quiet mode") — narration is burned-in captions, not a voiceover track. Reuses `playwright_demo_script.py`'s server bootstrap/slugify helpers and `run_demo_sequence.py`'s prompt loader; writes to `demo/recordings/professional/` (kept separate from the short-form script's `demo/recordings/{screenshots,video}/`). |

## Coordination rule

Since this folder has two owners, treat `demo-script.md` like the shared
files in `../SCAFFOLDING.md` §4: append/edit your own column, don't
silently rewrite the other person's beats without a quick sync.
