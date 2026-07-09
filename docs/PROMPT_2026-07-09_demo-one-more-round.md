---
title: "PROMPT — one more round for engineering-studio-ai prototype demo"
author: "GitHub Copilot (agent session)"
date: "2026-07-09"
version: "2026.1.0.0"
status: "Ready"
confidentiality: "INTERNAL"
---

# PROMPT — One More Round (Demo-Focused)

Use this prompt in the next coding round to execute the highest-value
demo-readiness tasks grounded in current repo state.

## Prompt Text

You are continuing work in `engineering-studio-ai`.

Current verified baseline:

- CI-critical gates are green (lint, strict mypy, bandit, pip-audit).
- `pytest tests` passes at 100% coverage.
- E2E is green (`reports/e2e-junit.xml` shows 17 tests, 0 failures, 0 errors).
- Remaining gaps are demo/presentation readiness and one deprecation warning
  observed in test output.

Execute this round with strict scope control and no hallucinations:

1. Fill the fallback section in `demo/demo-script.md` with an explicit,
   truthful failure-mode flow for live-rate-limit/network disruption.
2. Fill all `[SECTION INCOMPLETE` placeholders in
   `presentation/slides-outline.md` using claims grounded in existing repo
   artifacts.
3. Add deterministic demo orchestration:
   - `demo/demo_prompts.json` with confirmed software-first prompts.
   - `demo/run_demo_sequence.py` to run or stage prompts in fixed order and
     print/save run metadata.
4. Add a pre-demo validation script/command that runs:
   `ruff`, `mypy`, `bandit`, `pip-audit`, `pytest tests`, `pytest tests/e2e`.
5. Investigate and, if safe this round, fix the current Starlette/FastAPI
   deprecation warning path in tests; otherwise add a narrow documented filter.
6. Re-run full regression after edits and report exact pass/fail evidence.
7. Write a dated chat archive under `markdowns/chats/` describing what changed,
   what was deferred, and why.

Constraints:

- Do not fabricate demo output.
- Keep the locked palette conventions intact (`#FFAEC9`, `#000000`, `#B76E79`).
- Do not push to remote unless explicitly asked.
- Prefer minimal, focused changes over broad refactors.

Definition of done for this round:

- `demo/demo-script.md` and `presentation/slides-outline.md` have no
  incomplete placeholders.
- Deterministic demo prompt flow exists as code/data.
- One-command pre-demo regression exists and is runnable.
- Post-change regressions are green, with evidence captured.
