"""Run the declared local mutation scope without altering source files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src" / "engineering_studio"
_TIMEOUT = 45.0


@dataclass(frozen=True)
class Mutation:
    """WHAT: Name a fault injection and its test oracle.

    WHY: Keep the finite mutation scope auditable and reproducible.
    HOW: Replace a declared occurrence of exact source text in one module.
    """

    name: str
    module: str
    original: str
    replacement: str
    tests: str
    occurrences: int = 1
    index: int = 0

    def inject(self, source: str) -> str:
        """WHAT: Substitute exactly one declared source occurrence.

        WHY: Stale or ambiguous anchors must block the gate.
        HOW: Check the original match count before selecting the occurrence.
        """
        parts = source.split(self.original)
        if len(parts) != self.occurrences + 1 or not 0 <= self.index < self.occurrences:
            raise ValueError(f"{self.name}: stale or ambiguous source anchor")
        start = self.original.join(parts[: self.index + 1])
        end = self.original.join(parts[self.index + 1 :])
        return start + self.replacement + end


def _parser_mutations() -> tuple[Mutation, ...]:
    """WHAT: List the parser's declared fault injections.

    WHY: Guard stage ownership and format validation at their fault boundaries.
    HOW: Use one exact source edit per mutant and the focused parser tests.
    """
    edits = (
        ("section-boundary", 'if token.group("section") is not None:', "if False:"),
        ("missing-body", "if slug is not None and slug not in specs:", "if False:"),
        ("invalid-title", "if not slug:", "if False:"),
        ("open-fence", 'if token.group("unclosed") is not None:', "if False:"),
        ("other-fence", 'or token.group("info").strip() != "markdown"', "or False"),
        ("orphan", "if slug is None:", "if False:"),
        ("nested-fence", "if _NESTED_SPEC_FENCE.search(raw_body):", "if False:"),
        ("empty-block", "if not body:", "if False:"),
        ("no-stages", "if not specs:", "if False:"),
        (
            "eof",
            "    _require_stage_body(path, slug, stage_line, specs)\n    if not specs:",
            "    if not specs:",
        ),
        ("slug-normalization", "title.lower()", "title"),
        ("body-trimming", "body = raw_body.strip()", "body = raw_body"),
        ("fence-length", "(?P=marker)(?P=delimiter)*", "(?P=delimiter){3,}"),
    )
    tests = "tests/test_task_specs.py"
    return tuple(Mutation(name, "task_specs.py", old, new, tests) for name, old, new in edits) + (
        Mutation("duplicate-slug", "task_specs.py", "if slug in specs:", "if False:", tests, 2),
        Mutation("duplicate-body", "task_specs.py", "if slug in specs:", "if False:", tests, 2, 1),
    )


def _coverage_mutations() -> tuple[Mutation, ...]:
    """WHAT: Exercise the four repaired branch boundaries.

    WHY: Literal coverage alone does not validate behavior.
    HOW: Force the opposite guard result and require an assertion failure.
    """
    return (
        Mutation(
            "parallel-first-error",
            "agents/orchestrator.py",
            "if first_error is None:",
            "if True:",
            "tests/test_orchestrator.py",
        ),
        Mutation(
            "omit-reasoning-effort",
            "fireworks_client.py",
            "if self.reasoning_effort is not None:",
            "if True:",
            "tests/test_fireworks_client_complete.py",
        ),
        Mutation(
            "preserve-restart-detail",
            "runs.py",
            "if run.detail is None:",
            "if True:",
            "tests/test_runs.py",
        ),
        Mutation(
            "optional-frontend",
            "webapp/app.py",
            "if _FRONTEND_DIR.is_dir():",
            "if True:",
            "tests/test_webapp.py",
        ),
    )


_WORKER = """
import importlib.machinery
import os
from pathlib import Path
import sys

target = os.environ.pop("STUDIO_MUTATION_TARGET", "")
if target:
    original = importlib.machinery.SourceFileLoader.get_code
    def load(self, fullname):
        if Path(self.path).resolve() == Path(target):
            sys._studio_mutation_loaded = True
            return compile(Path(os.environ["STUDIO_MUTATION_FILE"]).read_bytes(), target, "exec")
        return original(self, fullname)
    importlib.machinery.SourceFileLoader.get_code = load

import pytest

