---
title: "Community Guide — Engineering Studio AI"
author: "Hadrian Hu"
date: "2026-07-07"
version: "0.1.0"
keywords: ["community", "merge-conflicts", "collaboration", "hackathon", "communication"]
---
# Community Guide — Engineering Studio AI

> How this small hackathon team talks to each other, avoids stepping on
> each other's work, and — when it happens anyway — recovers cleanly
> from two people building the same thing twice.

---

## Table of Contents

- [1. Getting Help](#1-getting-help)
- [2. Team Roles](#2-team-roles)
- [3. Communication Norms](#3-communication-norms)
- [4. Merge Conflict Resolution Playbook](#4-merge-conflict-resolution-playbook)
- [5. Prevention: Ownership Zones](#5-prevention-ownership-zones)
- [6. Code of Conduct (Short Form)](#6-code-of-conduct-short-form)
- [Changelog](#changelog)

---

## 1. Getting Help

- **[GitHub Issues](https://github.com/psi16181918161phi/engineering-studio-ai/issues)**
  — bugs, tracked follow-ups.
- **[GitHub Discussions](https://github.com/psi16181918161phi/engineering-studio-ai/discussions)**
  (if enabled) — questions, architecture proposals, "is anyone already
  building X?" checks.
- Security issues go through [SECURITY.md](SECURITY.md), never a public
  issue.

---

## 2. Team Roles

See `docs/RESPONSIBILITIES.md` for the full six-role breakdown (Project
Architect/Lead, Research, Backend/Pipeline, QA/Security/DevOps, Frontend,
Docs/Paper). Role 1 (Lead) is the tie-breaker for any shared-file
disagreement or architecture-decision deadlock.

---

## 3. Communication Norms

1. **Announce before you build, not after.** If you're about to start
   work that could plausibly overlap with another role's territory (a
   new web surface, a new CLI entry point, a new orchestrator lifecycle
   contract), say so first. This single norm would have prevented the
   incident described in [§4](#4-merge-conflict-resolution-playbook).
2. **Evening integration cadence.** Per `docs/RESPONSIBILITIES.md`,
   merge to `develop`/`main` regularly (small PRs) rather than holding a
   large branch open for days — the longer two branches diverge on the
   same subsystem, the worse the eventual reconciliation.
3. **Periodically diff against upstream**, even mid-task:
   ```powershell
   git fetch origin
   git log --oneline HEAD..origin/main
   git diff HEAD..origin/main --stat
   ```
   Don't wait until you're ready to open your own PR to discover what
   changed underneath you.

---

## 4. Merge Conflict Resolution Playbook

This is not theoretical: two teammates independently built two complete,
architecturally incompatible web surfaces (one synchronous SDK-based
FastAPI+Jinja2 app, one async SSE + vanilla-JS dashboard) in the same
repo, in the same week, each unaware of the other's work, and both
merged cleanly into their own branches before the conflict surfaced. If
this happens to you, follow these steps in order.

### Step 0 — Stop and surface it, don't silently pick a side

The moment you discover overlapping/incompatible work (not just a
textual conflict, but two different *approaches* to the same problem),
treat it as a team decision, not a merge-tool decision. Bring it to
whoever owns the affected zone (see [§5](#5-prevention-ownership-zones))
and agree explicitly on which version becomes canonical before writing
any resolution code. Don't guess which one "should" win.

### Step 1 — Inspect before committing

```powershell
git fetch origin
git merge origin/main --no-commit --no-ff
git status
```

`--no-commit --no-ff` lets you see every conflicted and auto-merged file
before anything is finalized. Review the **auto-merged** file list too,
not just the conflicted ones — see Step 2.

### Step 2 — Auto-merge is not enough when retiring a whole approach

`git checkout --theirs` and clean auto-merges only resolve *textual*
overlaps. A file that only **your** branch ever touched (e.g. a route
module the other architecture doesn't use) will never show as
conflicted — git has no way to know it should be deleted or rewritten.
After the merge, explicitly grep for and remove any now-dead code from
the retired approach; don't assume "no conflict markers" means "fully
reconciled."

### Step 3 — Grep for stale references

If the resolution removes an optional-dependency extra, a route, a CLI
flag, or a config key, grep the whole repo for its old name:

```powershell
Select-String -Path "**/*.yml","**/*.md","**/*.toml" -Pattern "old-extra-name" -Recurse
```

`ci.yml`, docs, and READMEs are the most common places a stale reference
survives a code-level cleanup.

### Step 4 — Re-run the full local quality gate, not just "no conflicts"

```powershell
python -m pytest tests -q --cov=engineering_studio --cov-report=term-missing
python -m ruff check .
python -m mypy src
python -m bandit -r src -ll
python -m pip_audit
```

Coverage gaps hide in "same-line-area, different-branch" spots — e.g. an
existing test hitting a function's early-return branch doesn't prove the
rest of the function body is covered after a merge changed what feeds
into it. Trust the coverage percentage, not a visual conflict-marker
scan.

### Step 5 — Reconcile stashed/WIP docs, don't pop-and-leave

If you stashed in-progress doc edits before starting the merge, popping
the stash is not the end of the job — if that doc references anything
from the now-retired architecture (function names, module paths, UI
flow descriptions), update every stale reference. A doc that describes a
retired approach is actively misleading, worse than no doc at all.

### Step 6 — Commit and communicate

- Commit message prefix `merge:` + a description of **what** was
  reconciled and **why** a particular side was chosen (not just "merge
  branch X into Y").
- Push only after Step 4 is fully green.
- Post a short summary in the team channel: what conflicted, what was
  chosen as canonical, and what changed for anyone who had that old
  architecture checked out locally.

---

## 5. Prevention: Ownership Zones

The best fix for merge pain is not resolving it well — it's reducing how
often it happens. [SCAFFOLDING.md §2](SCAFFOLDING.md#2-ownership-zones-merge-conflict-avoidance)
defines which paths each role owns by default and which few files are
genuinely shared. Read it before starting any new subsystem, and follow
[SCAFFOLDING.md §4](SCAFFOLDING.md#4-shared-file-coordination-protocol)
for the shared-file coordination rules.

---

## 6. Code of Conduct (Short Form)

This is a small hackathon team, not a large open-source project — no
separate `CODE_OF_CONDUCT.md` is maintained. The expectation is simple:
be direct about disagreements, assume good faith when you find
overlapping work (see [§4](#4-merge-conflict-resolution-playbook)), and
raise architecture concerns to Role 1 (Lead) rather than resolving a
cross-team disagreement unilaterally in a merge commit.

---

## Changelog

| Version | Date       | Author     | Description                                        |
| :------ | :--------- | :--------- | :--------------------------------------------------- |
| 0.1.0   | 2026-07-07 | Hadrian Hu | Initial community guide, incl. merge-conflict playbook grounded in the SSE-vs-Jinja2 web-surface incident. |
