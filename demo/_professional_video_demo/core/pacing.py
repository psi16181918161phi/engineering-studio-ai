"""WHAT: Fixed pipeline-stage metadata and the `Pacing` value object
controlling how long each recorded beat is held on screen.
WHY: Isolated as pure data/pure-function code (FP §3) — no I/O, trivially
unit tested. Mirrors the original `professional_video_demo.py` module
constants 1:1 (`STAGE_ORDER`, `STAGE_CAPTIONS`, `DISCLAIMER`, `VIEWPORT`,
`Pacing`).
HOW: `Pacing.from_target_seconds()` is the only supported construction
path; it clamps the target into [120, 300]s, spreads the remainder
evenly across the 8 fixed stages, and raises `PacingError` (rather than
asserting) if the computed total ever drifts outside the [100, 320]s
sanity band.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..exceptions.errors import PacingError

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

# WHAT: 1080p, the de-facto minimum "professional" resolution for a
# YouTube-grade upload.
VIEWPORT = {"width": 1920, "height": 1080}


@dataclass(frozen=True)
class Pacing:
    """WHAT: Wall-clock hold durations (seconds) for each beat of the
    recorded walkthrough.

    WHY: A Playwright video's recorded length is the real wall-clock time
    its browser context stays open. Since the (default, mocked) pipeline
    itself can finish in well under a minute, each beat deliberately
    holds its caption on screen for a fixed duration so the overall
    recording reliably lands inside the required 2-5 minute band
    regardless of how fast the underlying pipeline actually runs.

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
            Pacing: Fixed intro/typing/launch/gate/outro overhead plus an
            equal per-stage caption hold spread across the 8 fixed
            pipeline stages.

        RAISES:
            PacingError: If the computed total unexpectedly drifts
            outside the [100, 320] second sanity band (would indicate a
            bug in `STAGE_ORDER` length or the overhead constants below,
            not a user-input error).
        """
        target = max(120.0, min(300.0, target_seconds))
        intro, typing, launch, gate, outro = 8.0, 6.0, 3.0, 15.0, 10.0
        overhead = intro + typing + launch + gate + outro
        remaining = max(0.0, target - overhead)
        per_stage = max(10.0, remaining / len(STAGE_ORDER))
        pacing = cls(intro, typing, launch, per_stage, gate, outro)
        if not (100.0 <= pacing.total_seconds <= 320.0):
            raise PacingError(
                f"Pacing total {pacing.total_seconds:.1f}s drifted outside the "
                "expected band — check STAGE_ORDER length or overhead constants."
            )
        return pacing
