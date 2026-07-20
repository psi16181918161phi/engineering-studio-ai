---
title: "Virtual Env — README"
author: "Hadrian Hu"
date: "2026-07-18"
version: "0.1.0"
keywords: ["virtual-env", "venv", "pyproject-toml", "uv", "setup-py", "polyglot"]
status: "Active"
---

# Virtual Env

Owns Python (and, contingently, non-Python) isolated-environment and
dependency-manifest hygiene: which venv exists, what it's named, which
packaging file (`pyproject.toml` / legacy `setup.py` / `uv.lock`) is
authoritative, and — forward-looking only — the equivalent concerns for
other languages this workspace might one day add.

| File | Scope |
| :--- | :--- |
| `custom-venv-naming-specialist.agent.md` | Discovery + `.gitignore` coverage for non-`.venv`-named venvs (e.g. `venv_cve_scan/`) |
| `pyproject-toml-specialist.agent.md` | PEP 621 `[project]` / `[build-system]` / `[tool.*]` schema correctness |
| `uv-workflow-specialist.agent.md` | Optional `uv` adoption guidance — not currently adopted by this repo |
| `setup-py-legacy-specialist.agent.md` | Legacy `setup.py` detection + safe migration path (this repo has none today) |
| `polyglot-environment-specialist.agent.md` | Node/Rust/Go/.NET/Java manifest conventions — contingency role, none present today |

## Why this folder exists

`../STANDARDS_SUMMARY.md` §8 documents this repo's single canonical
`.venv`. The wider workspace this repo lives in routinely uses several
differently-named, purpose-scoped virtual environments at once (see
`custom-venv-naming-specialist.agent.md`'s real, currently-observed
examples) — a single "the venv is always called `.venv`" assumption does
not hold workspace-wide. This folder's roster exists so that assumption is
never silently made by tooling or a reviewing agent.

## Relationship to `../scaffolding/`

`../scaffolding/python-scaffolding-micro-specialist.agent.md` owns new
module/package layout (`src/engineering_studio/<domain>/` + matching
`tests/`). This folder owns the environment/packaging-manifest layer
underneath that — the two are complementary, not overlapping; a
scaffolding request that also needs a new isolated venv or a
`pyproject.toml` edit should hand off here rather than duplicating this
folder's scope.

Condensed from this repo's own ground-truth files (`pyproject.toml`,
`.gitignore`, `frontend/`) and `OPEN_AI_DEV_WEEK_HACKATHON/PREPLAN.md` §2's
non-goal discipline for ungrounded-owner roles — no verbatim standards
text reproduced.

## Changelog

| Version | Date       | Author     | Description                                                             |
| :------ | :--------- | :--------- | :---------------------------------------------------------------------------|
| 0.1.0   | 2026-07-18 | Hadrian Hu | Initial creation — fills the previously-empty `virtual_env/` roster folder with 5 files. |
