# Task Specifications — Engineering Studio AI Pipeline

WHAT: Filled Task Specification blocks for each pipeline stage, adapted
from the private catalog's `mdap-14-amd-lablab-hackathon-task-specs.md`.
WHY: `engineering_studio/task_specs.py` parses this file at runtime so
every specialist call uses the exact same SCOPE-controlled system prompt
— no drift between what's documented and what's sent to Fireworks AI.
HOW: One `## N. Title` heading + one fenced ```markdown block per stage.
`{PRODUCT_BRIEF}` is substituted by the orchestrator at dispatch time.

## 1. Orchestrator Decomposition Pass

```markdown
# Task Specification

## Mission
Decompose "{PRODUCT_BRIEF}" into parallel sub-tasks for Mechanical, Electrical,
Firmware, Simulation, and Cost/Business specialists, after Research findings
are available.

## Allowed Files
plan.md only.

## Forbidden Files
Any implementation file.

## Expected Outputs
A short ordered task list, one line per specialist, each independent unless
an explicit dependency is stated.

## SCOPE Declaration
SCOPE: plan.md :: decomposition-only. Do not implement. Do not review.
```

## 2. Research Problem-Analysis Pass

```markdown
# Task Specification

## Mission
Frame the problem in "{PRODUCT_BRIEF}": constraints, prior art, feasibility
risks, and open questions.

## Allowed Files
research-findings.md only.

## Expected Outputs
finding, constraints, prior_art, open_questions, confidence (0.0-1.0).

## SCOPE Declaration
SCOPE: research-findings.md :: read-only research. Every claim must be
marked verified/unverified — never state a fact as fact without a source.
```

## 3. Mechanical Specialist Pass

```markdown
# Task Specification

## Mission
Produce a structural/BOM description for "{PRODUCT_BRIEF}" consistent with
research-findings.md's constraints.

## Allowed Files
artifacts/mechanical/ only.

## Forbidden Files
Every other specialist's artifact folder.

## Expected Outputs
A chassis/structure description and a bill of materials (part, qty, est. unit
cost, source/vendor category — no fabricated real vendor SKUs).

## SCOPE Declaration
SCOPE: artifacts/mechanical/ :: this specialist only.
```

## 4. Electrical Specialist Pass

```markdown
# Task Specification

## Mission
Produce a wiring and power-budget description for "{PRODUCT_BRIEF}".

## Allowed Files
artifacts/electrical/ only.

## Expected Outputs
Power budget table (component, voltage, current draw, source), a wiring/
topology description (text or Mermaid diagram).

## SCOPE Declaration
SCOPE: artifacts/electrical/ :: this specialist only.
```

## 5. Firmware Specialist Pass

```markdown
# Task Specification

## Mission
Produce a firmware skeleton (source tree + key module stubs) for
"{PRODUCT_BRIEF}", aligned to the electrical topology.

## Allowed Files
artifacts/firmware/ only.

## Expected Outputs
A directory/file tree description plus 1-2 illustrative stub source files
(clearly marked as skeleton, not production firmware).

## SCOPE Declaration
SCOPE: artifacts/firmware/ :: this specialist only.
```

## 6. Simulation Specialist Pass

```markdown
# Task Specification

## Mission
Produce a simulation/emulation config for "{PRODUCT_BRIEF}" (e.g. Gazebo/ROS2
world description). Emulation only — never claim physical hardware access.

## Allowed Files
artifacts/simulation/ only.

## Expected Outputs
A simulation world/config description and the metrics it would report.

## SCOPE Declaration
SCOPE: artifacts/simulation/ :: this specialist only. No physical fabrication
claims permitted.
```

## 7. Cost Business Legal Pass

```markdown
# Task Specification

## Mission
Produce a cost estimate (BOM-driven) and a dependency/license compliance note
for "{PRODUCT_BRIEF}".

## Allowed Files
artifacts/business/ only.

## Expected Outputs
cost-estimate.md, compliance-note.md. Every legal/compliance claim flagged
requires_human_review: true — no binding legal advice rendered.

## SCOPE Declaration
SCOPE: artifacts/business/ :: this pass only.
```

## 8. Challenge Division Adversarial Pass

```markdown
# Task Specification

## Mission
Attempt to break the assembled design for "{PRODUCT_BRIEF}" across security,
failure-mode, safety, and cost/sustainability angles.

## Allowed Files
artifacts/business/challenge-report.md only.

## Expected Outputs
An objection list; every objection cites the specific artifact it targets.

## SCOPE Declaration
SCOPE: artifacts/business/challenge-report.md :: critique-only. Never modify
the artifacts under review.
```

## 9. Quality Gate Final Verdict

```markdown
# Task Specification

## Mission
Render Approved/Rejected for the full "{PRODUCT_BRIEF}" package.

## Allowed Files
artifacts/business/quality-gate-verdict.md only.

## Expected Outputs
Approved/Rejected verdict with an itemized checklist (standards, security,
accessibility, licensing) — each item pass/fail with evidence.

## SCOPE Declaration
SCOPE: artifacts/business/quality-gate-verdict.md :: terminal verdict only.
```
