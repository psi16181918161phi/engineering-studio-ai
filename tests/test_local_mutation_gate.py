"""WHAT: Exercise the local mutation gate's evidence and anchor rules.

WHY: A broken runner must not report survivors or failed setup as kills.
HOW: Use minimal JUnit fixtures and exact source text without spawning pytest.
"""

from pathlib import Path

import pytest

from scripts.local_mutation_gate import Mutation, classify


@pytest.mark.parametrize(
    ("cases", "exit_code", "mutant", "expected"),
    [
        ("<testcase/>", 0, False, "baseline-pass"),
        ("<testcase/>", 0, True, "survived"),
        ("<testcase><failure/></testcase>", 1, True, "killed"),
        ("<testcase><failure/></testcase>", 1, False, "inconclusive"),
        ("<testcase><failure/></testcase>", 2, True, "inconclusive"),
        ("<testcase><error/></testcase>", 1, True, "inconclusive"),
        ("<testcase><skipped/></testcase>", 0, True, "inconclusive"),
        ("", 5, True, "inconclusive"),
    ],
)
def test_classification_requires_call_failure_in_a_real_run(
    tmp_path: Path, cases: str, exit_code: int, mutant: bool, expected: str
) -> None:
    """WHAT: Classify passing and failing workers by their evidence.

    WHY: No-tests, skipped and errored runs must all fail closed.
    HOW: Compare each JUnit and exit-code combination to its required verdict.
    """
    path = tmp_path / "result.xml"
    path.write_text(f"<testsuite>{cases}</testsuite>", encoding="utf-8")

    outcome, failures = classify(exit_code, path, mutant)

    assert outcome == expected
    if expected == "killed":
        assert len(failures) == 1


def test_missing_and_invalid_reports_are_inconclusive(tmp_path: Path) -> None:
    """WHAT: Handle unavailable reports. WHY: Preserve the evidence boundary.

    HOW: Test absent and unparseable XML even with pytest's failure exit code.
    """
    path = tmp_path / "result.xml"
    assert classify(1, path, True) == ("inconclusive", [])
    path.write_text("<unterminated", encoding="utf-8")
    assert classify(1, path, True) == ("inconclusive", [])


def test_injection_checks_cardinality_and_replaces_one_occurrence() -> None:
    """WHAT: Verify deterministic placement. WHY: Anchors must not drift.

    HOW: Change only the second occurrence, then reject missing or extra anchors.
    """
    variant = Mutation("condition", "example.py", "old", "new", "tests", 2, 1)
    assert variant.inject("old + old") == "old + new"
    for source in ("old", "old + old + old"):
        with pytest.raises(ValueError, match="stale or ambiguous"):
            variant.inject(source)
