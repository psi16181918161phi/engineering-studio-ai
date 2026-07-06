---
title: "Research Findings — Engineering Studio AI"
author: Hadrian Hu
date: 2026-07-05
version: "0.1.0"
keywords:
  - agent-frameworks
  - amd
  - benchmarking
  - engineering-studio-ai
  - fireworks-ai
  - prior-art
  - prompt-engineering
status: "Draft"
changelog:
  - version: "0.1.0"
    date: "2026-07-05"
    author: "Hadrian Hu"
    description: "Template scaffold — sections to be filled by Role 2."
---
# Research Findings — Engineering Studio AI

## Table of Contents

- [Abstract](#abstract)
- [Keywords](#keywords)
- [Executive Summary](#executive-summary)
- [1. Constraints](#1-constraints)
- [2. Prior Art](#2-prior-art)
- [3. Findings](#3-findings)
- [4. Open Questions](#4-open-questions)
- [Changelog](#changelog)

## Abstract

## Abstract

This document frames the research problem behind Engineering Studio AI's
Research stage (docs/task-specs.md §2): a multi-agent pipeline that is
proposed to decompose a natural-language product brief into
Mechanical, Electrical, Firmware, Simulation, and Cost/Business/Legal
artifacts, dispatched as Fireworks AI chat-completion calls and critiqued
by an adversarial Challenge Division before a Quality Gate verdict. No
part of the pipeline is claimed to be implemented, benchmarked, or
demoed as of this writing — this document only surveys the technology
landscape the design is expected to draw on: multi-agent orchestration
frameworks, the Fireworks AI serverless inference platform, AMD's
ROCm/Instinct GPU stack (the hackathon's sponsor track), prompt
engineering practice for scope-controlled tool-calling agents, and
comparable LLM-driven engineering-assistant research. Every claim below
is tagged Verified or Unverified with a 0.0–1.0 confidence score, per
AGENTS.md §5's grounding rule and docs/task-specs.md §2's Expected
Outputs.

## Keywords

agent-frameworks, amd, benchmarking, engineering-studio-ai, fireworks-ai,
prior-art, prompt-engineering

## Executive Summary

Objective: Establish a sourced, confidence-scored technology base for
the Research stage of the Engineering Studio AI pipeline, so downstream
specialist prompts (Mechanical, Electrical, Firmware, Simulation,
Cost/Business) are grounded in verifiable facts about the frameworks,
inference provider, and hardware platform the design is proposed to use,
rather than in unexamined assumptions.
Approach: Reviewed the repository's own draft design documents
(README.md, AGENTS.md, SCAFFOLDING.md, docs/task-specs.md,
docs/RESPONSIBILITIES.md) to confirm scope, then researched (a) the
three multi-agent orchestration frameworks most directly comparable to
this project's Orchestrator → parallel-specialists → Challenge Division
→ Quality Gate shape (AutoGen/AG2, CrewAI, LangGraph), (b) Fireworks AI's
publicly documented serving paths, pricing, and tool-calling support,
(c) AMD's ROCm/Instinct MI300X stack as the sponsor-track hardware
context, and (d) peer-reviewed and preprint work on LLM-driven hardware
and firmware generation, since that is the closest existing prior art to
an "engineering studio" concept.
Outcome: No comparable end-to-end system (brief → BOM + wiring +
firmware skeleton + simulation config + cost estimate + adversarial
review, in one pipeline) was found in the literature or in public
hackathon submissions searched; the closest prior art addresses single
disciplines (circuit schematics, firmware security, CFD configs)
rather than the six-discipline breadth this project proposes. This
suggests the project's differentiator is breadth-of-integration rather
than depth-of-technique in any one discipline — a finding with direct
implications for the Challenge Division's adversarial pass (§3, §4).
Recommendations: Treat every specialist artifact as provisional
engineering guidance requiring human review, not a fabrication-verified
design — consistent with docs/task-specs.md's "no fabricated real
vendor SKUs" and "requires_human_review: true" constraints already
written into the Task Specification blocks. Prioritize a lightweight,
model-agnostic prompt structure (SCOPE + Allowed/Forbidden Files +
Expected Outputs, already adopted in AGENTS.md §3) over adopting a
heavyweight orchestration framework wholesale, given the hackathon time
budget documented in §1 below.


## 1. Constraints

| Constraint | Description | Source |
| Hackathon timeline | The project is a fixed-duration hackathon submission (AMD LabLabAI Hackathon, Act II, Unicorn Track); SCAFFOLDING.md frames scaffolding decisions around a "5-day hackathon" window with six parallel roles. | SCAFFOLDING.md (this repo) — Verified, 0.95 |
| No physical fabrication | The Simulation specialist's Task Specification explicitly forbids physical-hardware-access claims; outputs are emulation/config only (e.g. a Gazebo/ROS2 world description). | docs/task-specs.md §6 (this repo) — Verified, 0.95 |
| Fireworks AI as the inference vendor | Fireworks AI (not a self-hosted AMD endpoint) is the pipeline's primary named inference provider per the repo's own README and hackathon branding ("Fireworks AI-hosted open models"). | README.md (this repo) — Verified, 0.9 |
| Scope-controlled agent calls | Every specialist prompt must declare Allowed Files, Forbidden Files, and Acceptance Criteria; specialists write only to their own artifacts/<discipline>/ folder. | AGENTS.md §3 (this repo) — Verified, 0.95 |
| No fabricated technical facts | Agents must never state a BOM number, part number, or benchmark figure as fact without a source; unverifiable claims must be marked unverified. | AGENTS.md §5, docs/task-specs.md §2 (this repo) — Verified, 0.95 |
| Model-routing, non-single-vendor | The backend's Fireworks client is designed with "a local-llama fallback (model routing, never single-vendor hard-coded)," per the repo's own README. | README.md (this repo) — Verified, 0.9 |
| Sponsor hardware track | The hackathon is AMD-sponsored; entrants are expected to build on AMD's Developer Cloud / Instinct MI300X GPUs, with $100 in free credits (~50 GPU-hours) available via the AMD AI Developer Program. | lablab.ai AMD Developer Cloud tutorial — Verified, 0.75 |
| Fireworks pricing/rate-limit budget | Fireworks serverless inference is billed per token across input/cached-input/output; a new account receives roughly $1 in evaluation credit before a payment method is required, and unauthenticated/low-tier accounts face a request-rate cap. | Fireworks AI docs (docs.fireworks.ai/serverless/pricing); pricepertoken.com Fireworks free-tier page — Verified, 0.7 |
| Legal/compliance claims require human review | Every legal or compliance-adjacent output from the Cost/Business/Legal pass must be flagged requires_human_review: true; no binding legal advice is rendered by the pipeline | docs/task-specs.md §7 (this repo) — Verified, 0.95 |
| Team-coordination constraint | Six roles work in parallel; only three files (docs/task-specs.md, docs/TEAM_QA.md, root docs) are shared and require a coordination protocol to avoid merge conflicts. | SCAFFOLDING.md §2, §4 (this repo) — Verified, 0.9 |

## 2. Prior Art

| Project/Paper | Relevance | Link | Verified? |
| CircuitLM (Al Hasan et al., 2026 preprint) | Closest single-discipline analog: a five-stage multi-agent pipeline that turns a natural-language prompt into a structured, visually-interpretable circuit schematic, grounded in a curated component knowledge base and scored with a "Dual-Metric Circuit Validation" framework. Directly relevant to the proposed Electrical specialist's grounding/hallucination concerns. | arxiv.org/abs/2601.04505 | Verified, 0.7 |
| "Securing LLM-Generated Embedded Firmware through AI Agent-Driven Validation and Patching" (2025 preprint) | Multi-agent, three-phase generate/verify/patch cycle for LLM-generated firmware; relevant prior art for the proposed Firmware specialist's "skeleton, not production firmware" framing and for why firmware outputs need adversarial review. | arxiv.org/abs/2509.09970 | Verified, 0.6 |
| CFDagent (2025 preprint) | Three-agent (preprocess/solve/postprocess) pipeline that turns a natural-language description into a CFD simulation; closest analog to the proposed Simulation specialist's "emulation-only" scope, though it targets fluid dynamics rather than robotics/Gazebo-style world configs. | arxiv.org/pdf/2507.23693 | Verified, 0.55 |
| "AI-Driven Automation for Digital Hardware Design: A Multi-Agent Generative Approach" (ACM, 2025) | Decomposes a high-level system spec into functional blocks via an LLM, then generates architectural models with RAG-augmented context; relevant precedent for orchestrator decomposition passes generally, though scoped to digital hardware/Verilog rather than a six-discipline studio. | dl.acm.org/doi/10.1145/3748382.3748388 | Verified, 0.55 |
| AutoGen / AG2 (Microsoft) | Conversational multi-agent framework (GroupChat pattern); as of Q2 2026 Microsoft has folded new development into "Microsoft Agent Framework 1.0," with AutoGen/AG2 continuing as a legacy/community path. Relevant as a considered-and-not-adopted alternative to this project's simpler Task-Specification-driven dispatch model — a full GroupChat-style deliberation was judged unnecessary for a fixed pipeline of independent specialists. | Multiple 2026 framework-comparison articles (see §3) | Verified, 0.6 |
| CrewAI | Role-based "crew" framework explicitly designed for workflows that "split naturally into specialist roles" — structurally the closest match to this project's Mechanical/Electrical/Firmware/Simulation/Business role split, though this repo's design (per AGENTS.md §2 OCP note) implements its own lightweight dispatch table rather than adopting CrewAI as a dependency. | Multiple 2026 framework-comparison articles (see §3) | Multiple 2026 framework-comparison articles (see §3) | Verified, 0.6 |
| LangGraph | Graph-based stateful orchestration with checkpointing and human-in-the-loop primitives; considered as a heavier-weight alternative offering more production-grade state management than this project's scope requires for a fixed, mostly-parallel five-day pipeline. | Multiple 2026 framework-comparison articles (see §3) | Verified, 0.6 |
| lablab.ai AMD Developer Hackathon (May 2026) submission gallery | Contemporaneous hackathon prior art on the same sponsor hardware (AMD MI300X/ROCm): multiple prior submissions used multi-agent LLM pipelines (e.g. a document-review "Analyst/Skeptic/Strategist/Auditor" four-agent deliberation system on Llama 3.1 70B + vLLM), which parallels this project's Challenge Division adversarial-critique concept but for document review rather than engineering artifacts. | lablab.ai/ai-hackathons/amd-developer | Verified, 0.6 |  

## 3. Findings

Use one row per finding. `confidence` is a 0.0–1.0 self-assessment, not a
guess dressed up as certainty.

| Finding | Verified/Unverified | Confidence | Source |
| No published system was found that performs this project's full proposed scope (brief → BOM + wiring/power notes + firmware skeleton + simulation config + cost estimate + documentation export, in one adversarially-reviewed pipeline); closest prior art (CircuitLM, CFDagent, the firmware-security paper) each cover one discipline. | Unverified (absence claim — a targeted literature/hackathon-gallery search found none, which cannot rule out an unindexed or very recent submission) | 0.55 | Search performed 2026-07-06; see §2 |
| CrewAI is the framework most structurally analogous to this project's design (fixed roles, largely-parallel task execution) among the three major options surveyed, but the current repo design does not depend on any of the three — it implements its own SCOPE-declaration dispatch table per AGENTS.md §2's OCP note ("add a new specialist agent as a new file; don't rewrite the Orchestrator's dispatch table") | Verified (for the framework comparison) / the repo's independent-implementation choice is a design statement, not an external fact | 0.7 | 2026 framework comparisons (pecollective.com, openagents.org, datacamp.com, alicelabs.ai); AGENTS.md (this repo) |
| Microsoft has shifted AutoGen/AG2 to a legacy/maintenance posture as of April 2026, consolidating new development into "Microsoft Agent Framework 1.0." This is relevant context if a future iteration of the project were to consider adopting a named framework rather than the current custom dispatch table. | Verified | 0.65 | openagents.org (2026-02-23), alicelabs.ai (2026, Q2 roundup) |
| Fireworks AI's serverless API is OpenAI-compatible, supports function calling and JSON-mode structured output on its hosted open-weight models, and prices batch inference at a 50% discount versus standard per-token serverless rates — relevant to a future cost estimate for running the six-stage pipeline at scale. | Verified | 0.7 | docs.fireworks.ai/serverless/pricing; modern-datatools.com Fireworks review (2026-04-29); artificialanalysis.ai/providers/fireworks |
| AMD's Developer Cloud offers MI300X GPU instances (192 GB HBM3) at approximately $1.99/hr on-demand, with a $100 free-credit grant (~50 GPU-hours) available through the AMD AI Developer Program — directly relevant as a possible future compute budget line if any pipeline stage is run on a self-hosted open model rather than purely through the Fireworks API. | Verified | 0.7 | lablab.ai AMD Developer Cloud tutorial (2026-03-24); AMD ROCm AI Developer Hub |
| ROCm (AMD's open-source CUDA-equivalent stack) has first-class support for PyTorch, vLLM, and Hugging Face's TGI as of 2026, meaning a future self-hosted fallback model does not require custom ROCm/ HIP kernel work for standard inference workloads — consistent with the repo's own stated design goal of "a local-llama fallback." | Verified | 0.65 | rocm.docs.amd.com vLLM inference page; rocm.docs.amd.com LLM inference frameworks page |
| A SCOPE-declaration prompt structure (Allowed Files / Forbidden Files / Expected Outputs), as already adopted in this repo's docs/task-specs.md, is consistent with general prompt-engineering guidance to give models explicit constraints, structured output expectations, and role framing rather than open-ended instructions — this is a design-consistency observation, not a claim that any specific external prompt-engineering paper prescribes this exact structure. | Unverified as a citation to a specific external source; the underlying practice (explicit constraints + structured output) is widely documented prompt-engineering guidance | 0.5 | General prompt-engineering practice; no single authoritative source cited to avoid overclaiming |
| The six-discipline specialist split (Mechanical, Electrical, Firmware, Simulation, Cost/Business, Legal) has partial precedent in narrower academic multi-agent design pipelines, but none of the surveyed prior art combines all six with an adversarial "Challenge Division" critique stage before a terminal Quality Gate verdict — this appears to be this project's most novel structural element relative to the prior art surveyed. | Unverified (novelty claim based on a bounded search, not an exhaustive literature review) | 0.5 | Synthesis of §2 findings | 

## 4. Open Questions

- Should the pipeline standardize on Fireworks AI exclusively, or does the "local-llama fallback" mentioned in README.md need a concrete self-hosting plan (e.g. AMD Developer Cloud + vLLM) before the hackathon deadline, given the additional setup time that would require versus a pure-Fireworks call path?
- What is the actual per-run cost of the nine-stage pipeline (Orchestrator → Research → 5 parallel specialists → Cost/Business → Challenge Division → Quality Gate) at Fireworks' serverless per-token rates, and does that cost fit whatever demo budget Role 1/Role 4 have allocated? This has not been estimated because no specific model or token-volume assumptions have been fixed yet. 
- Does the Challenge Division's adversarial pass need its own distinct model/persona from the specialist it is critiquing (to avoid a model critiquing its own output with the same biases), and if so, does that require routing to a second Fireworks model or a different sampling configuration on the same model? 
- Given that no directly comparable six-discipline prior art was found (§2, §3), what is the minimum viable subset of disciplines to fully implement and polish for the demo, versus which should remain a documented "proposed but not built" stretch goal, per docs/RESPONSIBILITIES.md's guidance to prioritize "a polished, working demonstration over an overly ambitious feature set"?
- Should technology-comparisons.md (the sibling Role 2 deliverable named in research/README.md) carry the full framework benchmark detail, with this file limited to a pointer, to avoid duplicating the AutoGen/CrewAI/LangGraph comparison across two files?
- What confidence threshold (if any) should the Quality Gate require before treating a specialist's finding as "safe to present" in the live demo, given that several findings above are self-rated at 0.5–0.55 confidence?

## Changelog

| Version | Date | Author | Description |
|---|---|---|---|
| 0.1.0 | 2026-07-05 | Hadrian Hu | Template scaffold created. |
| 0.1.1 | 2026-07-06 | Umaima Mughal | Completed the research findings document by replacing template placeholders with researched content. |
