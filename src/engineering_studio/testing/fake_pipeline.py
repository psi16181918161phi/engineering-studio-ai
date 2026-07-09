"""WHAT: A deterministic, no-network stand-in for `agents.orchestrator.
run_pipeline`, used only when `ENGINEERING_STUDIO_FAKE_PIPELINE=1` is set
in the process environment.
WHY: Playwright end-to-end tests (Mode B, `tests/e2e/`) drive a *real*
`uvicorn` server as a subprocess to exercise the actual SSE wire contract
and browser rendering — but must never depend on a Fireworks API key or
real network access in CI (live-data-honesty: a CI-green e2e run must
never be mistaken for evidence the real model integration works; see
`docs/PLAYWRIGHT_INTEGRATION_PLAN.md` §3.2).
HOW: Emits the same "running" -> "done" `on_event` transitions, in the
same `STAGE_ORDER`, for every stage, writing a short, clearly-labeled
artifact file per stage so the frontend's "View output" / download
affordances have real (if synthetic) content to render. Small `time.
sleep` pauses between stages keep transitions visually distinguishable
for a screen recording, without meaningfully slowing the test suite.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

from engineering_studio.agents.orchestrator import STAGE_ORDER

EventCallback = Callable[[str, str, str | None], None]

# WHAT: Per-stage synthetic "thinking + result" artifact bodies.
# WHY: Gives the frontend's per-stage output panel and download links
# real, readable content in a Mode-B (mocked) recording instead of an
# empty placeholder, without pretending it came from a real model call.
_STAGE_LABELS: dict[str, str] = {
    "research": "Research & Problem Framing",
    "mechanical": "Mechanical Specialist",
    "electrical": "Electrical Specialist",
    "firmware": "Firmware Specialist",
    "simulation": "Simulation Specialist",
    "business": "Cost / Business / Legal",
    "challenge": "Challenge Division",
    "quality_gate": "Quality Gate",
}

# WHAT: Pause between each stage transition, in seconds.
# WHY: Long enough for a Playwright screenshot/video capture to observe a
# distinct "running" frame per stage; short enough to keep the full e2e
# suite fast (8 stages * ~0.3s ~= 2.4s of sleep per run).
_STAGE_DELAY_SECONDS = 0.3


def fake_run_pipeline(
    product_brief: str,
    artifacts_root: Path,
    on_event: EventCallback | None = None,
) -> dict[str, Path]:
    """WHAT: Deterministically "runs" every stage in `STAGE_ORDER`.

    ARGS:
        product_brief (str): The one-sentence demo prompt (echoed into
            each stage's artifact so a recording still looks tailored to
            the input).
        artifacts_root (Path): Root directory this run writes into.
        on_event (EventCallback | None): Notified "running" then "done"
            for every stage, matching the real pipeline's contract.

    RETURNS:
        dict[str, Path]: Mapping of stage name to its written artifact.
    """
    outputs: dict[str, Path] = {}
    for stage in STAGE_ORDER:
        if on_event is not None:
            on_event(stage, "running", None)
        time.sleep(_STAGE_DELAY_SECONDS)

        folder = artifacts_root / stage
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "output.md"
        label = _STAGE_LABELS.get(stage, stage)
        path.write_text(
            f"# {label} — Mock Output\n\n"
            f"**Product brief:** {product_brief}\n\n"
            "## Thinking\n\n"
            f"(Mode B / fake pipeline) Deterministic placeholder reasoning "
            f"for the `{stage}` stage — no live model call was made.\n\n"
            "## Result\n\n"
            f"Synthetic `{stage}` deliverable produced for CI-safe "
            "end-to-end demonstration and recording purposes.\n",
            encoding="utf-8",
        )
        outputs[stage] = path

        if on_event is not None:
            on_event(stage, "done", str(path))

    return outputs
