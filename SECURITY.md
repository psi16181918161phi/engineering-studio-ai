---
title: "Security Policy — Engineering Studio AI"
author: "Hadrian Hu"
date: "2026-07-07"
version: "0.1.0"
keywords: ["security", "vulnerability-disclosure", "secrets", "hackathon"]
---
# Security Policy — Engineering Studio AI

**Governing standards:** `AGENTS.md §8` (condensed security baseline) and
`.github/agents/STANDARDS_SUMMARY.md` (extended coverage). This repo is a
public spin-off of a private standards corpus — see `AGENTS.md`'s intro
for why the full corpus is not reproduced here.

---

## Supported Versions

This is a short-lived hackathon submission (AMD LabLabAI, Act II —
Unicorn Track), not a long-term maintained product. There is a single
active line of development:

| Component | Supported | Notes |
| :--------- | :--------: | :----- |
| `main` branch (current release) | ✅ Yes | Active during and shortly after the hackathon |
| Any tagged/archived snapshot | ❌ No | Point-in-time submission artifact only |

---

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

1. Open a [private security advisory](https://github.com/psi16181918161phi/engineering-studio-ai/security/advisories/new)
   on GitHub, or contact a maintainer directly if advisories are
   unavailable.
2. Include: affected file(s), a description of the vulnerability (CWE
   reference if known), reproduction steps, and potential impact.

---

## Response

Given the hackathon timeline, response is **best-effort**, not SLA-backed:

| Milestone | Target |
| :--------- | :------ |
| Acknowledgement | 3–5 calendar days |
| Fix or mitigation | As soon as practical; critical findings prioritized immediately |

---

## Scope

**In scope:**

- `src/engineering_studio/` — API/SSE routes (`api/`), the FastAPI app
  (`webapp/`), CLI (`cli/`), SDK (`sdk/`), orchestrator/agents
  (`agents/`) — injection, path traversal, insecure file handling,
  secrets handling.
- `frontend/` — served static assets, CORS configuration.
- `.github/workflows/ci.yml` — secrets leakage, supply-chain risk.
- Dependency set in `pyproject.toml`/`requirements*.txt` (tracked via
  `pip-audit` in CI).

**Out of scope:**

- Denial of service against local dev tooling.
- Findings in `research/`, `docs/`, `paper/`, `presentation/` (no code
  execution).
- The Fireworks AI hosted models themselves (report to Fireworks AI,
  not here).

---

## Secrets Handling

- `FIREWORKS_API_KEY` and any other credential live only in a local
  `.env` (gitignored) — never in `.env.example`, source, tests, or
  fixtures.
- If a secret is ever accidentally committed: rotate it immediately at
  the provider, then open a private security advisory — do not rely on
  `git rm`/history rewrite alone, since the key must be treated as
  compromised the moment it was pushed.

---

## Security Standards Reference

- `AGENTS.md §8` — no secrets in source, input validation/sanitization
  before prompt interpolation, pinned dependencies, `pip-audit` before
  submission commits.
- `.github/agents/STANDARDS_SUMMARY.md` — extended coverage (OWASP-
  aligned baseline, CI security gates).
- Local quality gate (`ruff`, `mypy --strict`, `bandit -ll`, `pip-audit`)
  — see [CONTRIBUTION.md §7](CONTRIBUTION.md#7-local-quality-gate); all
  four run in `.github/workflows/ci.yml`.

---

## Changelog

| Version | Date       | Author     | Description            |
| :------ | :--------- | :--------- | :---------------------- |
| 0.1.0   | 2026-07-07 | Hadrian Hu | Initial security policy. |
