# Demo Script — Engineering Studio AI

WHAT: Beat-by-beat live demo narration mapped to the pipeline's Demo Flow.
WHY: Keeps the live demo tight and rehearsed rather than improvised under
time pressure — every beat has an owner and an expected on-screen result.
HOW: One row per beat, in execution order. Update the "On-Screen Action"
column as Role 5's UI takes shape.

| # | Narration Beat | On-Screen Action | Owner |
|---|---|---|---|
| 1 | "Type one product brief — e.g. 'Design a warehouse robot'." | User types the brief into the CLI/UI. | Role 5 |
| 2 | Orchestrator decomposes the brief into parallel sub-tasks. | Show `plan.md` / task list output. | Role 5 |
| 3 | Research agent frames the problem. | Show `research/research-findings.md`-style output artifact. | Role 5 |
| 4 | Mechanical/Electrical/Firmware/Simulation/Cost specialists run in parallel. | Show each `artifacts/<discipline>/output.md` populating live. | Role 5 |
| 5 | Challenge Division adversarially reviews the result. | Show objections/findings summary. | Role 5 |
| 6 | Quality Gate renders a verdict. | Show pass/fail + confidence/evidence declaration. | Role 5 |
| 7 | Final package export. | Show the compiled BOM/wiring/firmware/sim/cost/docs bundle. | Role 5 |

## Fallback plan

[SECTION INCOMPLETE — REQUIRES HUMAN INPUT] — document what to show if a
live Fireworks AI call fails/rate-limits during the actual presentation
(per `../AGENTS.md` §5 "live-data honesty": never fake a result — have a
pre-recorded fallback run ready instead).
