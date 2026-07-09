# Slides Outline — Engineering Studio AI

WHAT: Slide-by-slide content plan for the hackathon pitch.
WHY: Lets Role 6 draft the narrative before investing in slide design,
and lets other roles review/comment on content via a plain-text diff.
HOW: One `##` heading per slide; keep bullets terse — this is a plan, not
the deck itself.

## Slide 1 — Title

- Product name, one-line pitch, team name.

## Slide 2 — Problem

- Turning one natural-language product idea into a *complete* engineering
  package today means separately briefing (or hiring) a mechanical
  engineer, an electrical engineer, a firmware engineer, a simulation
  engineer, and a cost/business analyst — then manually reconciling their
  outputs into one coherent, submittable package.
- That hand-off chain is slow, inconsistent (each specialist works from a
  slightly different re-telling of the brief), and hard to audit (no
  single place shows how the mechanical BOM, wiring notes, firmware
  skeleton, and cost estimate were each derived from the same brief).
- Existing single-model "ask an LLM for code" tools solve the software
  half but stop at one artifact type (usually just code) — none of them
  produce a full, multi-discipline engineering package with an
  adversarial review and an explicit pass/fail quality verdict attached.

## Slide 3 — Solution: Engineering Studio AI

- One prompt in → multi-agent collaboration → complete engineering
  package out (BOM, wiring/power notes, firmware skeleton, simulation
  config, cost estimate, docs export).

## Slide 4 — Architecture

- Reuse the architecture diagram from `../README.md` §Architecture.

## Slide 5 — Live Demo

- Mirror `../demo/demo-script.md` beats.

## Slide 6 — AMD Ecosystem Usage

- Primary inference path: Fireworks AI (OpenAI-compatible chat-completions
  API), selected per `../research/technology-comparisons.md` for
  structured/JSON-mode output the multi-stage pipeline parses per stage.
- Disclosed fallback path (not yet provisioned for this submission, per
  the same document): AMD Developer Cloud on-demand GPU droplets
  exposing AMD Instinct MI300X (192 GB HBM3), running a ROCm-enabled
  vLLM Docker image (`vllm/vllm-openai-rocm`) behind an OpenAI-compatible
  endpoint — chosen specifically so `fireworks_client.py`'s existing
  request/response handling is reusable with minimal changes, funded by
  the AMD AI Developer Program's ~$100 credit (~50 GPU-hours at a single
  MI300X instance's ~$1.99/hr rate).
- Framing: AMD-ecosystem usage in this submission is honestly scoped —
  the *live* demo runs on Fireworks AI; the MI300X/ROCm/vLLM path is a
  researched, documented, cost-modeled fallback architecture, not a
  claim of hardware already exercised in this build (see
  `../research/technology-comparisons.md`'s own `Verified?` column).

## Slide 7 — Results / Validation

- Testing bar met (100% coverage, 100% pass — `../docs/TEAM_QA.md` §5).

## Slide 8 — Startup Potential / Roadmap

- Near-term (post-hackathon): open the MI300X/ROCm/vLLM fallback path for
  real (currently only researched/cost-modeled, per Slide 6), add more
  domain specialists (e.g. dedicated robotics/perception/planning roles
  already mapped in `../docs/VISION_AMD_LABLAB_HACKATHON_ENGINEERING_STUDIO.md`
  §4), and let a user iterate a brief across multiple pipeline runs
  instead of one-shot.
- Product framing: the same orchestrator -> parallel specialists ->
  adversarial review -> quality-gate pipeline shape is domain-agnostic —
  the specialist roster (Mechanical/Electrical/Firmware/Simulation/
  Cost-Business) is what makes this build "engineering"-flavored; swap
  the roster and Task Specifications (`../docs/task-specs.md`) for
  another discipline set and the same orchestration core applies, which
  is the basis for a horizontal "AI studio" product rather than a
  single-vertical tool.
- Honest current-state caveat for this slide: no market validation,
  pricing model, or customer discovery has been performed for this
  submission — this section states architecture-level extensibility, not
  a validated business plan.

## Slide 9 — Team & Thanks

- Six-role credits per `../docs/RESPONSIBILITIES.md`.
