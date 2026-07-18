---
title: "Testing — README"
author: "Hadrian Hu"
date: "2026-07-18"
version: "0.1.0"
keywords: ["testing", "unit", "integration", "contract", "e2e"]
status: "Active"
---

# Testing (per-tier split)

Narrower per-tier successors to `../testing.agent.md`, which remains the
umbrella overview and cross-links here rather than being rewritten
wholesale.

| File | Tier |
| :--- | :--- |
| `unit-testing-specialist.agent.md` | Single function/class boundary |
| `integration-testing-specialist.agent.md` | 2+ module boundaries, mocked `ModelClient` |
| `contract-testing-specialist.agent.md` | `ModelClient` provider-contract stability (Fireworks/OpenAI) |
| `e2e-testing-specialist.agent.md` | Playwright, screenshots/video |

Condensed from `OPEN_AI_DEV_WEEK_HACKATHON/INVESTIGATE.md` §3.5.

## Changelog

| Version | Date       | Author     | Description        |
| :------ | :--------- | :--------- | :------------------- |
| 0.1.0   | 2026-07-18 | Hadrian Hu | Initial creation. |
