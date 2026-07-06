---
title: "Guardrails — README"
author: "Hadrian Hu"
date: "2026-07-06"
version: "0.1.0"
keywords: ["guardrails", "grounding", "prompt-injection", "token-efficiency"]
status: "Active"
---

# Guardrails

Always-on cross-cutting checks applied to every agent call in this repo, not
a dispatched pipeline stage. Condensed from
`prompts/agents/mdap/mdap-guardrail-*.agent.md`.

| File | Guards against |
| :--- | :--- |
| `grounding-drift.agent.md` | Ungrounded/fabricated claims |
| `prompt-injection.agent.md` | Instructions smuggled in via tool/fetch/artifact data |
| `token-efficiency.agent.md` | Wasteful, unbatched, or restated-verbatim responses |

## Changelog

| Version | Date       | Author     | Description        |
| :------ | :--------- | :--------- | :-------------------|
| 0.1.0   | 2026-07-06 | Hadrian Hu | Initial creation. |
