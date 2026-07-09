---
title: "CONTRIBUTION Guide — Engineering Studio AI"
author: "Hadrian Hu"
date: "2026-07-07"
version: "0.1.0"
keywords: ["contributing", "git", "onboarding", "merge-conflicts", "workflow", "hackathon"]
---
# CONTRIBUTION Guide — Engineering Studio AI

> AMD LabLabAI Hackathon submission, built by a small team in parallel
> over a few days. Read this guide, [SCAFFOLDING.md](SCAFFOLDING.md)
> (ownership zones), and [AGENTS.md](AGENTS.md) (condensed standards)
> before opening your first PR.

---

## Table of Contents

- [1. Onboarding — First-Time Setup](#1-onboarding--first-time-setup)
- [2. Branch Naming](#2-branch-naming)
- [3. Commit Messages](#3-commit-messages)
- [4. Pull Request Process](#4-pull-request-process)
- [5. Before You Touch a Shared File](#5-before-you-touch-a-shared-file)
- [6. When Merges Get Messy](#6-when-merges-get-messy)
- [7. Local Quality Gate](#7-local-quality-gate)
- [8. Key References](#8-key-references)
- [Changelog](#changelog)

---

## 1. Onboarding — First-Time Setup

| Requirement                       | Minimum Version |
| :-------------------------------- | :-------------- |
| Git                               | 2.30            |
| Python                            | 3.14.4 x64      |
| PowerShell (Windows contributors) | 5.1+            |

```powershell
git clone https://github.com/psi16181918161phi/engineering-studio-ai.git
cd engineering-studio-ai
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[gui]"
pip install -r requirements-dev.txt
Copy-Item .env.example .env   # fill in FIREWORKS_API_KEY, never commit it
```

---

## 2. Branch Naming

Follows `docs/RESPONSIBILITIES.md`'s `main` → `develop` → `feature/<name>`
strategy:

| Type         | Example                       | Merges Into |
| :----------- | :---------------------------- | :---------- |
| `feature/` | `feature/research-role2`    | `develop` |
| `fix/`     | `fix/sse-keepalive-timeout` | `develop` |
| `chore/`   | `chore/update-deps`         | `develop` |

Do not commit directly to `main`. `develop` (if used) or a `feature/*`
branch off `main` is always the starting point.

---

## 3. Commit Messages

Keep commits **small and descriptive**. Prefer a Conventional-Commits-style
prefix (`feat:`, `fix:`, `docs:`, `chore:`, `merge:`, `build:`) even though
this repo does not enforce it via a commit hook — it makes `git log --oneline` scannable when six people are committing in parallel.

---

## 4. Pull Request Process

1. Confirm your change is entirely inside your ownership zone per
   [SCAFFOLDING.md §2](SCAFFOLDING.md#2-ownership-zones-merge-conflict-avoidance),
   or that you followed the shared-file protocol in
   [SCAFFOLDING.md §4](SCAFFOLDING.md#4-shared-file-coordination-protocol).
2. Run the [local quality gate](#7-local-quality-gate) before opening the
   PR — CI runs the same checks and will block on failure.
3. Keep PRs small and frequent rather than one large end-of-day dump —
   this is the single biggest lever against the merge pain described in
   [§6](#6-when-merges-get-messy).
4. At least one other teammate reviews before merging to `main`/`develop`.
5. Squash-or-keep history is a project-lead call at merge time; either
   way, the merge commit message should say **what** was reconciled, not
   just "merge branch X".

---

## 5. Before You Touch a Shared File

Only a handful of files are genuinely shared across roles
(`pyproject.toml`, `requirements*.txt`, root `README.md`/`AGENTS.md`/
`SCAFFOLDING.md`, `docs/task-specs.md`, `docs/TEAM_QA.md`, `.github/workflows/ci.yml`).
Before editing one:

- Check `git log --oneline main..origin/main` (or `HEAD..origin/main`)
  for recent teammate changes to that file — don't rely on discovering
  this only when you open a PR.
- Add your section/dependency/row without reformatting someone else's.
- If you're about to build something that could plausibly overlap with
  another role's in-flight work (e.g. a new web surface, a new CLI
  entry point), say so in the team channel **before** you build it, not
  after. See [COMMUNITY.md](COMMUNITY.md) for why this matters.

---

## 6. When Merges Get Messy

Two teammates have, in practice, independently built entire overlapping
subsystems (two different web architectures, same repo, same week)
without either knowing about the other's work until merge time. It
happens even with an ownership-zone table. When it does:
**[COMMUNITY.md § Merge Conflict Resolution Playbook](COMMUNITY.md#merge-conflict-resolution-playbook)**
is the step-by-step recovery process — read it before you start resolving
conflicts by hand.

---

## 7. Local Quality Gate

Run the same checks CI runs, before opening a PR:

```powershell
python -m pytest tests -q --cov=engineering_studio --cov-report=term-missing
python -m ruff check .
python -m mypy src
python -m bandit -r src -ll
python -m pip_audit
```

All five must be clean (100% coverage, `ruff`/`mypy --strict`/`bandit -ll`
all pass, no known CVEs) before merging to `main`.

---

## 8. Key References

| Topic                                            | Source                                  |
| :----------------------------------------------- | :-------------------------------------- |
| Team roles & Definition of Done                  | `docs/RESPONSIBILITIES.md`            |
| Ownership zones / merge-conflict avoidance       | `SCAFFOLDING.md`                      |
| Condensed engineering standards                  | `AGENTS.md`                           |
| Extended standards (JPL, ARIA, testing taxonomy) | `.github/agents/STANDARDS_SUMMARY.md` |
| Security policy                                  | `SECURITY.md`                         |
| Community norms & merge-conflict playbook        | `COMMUNITY.md`                        |

---

## Changelog

| Version    | Date       | Author     | Description                 |
| :--------- | :--------- | :--------- | :-------------------------- |
| 2026.0.1.0 | 2026-07-07 | Hadrian Hu | Initial CONTRIBUTION guide. |
