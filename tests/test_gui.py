"""WHAT: Unit/behavioral tests for engineering_studio.gui (W6b textual TUI).
WHY: Must prove the pure formatting helper is correct in isolation and
that the full `EngineeringStudioApp` widget wiring (input -> button ->
log) behaves correctly, headlessly, via `textual`'s `Pilot` API.
HOW: `format_pipeline_outcome()` is tested as a plain function (no event
loop). `EngineeringStudioApp` is driven via `app.run_test()` (a
`textual.pilot.Pilot`), run under `pytest-anyio` (the `anyio` package's
built-in pytest plugin — no extra `pytest-asyncio` dependency needed).
`sdk.run_pipeline` is monkeypatched throughout; no real network/model call.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engineering_studio import sdk
from engineering_studio.exceptions import ModelUnavailableError
from engineering_studio.gui import EngineeringStudioApp, format_pipeline_outcome
from engineering_studio.models import PipelineResult

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def test_format_pipeline_outcome_renders_brief_and_artifacts(tmp_path: Path) -> None:
    result = PipelineResult.from_pipeline_outputs(
        "build a drone", {"research": tmp_path / "research" / "output.md"}
    )

    text = format_pipeline_outcome(result)

    assert "build a drone" in text
    assert "research" in text
    assert str(tmp_path / "research" / "output.md") in text


async def test_app_runs_pipeline_successfully_on_button_press(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake_outputs = {"research": tmp_path / "research" / "output.md"}
    monkeypatch.setattr(sdk, "run_pipeline", lambda brief, root: fake_outputs)
    app = EngineeringStudioApp(artifacts_root=tmp_path)

    async with app.run_test() as pilot:
        brief_input = app.query_one("#brief_input")
        brief_input.value = "build a drone"
        await pilot.click("#run_button")
        await pilot.pause()

        output_log = app.query_one("#output_log")
        rendered = "\n".join(str(line) for line in output_log.lines)
        assert "build a drone" in rendered
        assert "research" in rendered


async def test_app_shows_validation_error_without_calling_pipeline(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def _unexpected_call(*args: object, **kwargs: object) -> None:
        raise AssertionError("run_pipeline should not be called for invalid input")

    monkeypatch.setattr(sdk, "run_pipeline", _unexpected_call)
    app = EngineeringStudioApp(artifacts_root=tmp_path)

    async with app.run_test() as pilot:
        brief_input = app.query_one("#brief_input")
        brief_input.value = "   "
        await pilot.click("#run_button")
        await pilot.pause()

        output_log = app.query_one("#output_log")
        rendered = "\n".join(str(line) for line in output_log.lines)
        assert "Invalid product brief" in rendered


async def test_app_shows_model_unavailable_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def _raise(brief: str, root: Path) -> dict[str, Path]:
        raise ModelUnavailableError("network down")

    monkeypatch.setattr(sdk, "run_pipeline", _raise)
    app = EngineeringStudioApp(artifacts_root=tmp_path)

    async with app.run_test() as pilot:
        brief_input = app.query_one("#brief_input")
        brief_input.value = "build a drone"
        await pilot.click("#run_button")
        await pilot.pause()

        output_log = app.query_one("#output_log")
        rendered = "\n".join(str(line) for line in output_log.lines)
        assert "Model call failed" in rendered
        assert "network down" in rendered


async def test_app_shows_pipeline_execution_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from engineering_studio.exceptions import PipelineExecutionError

    def _raise(brief: str, root: Path) -> dict[str, Path]:
        raise PipelineExecutionError("boom")

    monkeypatch.setattr(sdk, "run_pipeline", _raise)
    app = EngineeringStudioApp(artifacts_root=tmp_path)

    async with app.run_test() as pilot:
        brief_input = app.query_one("#brief_input")
        brief_input.value = "build a drone"
        await pilot.click("#run_button")
        await pilot.pause()

        output_log = app.query_one("#output_log")
        rendered = "\n".join(str(line) for line in output_log.lines)
        assert "Pipeline execution failed" in rendered


async def test_button_pressed_event_for_other_widget_is_ignored(tmp_path: Path) -> None:
    app = EngineeringStudioApp(artifacts_root=tmp_path)
    async with app.run_test():
        from textual.widgets import Button

        other_button = Button("other", id="not_run_button")
        # Directly exercise the guard clause without a real widget mount.
        event = Button.Pressed(other_button)
        app.on_button_pressed(event)
        output_log = app.query_one("#output_log")
        assert output_log.lines == []


def test_default_artifacts_root_matches_cli_default() -> None:
    app = EngineeringStudioApp()
    assert app.client.artifacts_root == Path("runs") / "latest" / "artifacts"
