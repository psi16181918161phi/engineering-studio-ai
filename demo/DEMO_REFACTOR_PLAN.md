# Demo Scripts Refactor — Plan

WHAT: Archive `playwright_demo_script.py` and `professional_video_demo.py`
(plus its sibling `professional_video_overlay.js`), then rebuild both as
`scripts/_*`-style packages (`__init__.py`/`__main__.py`/`main.py` +
`core/`/`exceptions/`/`util/`), with a 100%-covered unit/integration test
suite (mocked Playwright) and a separate real-browser e2e/performance
smoke suite, per `coding_stds/MOST_CITED_STANDARDS.md` Tier 0/1/3.

WHY: The two scripts currently live as flat, long, cross-importing
top-level files with zero test coverage. The parent repo's
`scripts/_sync_submodules` / `_lint_docs` / `_security_scan` /
`_patch_domain_registry` / `_translate_standards` packages are the
house-standard shape (SOLID SRP: scan/act/report split across
`core/`+`util/`, domain exceptions, thin `main.py` CLI). This refactor
brings the demo tooling in line with that shape and adds the coverage
gate this repo enforces everywhere else (`pyproject.toml`
`--cov-fail-under=100`, currently scoped only to `engineering_studio`
and silently excluding `demo/`).

HOW: See phases below. Nothing is implemented until this plan +
`DEMO_REFACTOR_PROMPT.md` are approved.

## 1. Archive (Tier-1 reversible move, no deletion)

- Create `demo/_archive/` (new folder).
- Move (git mv) into it, unchanged:
  - `demo/playwright_demo_script.py`
  - `demo/professional_video_demo.py`
  - `demo/professional_video_overlay.js`
- Add `demo/_archive/README.md`: one paragraph — what these are, why
  archived, pointer to the two new packages that replace them.

## 2. New package: `demo/_playwright_demo_script/`

Mirrors `scripts/_sync_submodules` shape exactly.

```
demo/_playwright_demo_script/
  __init__.py        # re-exports public API (SOLID OCP)
  __main__.py         # `python -m demo._playwright_demo_script`
  main.py              # argparse CLI, same flags as today (--theme, --live)
  core/
    server.py          # _free_port, _start_server (health-poll loop)
    naming.py           # _slugify
    recorder.py         # _record_one (per-scenario screenshot+video walk)
  exceptions/
    errors.py           # PlaywrightDemoError, ServerStartError, RecordingError
  util/
    pipeline.py         # build_playwright_demo_runner() -> orchestrates
                         #  start server -> per (theme,prompt) record -> teardown
    reporter.py          # prints per-video pass/fail + final summary
```

Behavior parity requirement: identical CLI flags/output/exit codes to
the archived original (`--theme`, `--live`), same `STAGE_ORDER` constant,
same recordings layout under `demo/recordings/{screenshots,video}/`.

## 3. New package: `demo/_professional_video_demo/`

Same shape; imports `naming._slugify` / `server._start_server` from
`demo._playwright_demo_script` (mirrors the original's cross-file
import) rather than duplicating them.

```
demo/_professional_video_demo/
  __init__.py
  __main__.py
  main.py                    # argparse CLI, same flags as today
  core/
    pacing.py                # Pacing dataclass + from_target_seconds()
    overlay.py                # _inject_overlay/_set_topbar/_set_progress/
                               #  _set_caption/_clear_caption/_show_card/
                               #  _hide_card/_show_intro_card/_show_outro_card
                               #  (reads sibling overlay.js asset)
    scenario.py                # _record_scenario, _type_brief, _truncate
    recorder.py                 # _record_one_video (per (theme,prompt) video)
  exceptions/
    errors.py                    # ProfessionalDemoError, PacingError
  util/
    pipeline.py                   # build_professional_demo_runner() -> batch loop
    reporter.py                    # per-video + final summary printing
  assets/
    overlay.js                     # moved verbatim from demo/_archive/
                                    #  professional_video_overlay.js
```

`STAGE_CAPTIONS`/`DISCLAIMER`/`VIEWPORT` constants move into
`core/pacing.py` or a small `core/constants.py` (kept next to what
references them, avoiding a god-module).

`run_demo_sequence.py`'s `_load_prompts` stays where it is (out of
scope — not one of the two named files); both new packages import it
the same way the originals did (same-directory sys.path trick is
replaced by a proper relative import since `demo/` becomes a real
package — see Section 6).

## 4. Standards compliance (grounded in attached `MOST_CITED_STANDARDS.md`)

- Tier 0/1: every new module gets a WHAT/WHY/HOW module docstring
  (`architecture/class_function_exceptors_decorator_args_detailed_principles.txt`,
  `architecture/unified_architecture_reference_detailed.txt`), SOLID SRP
  per file, one `main()` + `if __name__ == "__main__":` guard only in
  `main.py`.
- Tier 1 FP principles: `core/*` functions stay pure where feasible
  (`Pacing`, `_slugify`, `_truncate`) — I/O-performing functions
  (`_start_server`, recorder functions) isolated in their own modules.
