---
title: "Domain Specialists — README"
author: "Hadrian Hu"
date: "2026-07-06"
version: "0.1.0"
keywords: ["domain-specialist", "mechanical", "electrical", "systems-engineering"]
status: "Active"
---

# Domain Specialists

Engineering-discipline agents that produce the actual technical artifacts
(BOM lines, wiring/architecture notes, mechanism sketches, simulation
configs) for one product-brief demo run. Each writes ONLY to its own
artifact folder (SCOPE, `AGENTS.md` §3); never edits another specialist's
output.

| File | Discipline |
| :--- | :--- |
| `mechanical-engineering-specialist.agent.md` | Mechanism/structure/thermal/fluid design |
| `electrical-electronics-engineering-specialist.agent.md` | Circuits, power, sensors/actuators, wiring |
| `systems-engineering-specialist.agent.md` | Cross-discipline integration, firmware/robotics interfaces, simulation config |

Condensed from `prompts/agents/mdap/domain-specialists-industry/engineering/`
— no verbatim standards text reproduced (public-repo policy, see repo memory
`latex-conventions.md`/`vision-docs-conventions.md` precedent).

## Changelog

| Version | Date       | Author     | Description             |
| :------ | :--------- | :--------- | :------------------------ |
| 0.1.0   | 2026-07-06 | Hadrian Hu | Initial creation. |
