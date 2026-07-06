---
title: "Token-Efficiency Guardrail"
author: "Hadrian Hu"
date: "2026-07-06"
version: "0.1.0"
keywords: ["guardrail", "token-efficiency", "signal-density"]
status: "Active"
---

# Token-Efficiency Guardrail

Requires: `../STANDARDS_SUMMARY.md`. Condensed from
`prompts/agents/mdap/mdap-guardrail-token-efficiency.agent.md`.

## Rule

Prefer diffs/structured JSON outputs over prose; batch independent tool
calls; do not restate the whole Task Specification back in the response
(mirrors `AGENTS.md` §5). Never trim a required, grounded assertion purely
to save tokens.

## Applies To

Every agent's response format — each `.agent.md` file's "Output Format"
JSON block exists specifically to keep responses compact and machine-
parseable for the next agent in the pipeline.

## Output Format

```json
{"guard": "Token-Efficiency", "flagged_verbosity": ["..."], "confidence": 0.0-1.0, "requires_human_review": true|false}
```

## Changelog

| Version | Date       | Author     | Description        |
| :------ | :--------- | :--------- | :-------------------|
| 0.1.0   | 2026-07-06 | Hadrian Hu | Initial creation, condensed from `mdap-guardrail-token-efficiency.agent.md`. |