- Tier 2: this plan + prompt use the mandated front-matter/TOC/Abstract
  structure is NOT required here (short planning docs, not
  `markdowns/visions/`-class docs) but headers keep WHAT/WHY/HOW.
- Tier 3 (`testing/testing_standards.txt`,
  `testing/test_coverage_100_pct_standards.txt`,
  `devops/cicd_standards.txt`): test taxonomy below matches the
  canonical unit/integration/e2e/performance categories; coverage gate
  set to 100% for the mocked (non-real-browser) layer.

## 5. Tests (per confirmed answer: mock Playwright for the 100%-coverage

   suite; real Playwright only for a separate, non-gated smoke test)

```
tests/demo/
  __init__.py
  conftest.py                          # shared fakes: FakePage, FakeBrowser,
                                        #  FakeContext, tmp recordings dirs
  unit/
    test_playwright_naming.py           # _slugify
    test_playwright_server.py            # _free_port/_start_server (mocked
                                          #  subprocess+requests)
    test_professional_pacing.py           # Pacing.from_target_seconds bounds
    test_professional_overlay.py           # overlay JS injection calls (FakePage)
    test_professional_scenario.py           # _record_scenario/_type_brief/_truncate
    test_errors.py                           # custom exception hierarchy
  integration/
    test_playwright_pipeline.py         # build_playwright_demo_runner() with
                                         #  FakeBrowser/FakeContext end-to-end
                                         #  through the pipeline, real argparse
    test_professional_pipeline.py       # build_professional_demo_runner()
                                          #  batch loop incl. one forced failure
                                          #  (asserts batch continues + exit code)
  e2e/
    test_real_browser_smoke.py          # REAL Playwright + REAL FastAPI/uvicorn
                                          #  demo server, --target-duration 120,
                                          #  1 theme x 1 prompt only; marked
                                          #  `@pytest.mark.e2e`, excluded from the
                                          #  default coverage run (matches
                                          #  existing `--ignore=tests/e2e` pattern)
  performance/
    test_pacing_performance.py           # Pacing math + batch-loop overhead
                                          #  stay within a bounded time budget
                                          #  using FakeBrowser (no real I/O) —
                                          #  asserts e.g. 100-iteration batch
                                          #  build completes under N ms;
                                          #  real per-video wall-clock timing
                                          #  is validated only in e2e/, not here
```

Coverage command (scoped to the two new demo packages, run separately
from the existing `engineering_studio`-scoped gate in root
`pyproject.toml`, which is untouched):

```
pytest tests/demo --ignore=tests/demo/e2e \
  --cov=demo._playwright_demo_script --cov=demo._professional_video_demo \
  --cov-report=term-missing --cov-fail-under=100
```

Real-browser smoke test run separately (slow, requires
`playwright install chromium`):

```
pytest tests/demo/e2e -v
```

## 6. Import mechanics change

`demo/` gains an `__init__.py` (currently absent) so the two new
subpackages are real importable packages
(`demo._playwright_demo_script`, `demo._professional_video_demo`)
instead of relying on the original scripts' manual
`sys.path.insert(0, str(DEMO_DIR))` trick. `run_demo_sequence.py`'s
`_load_prompts` is imported as `from demo.run_demo_sequence import
_load_prompts` from the new packages. This is the one structural change
outside the two named files, and is the minimum needed to make `demo/`
a normal package — flagged here explicitly rather than silently
expanding scope.

## 7. End-to-end run

After implementation: run the full mocked-coverage suite (must be
100%/green), then run the real-browser e2e smoke suite once for each
package (confirms the actual refactor still produces a real `.webm` +
screenshots, same as the last verified manual run recorded in repo
memory), then run the existing full engineering_studio suite
unchanged (`ruff`, `mypy`, `pytest --cov=engineering_studio`) to
confirm zero regressions elsewhere.

## 8. Documentation

- `report.md` → `engineering-studio-ai/reports/DEMO_REFACTOR_REPORT.md`
  (this repo's existing `reports/` convention — currently holds
  coverage/junit artifacts; this adds the first narrative report).
- `chat.md` → both:
  - `engineering-studio-ai/CHATS/CHAT_2026-07-21_demo-scripts-refactor.md`
    (this repo's own session-archive convention).
  - `CodingStandardsRef/markdowns/chats/CHAT_2026-07-21_demo-scripts-refactor.md`
    (parent repo's convention, per `markdowns/README.md` §4).
- Update `demo/README.md`'s file table (old rows removed/pointed at
  `_archive/`, two new package rows added) and repo-memory file
  `vision-docs-conventions.md` gets one new dated bullet at the end
  (append-only, per existing pattern).

## 9. Assumptions / Open Risks (flag, do not silently resolve)

- `demo/__init__.py` addition (Section 6) is a small scope expansion
  beyond "the two files" — confirmed necessary for clean package
  imports; will call it out again at implementation time.
- 100% coverage is scoped to the two new demo packages only, not to
  `demo/run_demo_sequence.py` or `demo/demo_prompts.json` handling
  (out of scope, unchanged).
- Real-browser e2e test requires Chromium already installed
  (`playwright install chromium`) in this environment; if missing, the
  e2e test will be skipped with a clear reason rather than failing the
  whole run.
