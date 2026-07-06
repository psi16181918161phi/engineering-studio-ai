---
title: "Grounding-Drift Guardrail"
author: "Hadrian Hu"
date: "2026-07-06"
version: "0.1.0"
keywords: ["guardrail", "grounding", "hallucination"]
status: "Active"
---

# Grounding-Drift Guardrail

Requires: `../STANDARDS_SUMMARY.md`. Condensed from
`prompts/agents/mdap/mdap-guardrail-grounding-drift.agent.md`.

## Rule

Every assertion an agent makes must be traceable to an input artifact, a
cited external source, or explicit deductive necessity. If uncertain: state
uncertainty or offer the assumption separately — never guess silently
(mirrors `AGENTS.md` §5 grounding rule, restated here as an always-on check
rather than a one-time role).

## Applies To

Every agent in this roster, every response, not a dispatched pipeline
stage — this is a standing check any Reviewer/Validator/Challenge agent can
invoke.

## Output Format

```json
{"guard": "Grounding-Drift", "flagged_claims": ["..."], "confidence": 0.0-1.0, "requires_human_review": true|false}
```

## Changelog

| Version | Date       | Author     | Description        |
| :------ | :--------- | :--------- | :-------------------|
| 0.1.0   | 2026-07-06 | Hadrian Hu | Initial creation, condensed from `mdap-guardrail-grounding-drift.agent.md`. |
