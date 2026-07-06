---
title: "Challenge Division — README"
author: "Hadrian Hu"
date: "2026-07-06"
version: "0.1.0"
keywords: ["challenge-division", "adversarial-review", "security", "safety"]
status: "Active"
---

# Challenge Division

Independent adversarial reviewers — run in parallel with the Reviewer, never
implement, never approve their own work. Each stance is distinct; the
Validator/Quality Gate reconcile conflicting findings, not the Challenge
agents themselves. Condensed from
`prompts/agents/mdap/challenge-division/`.

| File | Adversarial stance |
| :--- | :--- |
| `security.agent.md` | "How would this be attacked/exfiltrated/injected?" |
| `failure-analysis.agent.md` | "How does this fail, and how visibly?" |
| `safety.agent.md` | "Who/what gets physically hurt if this is wrong?" |
| `red-team.agent.md` | "Assume a hostile actor controls an input — what happens?" |
| `paranoid-devils-advocate.agent.md` | "What is everyone assuming that might be false?" |
| `cost-sustainability.agent.md` | "Is this affordable/sustainable at scale, not just in the demo?" |
| `project-prosecutor.agent.md` | "Argue the strongest case this project should NOT ship as-is." |

## Changelog

| Version | Date       | Author     | Description        |
| :------ | :--------- | :--------- | :-------------------|
| 0.1.0   | 2026-07-06 | Hadrian Hu | Initial creation. |
