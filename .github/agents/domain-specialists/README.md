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
| `mechanical-engineering-specialist.agent.md` | Mechanism/structure/thermal/fluid design (umbrella; see `mechanical/`) |
| `electrical-electronics-engineering-specialist.agent.md` | Circuits, power, sensors/actuators, wiring (umbrella; see `electrical/`, `electronics/`) |
| `firmware-specialist.agent.md` | Firmware/embedded-software architecture (umbrella; see `firmware/`) |
| `simulation-specialist.agent.md` | Simulation environment/config |
| `systems-engineering-specialist.agent.md` | Cross-discipline integration, firmware/robotics interfaces, simulation config (umbrella; see `systems/`) |

### Fine-grained per-discipline splits (`OPEN_AI_DEV_WEEK_HACKATHON/PLAN.md` Phase 7)

Each umbrella flat file above keeps its broad role description; the
subfolder below narrows it into one or more concrete, independently
dispatchable micro-specialists — increasing the number of distinct,
individually-testable model calls a single demo run can show.

| Folder | Files | Splits from |
| :--- | :--- | :--- |
| `electrical/` | `power-budget-specialist.agent.md`, `wiring-harness-specialist.agent.md` | `electrical-electronics-engineering-specialist.agent.md` |
| `electronics/` | `component-selection-bom-specialist.agent.md`, `pcb-footprint-note-specialist.agent.md` | `electrical-electronics-engineering-specialist.agent.md` |
| `firmware/` | `rtos-task-skeleton-specialist.agent.md`, `sensor-driver-stub-specialist.agent.md` | `firmware-specialist.agent.md` |
| `mechanical/` | `structural-frame-specialist.agent.md`, `tolerance-stackup-specialist.agent.md` | `mechanical-engineering-specialist.agent.md` |
| `systems/` | `integration-cross-domain-specialist.agent.md` | `systems-engineering-specialist.agent.md` |
| `software/` | `api-contract-specialist.agent.md`, `sdk-surface-specialist.agent.md` | Net-new (supports `PLAN.md` Phase 4) |
| `hardware/` | `enclosure-thermal-specialist.agent.md` | Net-new (previously ungrounded owner) |
| `middleware/` | `inter-service-message-contract-specialist.agent.md` | Net-new (ties to `runs.py` pub/sub) |
| `scripting/` | `build-automation-script-specialist.agent.md` | Net-new (adjacent to `../scaffolding/`) |

Condensed from `prompts/agents/mdap/domain-specialists-industry/engineering/`
and `OPEN_AI_DEV_WEEK_HACKATHON/INVESTIGATE.md` §3.1
— no verbatim standards text reproduced (public-repo policy, see repo memory
`latex-conventions.md`/`vision-docs-conventions.md` precedent).

## Changelog

| Version | Date       | Author     | Description             |
| :------ | :--------- | :--------- | :------------------------ |
| 0.1.0   | 2026-07-06 | Hadrian Hu | Initial creation. |
| 0.2.0   | 2026-07-18 | Hadrian Hu | Added 9 fine-grained per-discipline split subfolders (`OPEN_AI_DEV_WEEK_HACKATHON/PLAN.md` Phase 7) and listed the previously-missing `firmware-specialist.agent.md`/`simulation-specialist.agent.md` rows. |
