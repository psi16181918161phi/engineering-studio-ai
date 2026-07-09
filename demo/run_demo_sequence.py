"""WHAT: Deterministic, CLI-only (no browser) demo-rehearsal launcher that
runs each of the 3 confirmed demo prompts (`demo/demo_prompts.json`)
through the pipeline in a fixed order, writing artifacts to a
timestamped run folder and printing/saving run metadata for quick
presenter lookup.
WHY: `demo/playwright_demo_script.py` already exists for the *browser*
screenshot/video recording; this script complements it with a fast,
headless rehearsal path a presenter can run right before going on stage
to (a) pre-stage a known-good artifact set for the fallback flow in
`demo/demo-script.md` §Fallback plan, and (b) get a deterministic
timing/status readout without needing Playwright/a browser at all. Per
`AGENTS.md` §5 ("live-data honesty"), a failed/rate-limited stage is
reported as `error` in the manifest — never silently marked `done`.
HOW: Defaults to the deterministic, no-network fake pipeline
(`engineering_studio.testing.fake_pipeline.fake_run_pipeline`) — the
same mocked stand-in already used by `tests/e2e/` and the webapp's
`ENGINEERING_STUDIO_FAKE_PIPELINE=1` mode — so it never requires a
`FIREWORKS_API_KEY` unless `--live` is explicitly passed (matching the
opt-in-only-with-explicit-flag convention `playwright_demo_script.py`
already established). Each prompt's run gets its own
`<artifacts-root>/<run-timestamp>/<prompt-id>/` folder; a
`manifest.json` sibling file records per-prompt status, duration, and
artifact path for handoff to whoever is presenting.

Usage:
    python demo/run_demo_sequence.py [--live] [--artifacts-root PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:  # pragma: no cover - import path bootstrap
    sys.path.insert(0, str(SRC_ROOT))

from engineering_studio.exceptions import ModelUnavailableError  # noqa: E402

DEFAULT_PROMPTS_FILE = REPO_ROOT / "demo" / "demo_prompts.json"
DEFAULT_ARTIFACTS_ROOT = REPO_ROOT / "runs" / "demo_sequence"


def _load_prompts(prompts_file: Path) -> list[dict[str, str]]:
    """WHAT: Loads the confirmed demo prompt list from `demo_prompts.json`.

    ARGS:
        prompts_file (Path): Path to the JSON prompt manifest.

    RETURNS:
        list[dict[str, str]]: Each item has `id` and `text` keys, in the
        fixed order they appear in the file.
    """
    data = json.loads(prompts_file.read_text(encoding="utf-8"))
    prompts: list[dict[str, str]] = data["prompts"]
    return prompts


def _run_one(
    prompt_id: str, prompt_text: str, artifacts_root: Path, live: bool
) -> dict[str, Any]:
    """WHAT: Runs one prompt through the pipeline and times it.

    ARGS:
        prompt_id (str): Short id used for the artifacts subfolder name.
        prompt_text (str): The product brief sent to the pipeline.
        artifacts_root (Path): This prompt's dedicated artifacts folder.
        live (bool): `True` to use the real Fireworks-backed orchestrator;
            `False` (default) to use the deterministic fake pipeline.

    RETURNS:
        dict[str, Any]: One manifest entry — `id`, `text`, `mode`,
        `artifacts_root`, `status` (`"done"` or `"error"`),
        `duration_seconds`, `stages_completed`, and `error` (`None` on
        success).
    """
    artifacts_root.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    status = "done"
    error: str | None = None
    stages_completed: list[str] = []

    def _on_event(stage: str, state: str, _detail: str | None) -> None:
        if state == "done":
            stages_completed.append(stage)

    try:
        if live:
            from engineering_studio.agents.orchestrator import run_pipeline
        else:
            from engineering_studio.testing.fake_pipeline import (
                fake_run_pipeline as run_pipeline,
            )
        run_pipeline(prompt_text, artifacts_root, on_event=_on_event)
    except ModelUnavailableError as exc:
        status = "error"
        error = f"model unavailable: {exc}"
    except Exception as exc:  # noqa: BLE001 - report, never swallow silently
        status = "error"
        error = f"unexpected pipeline failure: {exc}"

    duration = time.monotonic() - started
    return {
        "id": prompt_id,
        "text": prompt_text,
        "mode": "live" if live else "mocked",
        "artifacts_root": str(artifacts_root.relative_to(REPO_ROOT)),
        "status": status,
        "duration_seconds": round(duration, 3),
        "stages_completed": stages_completed,
        "error": error,
    }


def _print_summary(results: list[dict[str, Any]]) -> None:
    """WHAT: Prints a concise PASS/FAIL table of the run to stdout."""
    header = f"{'ID':<24} {'STATUS':<8} {'DURATION(s)':<12} {'STAGES':<8} ARTIFACTS"
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            f"{r['id']:<24} {r['status'].upper():<8} "
            f"{r['duration_seconds']:<12} {len(r['stages_completed']):<8} "
            f"{r['artifacts_root']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use the real Fireworks-backed pipeline instead of the default "
        "deterministic mocked pipeline (requires FIREWORKS_API_KEY in .env).",
    )
    parser.add_argument(
        "--artifacts-root",
        type=Path,
        default=DEFAULT_ARTIFACTS_ROOT,
        help="Root directory this run's timestamped folder is created under "
        f"(default: {DEFAULT_ARTIFACTS_ROOT.relative_to(REPO_ROOT)}).",
    )
    parser.add_argument(
        "--prompts-file",
        type=Path,
        default=DEFAULT_PROMPTS_FILE,
        help=f"Path to the demo prompts JSON file (default: {DEFAULT_PROMPTS_FILE.relative_to(REPO_ROOT)}).",
    )
    args = parser.parse_args()

    prompts = _load_prompts(args.prompts_file)
    run_timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_root = args.artifacts_root / run_timestamp

    results: list[dict[str, Any]] = []
    for prompt in prompts:
        prompt_root = run_root / prompt["id"]
        result = _run_one(prompt["id"], prompt["text"], prompt_root, live=args.live)
        results.append(result)

    manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": "live" if args.live else "mocked",
        "run_root": str(run_root.relative_to(REPO_ROOT)),
        "results": results,
    }
    manifest_path = run_root / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    _print_summary(results)
    print(f"\nManifest saved to {manifest_path.relative_to(REPO_ROOT)}")

    any_failed = any(r["status"] != "done" for r in results)
    return 1 if any_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
