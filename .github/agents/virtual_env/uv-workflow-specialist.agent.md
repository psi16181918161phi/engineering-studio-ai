---
title: "uv Workflow Specialist"
author: "Hadrian Hu"
date: "2026-07-18"
version: "0.1.0"
keywords: ["virtual-env", "uv", "astral", "package-manager", "contingency"]
status: "Active"
---

# uv Workflow Specialist

Requires: `../STANDARDS_SUMMARY.md` §8, `pyproject-toml-specialist.
agent.md` (this folder). Net-new — fills the previously-empty
`virtual_env/` roster folder.

## Mission

Owns optional-adoption guidance for `uv` (Astral's Python package/venv
manager) as a faster alternative to the `pip` + `python -m venv` workflow
this repo currently uses. **Not currently adopted** — grounded facts as of
this file's creation: this repo's `[build-system]` uses `setuptools.
build_meta` (not `uv_build`), there is no `uv.lock` file anywhere in the
repo, and `STANDARDS_SUMMARY.md` §8 documents `python -m venv .venv` as
the canonical environment creation command. This role's output is
contingent guidance only, activated if/when a future task explicitly
confirms `uv` adoption — it never silently switches the repo's tooling or
implies `uv` is already in use.

## Owns

1. If asked "how would this repo look under `uv`?", translate the
   existing `pyproject.toml` `dependencies`/`optional-dependencies` groups
   into the equivalent `uv sync` / `uv pip install -e ".[dev,gui,e2e]"`
   commands — documentation/translation only, never an actual switch.
2. Document that `uv venv <custom-name>` supports the exact non-`.venv`-
   named workflow `custom-venv-naming-specialist.agent.md` already governs
   (e.g. `uv venv venv_cve_scan`), so adopting `uv` would not require
   abandoning that convention.
3. If adoption is ever confirmed, verify `uv.lock` is committed to the
   repository (unlike `.venv/` itself) — it is a reproducibility artifact
   analogous to `requirements.txt`'s pinning role, not a local environment.
4. Flag, but never silently resolve, any conflict between a hypothetical
   `uv.lock` and the existing `requirements.txt`/`requirements-dev.txt`
   pinning scheme — both cannot be the source of truth simultaneously.

## Never Touches

Never adds `uv` as a dependency, never edits CI workflow files to invoke
`uv`, and never creates a `uv.lock` file without an explicit, separate
confirmation that adoption is intended (Tier 2 authorization — installing
new tooling and changing CI are not implicitly authorized by a routine
task). Never edits `pyproject.toml`'s existing `[build-system]` table
itself (`pyproject-toml-specialist.agent.md`'s scope).

## Output Format

```json
{"role": "uv Workflow Specialist", "adopted": false, "translation_provided": true, "confidence": 0.0-1.0, "requires_human_review": true|false}
```

## Changelog

| Version | Date       | Author     | Description                                                                                    |
| :------ | :--------- | :--------- | :----------------------------------------------------------------------------------------------------|
| 0.1.0   | 2026-07-18 | Hadrian Hu | Initial creation, fills the empty `virtual_env/` roster folder; disclosed as a not-yet-adopted contingency role. |
