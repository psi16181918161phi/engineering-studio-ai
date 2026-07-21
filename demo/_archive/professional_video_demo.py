"""WHAT: Long-form, captioned, headless screen-recording demo script that
produces professional/"YouTube-grade" videos of the FULL Engineering
Studio AI pipeline cycle — brief entry, orchestrator dispatch, all eight
pipeline stages (`research` -> parallel domain specialists -> `business`
-> `challenge` -> `quality_gate`), and the final verdict — for both Light
Mode and Dark Mode, deliberately paced to land each video inside the
mandatory 2-5 minute (120-300 second) band.
WHY: `playwright_demo_script.py` already exists for short, real-time
screenshot/video capture, but its videos run only as long as the
(mocked) pipeline actually takes to execute — typically a few seconds,
far too short for a polished walkthrough video. This script is additive
(SOLID Open/Closed: extends the demo suite with a new file rather than
rewriting the existing short-form script) and produces a second,
separate output set under `demo/recordings/professional/` with:
  - a full-viewport (1920x1080, YouTube-standard 1080p) recording;
  - a burned-in captioned overlay (title bar, per-stage progress bar,
    lower-third caption explaining what each stage does and why) instead
    of a voiceover track — i.e. "quiet mode": Playwright's Chromium video
    recorder never captures audio, so these videos are intentionally
    silent-but-captioned rather than narrated, which the requester
    explicitly allowed ("in quiet mode is fine");
  - branded intro/outro title cards per theme.
Per `AGENTS.md` §5 (live-data honesty / grounding), the intro card
explicitly discloses that this is a *deliberately paced* walkthrough
(fixed caption-hold durations), not a literal real-time capture of
pipeline execution speed — never silently implying the mocked pipeline
is naturally this slow.
HOW: Reuses (does not duplicate) `_slugify`/`_start_server` from
`playwright_demo_script.py` and `_load_prompts` from
`run_demo_sequence.py` (both siblings in this same `demo/` directory,
importable because Python adds the executed script's own directory to
`sys.path[0]`). Defaults to **Mode B** (deterministic
`ENGINEERING_STUDIO_FAKE_PIPELINE=1`, no `FIREWORKS_API_KEY` required) —
pass `--live` for Mode A. Runs Chromium **headless** (no `--headed`
override is exposed beyond a local debug escape hatch) since this is a
batch video-generation script, not an interactive one.

The injected overlay's markup/CSS/JS lives in the sibling file
`professional_video_overlay.js` (single-responsibility split: this file
owns orchestration/pacing only, that file owns browser-side rendering) —
read from disk once at import time. Every overlay element is
`pointer-events: none` so it can never intercept a click meant for the
real app UI underneath it. Each (theme, prompt) recording is wrapped in
its own try/except in `main()` so one failed video (e.g. a transient
selector timeout) is reported and skipped rather than aborting the
entire batch — the run always attempts all `themes x prompts`
combinations and prints a final PASS/FAIL summary.

Usage:
    python demo/professional_video_demo.py [--theme light|dark|both]
        [--target-duration SECONDS] [--prompt-id ID ...] [--live] [--headed]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from playwright.sync_api import Browser, Page, sync_playwright

DEMO_DIR = Path(__file__).resolve().parent
if str(DEMO_DIR) not in sys.path:  # pragma: no cover - import path bootstrap
    sys.path.insert(0, str(DEMO_DIR))

from playwright_demo_script import _slugify, _start_server  # noqa: E402
from run_demo_sequence import _load_prompts  # noqa: E402

REPO_ROOT = DEMO_DIR.parent
RECORDINGS_ROOT = REPO_ROOT / "demo" / "recordings" / "professional"
DEFAULT_PROMPTS_FILE = REPO_ROOT / "demo" / "demo_prompts.json"

# WHAT: 1080p, the de-facto minimum "professional" resolution for a
# YouTube-grade upload.
VIEWPORT = {"width": 1920, "height": 1080}

# WHAT: Mirrors engineering_studio.agents.orchestrator.STAGE_ORDER /
# frontend/app.js STAGES — fixed-size, hand-kept-in-sync tuple (bounded,
# never dynamically grown) per JPL Power-of-Ten's preference for fixed,
# statically-known loop bounds.
STAGE_ORDER: tuple[str, ...] = (
    "research",
    "mechanical",
    "electrical",
    "firmware",
    "simulation",
    "business",
    "challenge",
    "quality_gate",
)

# WHAT: One heading + one grounded, one-sentence explanation per stage.
# WHY: Lifted directly from frontend/app.js's STAGES role metadata and
# the pipeline's documented responsibilities — never invented marketing
# copy, so the captions stay factually grounded in real pipeline
# behavior (coding_stds grounding mandate).
STAGE_CAPTIONS: dict[str, tuple[str, str]] = {
    "research": (
        "Research",
        "Frames the problem and checks feasibility before any discipline starts building.",
    ),
    "mechanical": (
        "Mechanical Specialist",
        "Designs the physical structure, materials, and tolerances — runs in parallel with the other disciplines.",
    ),
    "electrical": (
        "Electrical Specialist",
        "Designs power delivery, sensing, and wiring — runs in parallel with the other disciplines.",
    ),
    "firmware": (
        "Firmware Specialist",
        "Designs the embedded control logic — runs in parallel with the other disciplines.",
    ),
    "simulation": (
        "Simulation Specialist",
        "Validates the design virtually before anyone commits to a physical build — runs in parallel.",
    ),
    "business": (
        "Cost / Business / Legal",
        "Prices the bill of materials and flags any legal or compliance constraints.",
    ),
    "challenge": (
        "Challenge Division",
        "Adversarially reviews every prior stage's output, looking for gaps or unsafe assumptions.",
    ),
    "quality_gate": (
        "Quality Gate",
        "The sole certifying authority for this run — renders the final pass/fail verdict.",
    ),
}

DISCLAIMER = (
    "Deliberately paced walkthrough for caption readability — "
    "actual pipeline runtime may be faster or slower than shown here."
)

# WHAT: Browser-side overlay source, loaded once at import time from its
# own sibling file rather than embedded as a Python string literal.
# WHY: Keeps this file focused on orchestration/pacing; see
# `professional_video_overlay.js`'s own docstring for the overlay's
# rendering details (every element is `pointer-events: none` so it can
# never block a real click, e.g. the theme-toggle button underneath it).
_OVERLAY_JS_PATH = DEMO_DIR / "professional_video_overlay.js"
_OVERLAY_JS = _OVERLAY_JS_PATH.read_text(encoding="utf-8")


@dataclass(frozen=True)
class Pacing:
    """WHAT: Wall-clock hold durations (seconds) for each beat of the
    recorded walkthrough.

    WHY: A Playwright video's recorded length is the real wall-clock time
    its browser context stays open. Since the (default, mocked) pipeline
    itself can finish in well under a minute, each beat deliberately holds
    its caption on screen for a fixed duration so the overall recording
    reliably lands inside the required 2-5 minute band regardless of how
    fast the underlying pipeline actually runs.

    HOW: Construct via `from_target_seconds()` rather than the
    constructor directly, so the 2-5 minute invariant is enforced in one
    place.
    """

    intro_seconds: float
    typing_seconds: float
    launch_seconds: float
    per_stage_seconds: float
    gate_seconds: float
    outro_seconds: float

    @property
    def total_seconds(self) -> float:
        """WHAT: The full estimated recording length this pacing implies."""
        return (
            self.intro_seconds
            + self.typing_seconds
            + self.launch_seconds
            + self.per_stage_seconds * len(STAGE_ORDER)
            + self.gate_seconds
            + self.outro_seconds
        )

    @classmethod
    def from_target_seconds(cls, target_seconds: float) -> "Pacing":
        """WHAT: Builds a `Pacing` whose total lands inside the mandatory
        [120, 300] second (2-5 minute) band.

        ARGS:
            target_seconds (float): Desired total video length in
                seconds; clamped to [120, 300] before use.

        RETURNS:
            Pacing: fixed intro/typing/launch/gate/outro overhead plus an
            equal per-stage caption hold spread across the 8 fixed
            pipeline stages.
        """
        target = max(120.0, min(300.0, target_seconds))
        intro, typing, launch, gate, outro = 8.0, 6.0, 3.0, 15.0, 10.0
        overhead = intro + typing + launch + gate + outro
        remaining = max(0.0, target - overhead)
        per_stage = max(10.0, remaining / len(STAGE_ORDER))
        pacing = cls(intro, typing, launch, per_stage, gate, outro)
        assert 100.0 <= pacing.total_seconds <= 320.0, (
            f"Pacing total {pacing.total_seconds:.1f}s drifted outside the "
            "expected band — check STAGE_ORDER length or overhead constants."
        )
        return pacing


def _truncate(text: str, limit: int = 240) -> str:
    """WHAT: Caps caption body text length so the lower-third never
    overflows the recorded viewport.
    """
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _inject_overlay(page: Page) -> None:
    """WHAT: Injects the caption/topbar/progress-bar/title-card overlay
    described in `_OVERLAY_JS` into the current page.
    """
    page.evaluate(_OVERLAY_JS)


def _set_topbar(page: Page, title: str, stage_text: str) -> None:
    page.evaluate("([t, s]) => window.__demoSetTopbar(t, s)", [title, stage_text])


def _set_progress(page: Page, pct: float) -> None:
    page.evaluate("(p) => window.__demoSetProgress(p)", pct)


def _set_caption(page: Page, heading: str, body: str) -> None:
    page.evaluate(
        "([h, b]) => window.__demoSetCaption(h, b)", [heading, _truncate(body)]
    )


def _clear_caption(page: Page) -> None:
    page.evaluate("() => window.__demoClearCaption()")


def _show_card(page: Page, title: str, subtitle: str, extra: str) -> None:
    page.evaluate(
        "([t, s, e]) => window.__demoShowCard(t, s, e)", [title, subtitle, extra]
    )


def _hide_card(page: Page) -> None:
    page.evaluate("() => window.__demoHideCard()")


def _show_intro_card(
    page: Page, theme: str, prompt_text: str, hold_seconds: float
) -> None:
    """WHAT: Full-screen branded intro card, held for `hold_seconds`."""
    _show_card(
        page,
        "Engineering Studio AI",
        f"{theme.title()} Mode — Full Pipeline Walkthrough",
        f'Brief: "{prompt_text}"  |  {DISCLAIMER}',
    )
    page.wait_for_timeout(int(hold_seconds * 1000))
    _hide_card(page)


def _show_outro_card(page: Page, verdict_text: str, hold_seconds: float) -> None:
    """WHAT: Full-screen branded outro card summarizing the run, held for
    `hold_seconds` before the recording ends.
    """
    _show_card(
        page,
        "Run Complete",
        "Research -> Parallel Specialists -> Challenge Division -> Quality Gate",
        _truncate(verdict_text, 280)
        or "Every stage ran end-to-end under a single certifying pipeline.",
    )
    page.wait_for_timeout(int(hold_seconds * 1000))


def _type_brief(page: Page, prompt_text: str, hold_seconds: float) -> None:
    """WHAT: Simulates realistic human typing of the product brief,
    spread across roughly `hold_seconds`.
    """
    delay_ms = max(15.0, min(80.0, (hold_seconds * 1000.0) / max(1, len(prompt_text))))
    _set_caption(
        page,
        "Product Brief",
        "A single natural-language brief is all the pipeline needs to start.",
    )
    field = page.locator("#brief-input")
    field.click()
    field.fill("")
    field.press_sequentially(prompt_text, delay=delay_ms)


def _record_scenario(page: Page, theme: str, prompt_text: str, pacing: Pacing) -> None:
    """WHAT: Drives one full pipeline cycle end-to-end in the given theme,
    holding the captioned overlay on screen long enough to land the
    overall recording inside the required 2-5 minute band.

    WHY: This is the single function responsible for the "entire
    scenario" the user asked for — brief entry through the Quality Gate
    verdict — narrated via burned-in captions instead of a voiceover.

    HOW: Toggles theme first (if needed) and waits for the backend health
    check BEFORE the overlay is injected — this ordering matters even
    though every overlay element is `pointer-events: none`, since it
    guarantees the real `#theme-toggle` button is never covered by
    anything while Playwright clicks it. Only then does it show a
    branded intro card, type the brief, launch the run, walk
    `STAGE_ORDER` waiting for each stage's real `data-state` to flip to
    `"done"` before holding its caption, and finally show the Quality
    Gate verdict plus a branded outro card.
    """
    if theme == "light":
        page.click("#theme-toggle")
        page.wait_for_function("document.documentElement.dataset.theme === 'light'")
    page.wait_for_selector('#server-status[data-state="ok"]', timeout=10_000)
    _inject_overlay(page)

    _set_topbar(page, "Engineering Studio AI", "Preparing walkthrough…")
    _show_intro_card(page, theme, prompt_text, pacing.intro_seconds)

    _type_brief(page, prompt_text, pacing.typing_seconds)
    _clear_caption(page)

    page.click("#launch-button")
    page.wait_for_selector("#stage-grid", state="visible", timeout=10_000)
    _set_topbar(page, "Engineering Studio AI", "Run launched — dispatching stages…")
    _set_caption(
        page,
        "Orchestrator",
        "Decomposes the brief and dispatches each discipline in the correct order.",
    )
    page.wait_for_timeout(int(pacing.launch_seconds * 1000))

    total = len(STAGE_ORDER)
    for index, stage_id in enumerate(STAGE_ORDER, start=1):
        heading, body = STAGE_CAPTIONS[stage_id]
        _set_topbar(page, "Engineering Studio AI", f"Stage {index} of {total}: {heading}")
        selector = f'.stage-card[data-stage="{stage_id}"] .stage-card__status'
        page.wait_for_selector(f'{selector}[data-state="done"]', timeout=30_000)
        _set_caption(page, heading, body)
        _set_progress(page, (index / total) * 100.0)
        page.wait_for_timeout(int(pacing.per_stage_seconds * 1000))

    page.wait_for_selector("#gate-banner", state="visible", timeout=10_000)
    verdict_text = page.inner_text("#gate-banner").strip()
    _set_topbar(page, "Engineering Studio AI", "Run complete")
    _set_caption(page, "Quality Gate Verdict", verdict_text)
    page.wait_for_timeout(int(pacing.gate_seconds * 1000))

    _show_outro_card(page, verdict_text, pacing.outro_seconds)


def _record_one_video(
    browser: Browser,
    base_url: str,
    theme: str,
    prompt: dict[str, str],
    pacing: Pacing,
    video_dir: Path,
    screenshots_dir: Path,
) -> bool:
    """WHAT: Records one full-cycle, captioned walkthrough video for a
    single (theme, prompt) combination and renames the resulting `.webm`
    to a stable, descriptive filename.

    WHY: Returns a bool (success/failure) rather than raising, so
    `main()`'s batch loop can attempt every (theme, prompt) combination
    even if one recording hits a transient error (e.g. a selector
    timeout) — one bad video must never silently abort the rest of the
    batch. The `.webm` is still renamed/kept on a failure, since a
    partial recording is still useful for debugging.

    RETURNS:
        bool: `True` if the scenario completed and the video was saved;
        `False` if an exception was caught (already logged to stderr).
    """
    context = browser.new_context(
        record_video_dir=str(video_dir),
        record_video_size=VIEWPORT,
        viewport=VIEWPORT,
    )
    page = context.new_page()
    started = time.monotonic()
    success = True
    try:
        page.goto(base_url)
        _record_scenario(page, theme, prompt["text"], pacing)
        slug = _slugify(prompt["text"])
        page.screenshot(path=str(screenshots_dir / f"{slug}_{theme}_final.png"))
    except Exception as exc:  # noqa: BLE001 - reported below, batch must continue
        success = False
        print(f"[{theme}] {prompt['id']}: FAILED - {exc}", file=sys.stderr)
    finally:
        video = page.video
        page.close()
        context.close()  # flushes the .webm video file to disk

    elapsed = time.monotonic() - started
    final_path = video_dir / f"{prompt['id']}_{theme}.webm"
    if video is not None:
        raw_path = Path(video.path())
        if raw_path.exists():
            if final_path.exists():
                final_path.unlink()
            raw_path.rename(final_path)

    if not success:
        return False

    in_band = 115.0 <= elapsed <= 320.0
    flag = "OK" if in_band else "WARNING: outside the 2-5 minute band"
    print(
        f"[{theme}] {prompt['id']}: recorded {elapsed:.1f}s "
        f"({elapsed / 60:.2f} min) -> {final_path.name} ({flag})"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--theme", choices=["light", "dark", "both"], default="both")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use the real Fireworks-backed pipeline (Mode A) instead of the "
        "default deterministic mocked pipeline (Mode B, requires no API key).",
    )
    parser.add_argument(
        "--target-duration",
        type=float,
        default=200.0,
        help="Target seconds per video, clamped to the mandatory 120-300s "
        "(2-5 minute) band (default: 200).",
    )
    parser.add_argument(
        "--prompts-file",
        type=Path,
        default=DEFAULT_PROMPTS_FILE,
        help=f"Path to the demo prompts JSON file (default: {DEFAULT_PROMPTS_FILE.relative_to(REPO_ROOT)}).",
    )
    parser.add_argument(
        "--prompt-id",
        action="append",
        default=None,
        help="Limit to specific prompt id(s) from demo_prompts.json (repeatable); "
        "default: all confirmed prompts.",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Local debugging escape hatch only — shows the browser window "
        "instead of running headless. Never use this for batch generation.",
    )
    args = parser.parse_args()

    prompts = _load_prompts(args.prompts_file)
    if args.prompt_id:
        wanted = set(args.prompt_id)
        prompts = [p for p in prompts if p["id"] in wanted]
        if not prompts:
            print(f"No prompts matched --prompt-id {sorted(wanted)}", file=sys.stderr)
            return 1

    themes = ["light", "dark"] if args.theme == "both" else [args.theme]
    pacing = Pacing.from_target_seconds(args.target_duration)
    print(
        f"Pacing: ~{pacing.total_seconds:.0f}s ({pacing.total_seconds / 60:.1f} min) "
        f"per video x {len(themes)} theme(s) x {len(prompts)} prompt(s)"
    )

    # WHAT: One (theme, prompt_id) -> success bool per attempted video.
    # WHY: Every combination is always attempted regardless of earlier
    # failures (see `_record_one_video`'s try/except) so a single bad
    # recording never costs the rest of the batch; this dict is printed
    # as a final summary and drives the process exit code.
    results: dict[tuple[str, str], bool] = {}

    process, base_url = _start_server(live=args.live)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not args.headed)
            for theme in themes:
                video_dir = RECORDINGS_ROOT / "video" / theme
                screenshots_dir = RECORDINGS_ROOT / "screenshots" / theme
                video_dir.mkdir(parents=True, exist_ok=True)
                screenshots_dir.mkdir(parents=True, exist_ok=True)
                for prompt in prompts:
                    ok = _record_one_video(
                        browser, base_url, theme, prompt, pacing, video_dir, screenshots_dir
                    )
                    results[(theme, prompt["id"])] = ok
            browser.close()
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

    succeeded = sum(1 for ok in results.values() if ok)
    print(f"\n{succeeded}/{len(results)} videos completed successfully:")
    for (theme, prompt_id), ok in results.items():
        print(f"  [{'OK  ' if ok else 'FAIL'}] {theme}/{prompt_id}")
    print(f"Professional demo videos saved under {RECORDINGS_ROOT}")
    return 0 if succeeded == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