status = pytest.main(sys.argv[1:])
if target and not getattr(sys, "_studio_mutation_loaded", False):
    raise SystemExit(6)
raise SystemExit(status)
"""


def classify(exit_code: int, report: Path, mutant: bool) -> tuple[str, list[str]]:
    """WHAT: Classify the run from its exit code and JUnit test cases.

    WHY: Collection errors, timeouts, skips and empty runs cannot count as kills.
    HOW: Accept only consistent passing or test-call failure reports.
    """
    try:
        cases = list(ET.parse(report).iter("testcase"))
    except OSError, ET.ParseError:
        return "inconclusive", []
    if not cases or any(
        case.find("error") is not None or case.find("skipped") is not None for case in cases
    ):
        return "inconclusive", []
    failures = [
        f"{case.get('classname')}::{case.get('name')}"
        for case in cases
        if case.find("failure") is not None
    ]
    if exit_code == 0 and not failures:
        return ("survived" if mutant else "baseline-pass"), []
    if exit_code == 1 and failures and mutant:
        return "killed", failures
    return "inconclusive", failures


def _run(work: Path, tests: str, variant: Mutation | None) -> dict:
    """WHAT: Execute one bounded pytest worker in an isolated directory.

    WHY: Avoid stale imports, coverage flags, persistent runs, and source writes.
    HOW: Intercept only the declared module loader in the child and retain JUnit.
    """
    env = dict(
        os.environ,
        PYTHONPATH=str(_ROOT / "src"),
        PYTHONDONTWRITEBYTECODE="1",
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
        PYTEST_ADDOPTS="",
    )
    env.pop("STUDIO_MUTATION_TARGET", None)
    env.pop("STUDIO_MUTATION_FILE", None)
    record = {"name": variant.name if variant else "baseline", "tests": tests}
    if variant:
        path = _SRC / variant.module
        source = path.read_bytes()
        record.update(
            module=variant.module,
            source_sha256=hashlib.sha256(source).hexdigest(),
            original=variant.original,
            replacement=variant.replacement,
        )
        try:
            changed = variant.inject(source.decode("utf-8").replace("\r\n", "\n"))
        except ValueError as error:
            return dict(record, outcome="inconclusive", reason=str(error))
        mutant_file = work / "mutant.py"
        mutant_file.write_bytes(changed.encode())
        env.update(
            STUDIO_MUTATION_TARGET=str(path.resolve()), STUDIO_MUTATION_FILE=str(mutant_file)
        )
    report = work / "pytest.xml"
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                _WORKER,
                "-q",
                "-c",
                str(_ROOT / "pyproject.toml"),
                "-o",
                "addopts=",
                "-p",
                "no:cacheprovider",
                "--junitxml",
                str(report),
                *(str(_ROOT / test) for test in tests.split()),
            ],
            cwd=work,
            env=env,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return dict(record, outcome="inconclusive", reason=type(error).__name__)
    outcome, failures = classify(result.returncode, report, variant is not None)
    return dict(
        record,
        outcome=outcome,
        killing_tests=failures,
        exit_code=result.returncode,
        diagnostic=(result.stdout + result.stderr)[-1600:] if outcome == "inconclusive" else "",
    )


def main() -> int:
    """WHAT: Verify all declared mutants and write a machine-readable report.

    WHY: Prevent a surviving mutant or failed baseline from passing the gate.
    HOW: Use one fresh directory per worker and require all results to be kills.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    mutants = _parser_mutations() + _coverage_mutations()
    baseline_tests = sorted({mutation.tests for mutation in mutants})
    with tempfile.TemporaryDirectory(prefix="studio-mutations-") as scratch:
        root = Path(scratch)
        baselines = []
        for index, tests in enumerate(baseline_tests):
            work = root / f"baseline-{index}"
            work.mkdir()
            baselines.append(_run(work, tests, None))
        results = []
        if baselines and all(run["outcome"] == "baseline-pass" for run in baselines):
            for mutant in mutants:
                work = root / mutant.name
                work.mkdir()
                results.append(_run(work, mutant.tests, mutant))
    killed = sum(result["outcome"] == "killed" for result in results)
    passed = bool(mutants) and killed == len(mutants)
    report = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "scope": "declared rollout mutants",
        "baselines": baselines,
        "required": len(mutants),
        "killed": killed,
        "passed": passed,
        "results": results,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{killed}/{len(mutants)} declared mutants killed; report: {args.report}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
