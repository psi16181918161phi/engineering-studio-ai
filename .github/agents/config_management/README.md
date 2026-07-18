---
title: "Config Management — README"
author: "Hadrian Hu"
date: "2026-07-18"
version: "0.1.0"
keywords: ["config-management", "openai", "model-routing", "env-vars"]
status: "Active"
---

# Config Management

Owns the schema and validation of environment-driven configuration for
model-provider routing (`FIREWORKS_*` today, `OPENAI_*` added for the
OpenAI Hackathon pivot) and `.env.example` itself. Never edits code —
`src/engineering_studio/sdk/`, `api/`, `cli/`, `gui/` own the actual
provider-swap implementation (`OPEN_AI_DEV_WEEK_HACKATHON/PLAN.md` Phase 4).

| File | Scope |
| :--- | :--- |
| `openai-config-specialist.agent.md` | `OPENAI_API_KEY`/`OPENAI_BASE_URL`/`OPENAI_MODEL_*` env-var contract |

Condensed from `OPEN_AI_DEV_WEEK_HACKATHON/INVESTIGATE.md` §3.3 — see that
file for the full grounding trail. No verbatim standards text reproduced.

## Changelog

| Version | Date       | Author     | Description        |
| :------ | :--------- | :--------- | :------------------- |
| 0.1.0   | 2026-07-18 | Hadrian Hu | Initial creation. |
