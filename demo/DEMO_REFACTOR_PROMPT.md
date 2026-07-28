1.

---

title: "Demo Scripts Refactor — Task Specification"
version: "2026.1.0.0"
date: "2026-07-21"
status: "Draft — Pending Approval"
---

# PROMPT: Archive + Refactor `playwright_demo_script.py` /

`professional_video_demo.py` into `scripts/_*`-style packages

> Companion to `DEMO_REFACTOR_PLAN.md` (read that first — this is the
> literal, ordered task list an executor follows once the plan is
> approved). Do not start Task 1 until the user has explicitly approved
> both files.

## Task 1 — Archive originals

1.1. Create `demo/_archive/`.
1.2. `git mv` (preserve history) these 3 files into it unchanged:
     `demo/playwright_demo_script.py`,
     `demo/professional_video_demo.py`,
     `demo/professional_video_overlay.js`.
1.3. Write `demo/_archive/README.md` (WHAT/WHY/HOW, 1 short paragraph +
     pointer table to the two replacement packages).

## Task 2 — Make `demo/` a real package

2.1. Add `demo/__init__.py` (empty, docstring only).
2.2. Confirm `run_demo_sequence.py` still runs standalone
     (`python demo/run_demo_sequence.py --help`) — its own import style
     is untouched.

## Task 3 — Build `demo/_playwright_demo_script/`

3.1. Scaffold the package tree from `DEMO_REFACTOR_PLAN.md` §2.
3.2. Port logic 1:1 from the archived file into
     `core/naming.py` (`_slugify`), `core/server.py`
     (`_free_port`, `_start_server`), `core/recorder.py` (`_record_one`
     renamed `record_scenario`), preserving exact behavior (same
     selectors, timeouts, health-check loop, CLI flags).
3.3. `exceptions/errors.py`: define `PlaywrightDemoError` (base),
     `ServerStartError`, `RecordingError` — raise these instead of
     bare `RuntimeError`/`requests.RequestException` propagation where
     the original used ad hoc errors.
3.4. `util/pipeline.py`: `build_playwright_demo_runner(args) -> Runner`
     dataclass/class whose `.run() -> int` reproduces `main()`'s current
     body (server start → per (theme,prompt) loop → teardown → exit
     code).
3.5. `util/reporter.py`: extract the two `print(...)` result lines into
     a small reporter (mirrors `_sync_submodules/util/reporter.py`
     shape) — same stdout format, byte-for-byte.
3.6. `main.py`: argparse (identical flags/help text) → `build_...(args)`
     → `.run()` → `sys.exit`.
3.7. `__init__.py`: re-export public API. `__main__.py`: delegates to
     `main.main()`.

## Task 4 — Build `demo/_professional_video_demo/`

4.1. Scaffold the package tree from `DEMO_REFACTOR_PLAN.md` §3.
4.2. Move `professional_video_overlay.js` content verbatim into
     `assets/overlay.js`; `core/overlay.py` reads it via
     `Path(__file__).resolve().parent.parent / "assets" / "overlay.js"`.
4.3. Port `Pacing` (+ `STAGE_ORDER`, `STAGE_CAPTIONS`, `DISCLAIMER`,
     `VIEWPORT`) into `core/pacing.py` unchanged (same 120-300s
     assertion band).
4.4. Port `_truncate`, `_type_brief`, `_record_scenario` into
     `core/scenario.py`; port `_record_one_video` into
     `core/recorder.py`.
4.5. `exceptions/errors.py`: `ProfessionalDemoError` (base),
     `PacingError` (raised by `Pacing.from_target_seconds` if the
     post-construction assertion would fail — convert the bare
     `assert` into a raised, catchable exception instead, closing a
     real gap the original had: an `AssertionError` is not a
     documented public contract).
4.6. `util/pipeline.py` / `util/reporter.py` / `main.py` /
     `__init__.py` / `__main__.py`: same shape as Task 3, preserving
     the existing resilient try/except-per-video batch behavior and
     final PASS/FAIL summary + exit code.
4.7. Both packages' `core/*` import `demo._playwright_demo_script`'s
     `naming`/`server` modules for shared helpers (no duplication).

## Task 5 — Tests (mocked layer, 100% coverage gate)

5.1. `tests/demo/conftest.py`: `FakePage`, `FakeContext`, `FakeBrowser`,
     `FakeVideo` test doubles recording every method call
     (`.click`, `.fill`, `.evaluate`, `.wait_for_selector`,
     `.wait_for_timeout`, `.screenshot`, `.inner_text`, `.goto`) so
     assertions can check exact call sequences without a real browser.
5.2. Write `tests/demo/unit/*` and `tests/demo/integration/*` per
     `DEMO_REFACTOR_PLAN.md` §5 — cover every branch (success path,
     `--live` path, forced exception mid-batch, pacing out-of-band
     clamp, `--prompt-id` filtering with zero matches, missing overlay
     asset file, server-health-timeout path).
5.3. Run `pytest tests/demo --ignore=tests/demo/e2e --cov=demo._playwright_demo_script --cov=demo._professional_video_demo --cov-report=term-missing --cov-fail-under=100` until green at 100%.

## Task 6 — Real-browser e2e + performance smoke

6.1. `tests/demo/e2e/test_real_browser_smoke.py`: real `sync_playwright`,
     real FastAPI/uvicorn server (`ENGINEERING_STUDIO_FAKE_PIPELINE=1`),
     1 theme x 1 prompt, `--target-duration 120` equivalent, asserts a
     real `.webm` + screenshot file exist and are non-empty. Skip
     (not fail) with a clear reason if Chromium isn't installed.
6.2. `tests/demo/performance/test_pacing_performance.py`: bounded-time
     assertions using `FakeBrowser` only (no real I/O) — e.g. building
     and running a 6-video mocked batch completes under a fixed budget
     (documented rationale, not an arbitrary number).
6.3. Run `pytest tests/demo/e2e tests/demo/performance -v`.

## Task 7 — Full regression + end-to-end run

7.1. Re-run existing root suite unchanged: `ruff check .`, `mypy src`,
     `pytest --cov=engineering_studio --cov-report=term-missing      --cov-fail-under=100 -v` — must stay green (zero regressions).
7.2. One real full manual run of each new CLI end-to-end:
     `python -m demo._playwright_demo_script --theme light` and
     `python -m demo._professional_video_demo --theme light      --prompt-id <one-id> --target-duration 120` — confirm real output
     files land under `demo/recordings/...` exactly as before.

## Task 8 — Documentation

8.1. `engineering-studio-ai/reports/DEMO_REFACTOR_REPORT.md` — full
     report (what changed, test results/coverage numbers, standards
     citations, before/after file tree).
8.2. `engineering-studio-ai/CHATS/CHAT_2026-07-21_demo-scripts-refactor.md`
     and `CodingStandardsRef/markdowns/chats/CHAT_2026-07-21_demo-scripts-refactor.md`
     — session transcript archive (per each repo's own convention).
8.3. Update `demo/README.md` file table + append one dated bullet to
     repo-memory `vision-docs-conventions.md`.

## Output Format (per turn, while executing this prompt)

```json
{"task": "N.M", "status": "done|blocked", "evidence": ["path or command output"], "requires_human_review": false}
```

## Changelog

| Version    | Date       | Description                      |
| ---------- | ---------- | -------------------------------- |
| 2026.1.0.0 | 2026-07-21 | Initial draft, pending approval. |
