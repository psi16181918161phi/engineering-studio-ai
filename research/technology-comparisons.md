# Technology Comparisons — Engineering Studio AI

WHAT: Side-by-side comparisons of candidate models, frameworks, and AMD
infrastructure options.
WHY: Backs Role 3's implementation decisions with a documented rationale
instead of an undocumented ad hoc choice.
HOW: One table per comparison category. Add rows as options are
evaluated; never delete a rejected option — mark it `Rejected` with a
one-line reason instead, so the team doesn't re-debate it later.

## Model / Inference Provider Options

| Option | Pros | Cons | Status |
|---|---|---|---|
| Fireworks AI | OpenAI-compatible API (chat.completions), minimizing client rewrite cost; supports function calling and JSON-mode structured output, needed for parsing specialist agent outputs; batch inference and prompt-cache discounts (50% each) lower cost for repeated/offline calls; no self-hosting or GPU provisioning required. | Per-token billing scales with the 9-stage pipeline's cumulative token count; new/free-tier accounts are rate-limited (10 req/min) until a payment method is added; availability and latency depend on a third-party service outside team control; model catalog limited to what Fireworks hosts. | Selected (see `../AGENTS.md`, `fireworks_client.py`) |
| Local llama fallback | Removes single-point-of-failure dependency on an external API if Fireworks is unavailable during the demo; AMD Developer Cloud provides on-demand MI300X instances (192 GB HBM3) that can host large open-weight models without multi-GPU sharding; vLLM exposes an OpenAI-compatible endpoint, so fireworks_client.py-style call code is largely reusable; $100 in AMD AI Developer Program credits (~50 GPU-hours at ~$1.99/hr) covers hackathon-scale usage | Requires provisioning and configuring a GPU droplet ahead of the demo (image selection, SSH setup, container start) — non-trivial setup time versus a pure-API call path; incurs hourly GPU cost while the instance runs, independent of token usage; not viable on typical team laptops/desktops without a cloud GPU instance; team must own uptime/monitoring for the fallback path instead of relying on a vendor SLA. | Selected as fallback |

## Agent Framework Options

| Option | Pros | Cons | Status |
| CrewAI | Role-based abstraction maps naturally onto this project's Mechanical/Electrical/Firmware/Simulation/Cost-Business role split; low boilerplate to define agents and hand off tasks. | Coarse-grained error handling and no built-in checkpointing for long-running or partially-failed runs; adds a dependency and abstraction layer the project's fixed, mostly-parallel pipeline does not require. | Rejected — repo already implements a lightweight SCOPE-based dispatch table per AGENTS.md §2; adopting CrewAI would duplicate that mechanism without adding needed capability for this scope. |
| LangGraph | Explicit graph/state-machine model with checkpointing and human-in-the-loop primitives; well suited to workflows with cycles, branching, or long-lived state. | Steeper setup and learning curve; the project's specialist stages are a largely single-pass sequence (Orchestrator → parallel specialists → Challenge Division → Quality Gate) without the cyclical/branching control flow LangGraph is built for. | Rejected — pipeline shape does not need graph-level state management; adds implementation overhead not justified by the 5-day hackathon timeline (SCAFFOLDING.md). |
| AutoGen / AG2 | Conversational GroupChat pattern is a plausible fit for the Challenge Division's adversarial critique concept (agents debating over a shared artifact). | Each conversational turn resends accumulated history, increasing token cost — a concern given the team's ~100K-token-per-run target; Microsoft has shifted primary development to Microsoft Agent Framework 1.0, with AutoGen/AG2 in a legacy/maintenance posture as of Q2 2026. | Rejected — token overhead conflicts with the team's stated ~100K token budget; framework not under active primary development. |
| Custom orchestration | Full control over per-agent SCOPE, Allowed/Forbidden Files, and Expected Outputs, already specified in AGENTS.md §3; no added framework dependency or version-compatibility surface; simplest to reason about for token-budget tracking. | Team is responsible for implementing its own retry/error handling and observability (no built-in tracing/checkpointing that a framework like LangGraph would provide). | Selected (see ../AGENTS.md §2–§3) |


## AMD-Specific Infrastructure Notes

| Item | Notes | Verified? |
| AMD Developer Cloud | On-demand GPU droplets (DigitalOcean-based) providing AMD Instinct MI300X access (192 GB HBM3 per GPU); AMD AI Developer Program grants ~$100 in credit (≈50 GPU-hours at ~$1.99/hr for a single MI300X instance). Proposed as the hosting environment for the local-llama fallback path; not yet provisioned or configured for this project. | Verified |
| ROCm | AMD's open-source GPU compute stack (CUDA-equivalent). Official documentation states PyTorch, vLLM, and Hugging Face TGI run on ROCm with prebuilt Docker images targeting MI300X/MI325X/MI350X/MI355X. The project would not need to write ROCm/HIP kernels directly — vLLM handles that layer — but ROCm is the underlying runtime the fallback path depends on. | verified |
| vLLM (ROCm build) | AMD publishes a prebuilt ROCm-enabled vLLM Docker image (vllm/vllm-openai-rocm) integrating ROCm, PyTorch, and vLLM for MI300X-class GPUs, and exposes an OpenAI-compatible serving endpoint. This is the specific serving layer proposed for the local-llama fallback, chosen so the fallback client can reuse most of the fireworks_client.py-style request/response handling. Not yet deployed for this project. | verified |
