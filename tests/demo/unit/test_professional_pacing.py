"""WHAT: Unit tests for `demo._professional_video_demo.core.pacing`.
WHY: `Pacing` is pure data/logic (FP §3) — fully testable without any
browser or server.
HOW: Verifies clamping at both ends of the [120, 300]s band and forces
the otherwise-unreachable `PacingError` defensive branch by monkeypatching
`STAGE_ORDER` to an artificially long tuple.
"""

from __future__ import annotations

import pytest

from demo._professional_video_demo.core import pacing as pacing_module
from demo._professional_video_demo.core.pacing import STAGE_ORDER, Pacing
from demo._professional_video_demo.exceptions.errors import PacingError


def test_from_target_seconds_within_band() -> None:
    result = Pacing.from_target_seconds(200.0)
    assert 120.0 <= result.total_seconds <= 300.0


def test_from_target_seconds_clamps_low() -> None:
    result = Pacing.from_target_seconds(1.0)
    assert result.total_seconds >= 120.0


def test_from_target_seconds_clamps_high() -> None:
    result = Pacing.from_target_seconds(10_000.0)
    assert result.total_seconds <= 300.0


def test_total_seconds_matches_component_sum() -> None:
    result = Pacing(
        intro_seconds=8.0,
        typing_seconds=6.0,
        launch_seconds=3.0,
        per_stage_seconds=10.0,
        gate_seconds=15.0,
        outro_seconds=10.0,
    )
    expected = 8.0 + 6.0 + 3.0 + 10.0 * len(STAGE_ORDER) + 15.0 + 10.0
    assert result.total_seconds == expected


def test_from_target_seconds_raises_pacing_error_when_drifted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # An artificially long STAGE_ORDER forces per_stage_seconds * len(...)
    # past the [100, 320]s sanity band — this is the defensive branch that
    # can never trigger through the real, fixed 8-stage pipeline.
    monkeypatch.setattr(pacing_module, "STAGE_ORDER", tuple(f"stage-{i}" for i in range(40)))

    with pytest.raises(PacingError):
        Pacing.from_target_seconds(200.0)
