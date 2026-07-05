# Engineering Studio AI

**AMD LabLabAI Hackathon — Act II — Unicorn Track submission.**

Type one product brief (e.g. *"Design a warehouse robot"*) and a small
team of AI specialist agents — Mechanical, Electrical, Firmware,
Simulation, Cost/Business, Legal — collaborate in parallel over Fireworks
AI-hosted open models to produce a complete engineering package: BOM,
wiring/power notes, a firmware skeleton, a simulation config
(emulation-only — no physical fabrication claimed), a cost estimate, and a
documentation export.

See [VISION_AMD_LABLAB_HACKATHON_ENGINEERING_STUDIO.md](https://github.com/psi16181918161phi/CodingStandardsRef/blob/main/markdowns/visions/VISION_AMD_LABLAB_HACKATHON_ENGINEERING_STUDIO.md)
for the full track rationale (private repo — team members only).

## Why this repo is separate from our standards corpus

This is a **public** hackathon submission. Our team's full internal coding
standards corpus lives in a private repo. Rather than expose that whole
corpus here, we've distilled only the rules that apply to this project
into [AGENTS.md](AGENTS.md). If you're a teammate who needs the full
corpus, ask for private repo access separately.

## Architecture

```
Orchestrator ──► Research (problem framing)
                     │
       ┌─────────────┼─────────────┬──────────────┐
       ▼             ▼             ▼              ▼
  Mechanical    Electrical     Firmware      Simulation
       │             │             │              │
       └─────────────┴──────┬──────┴──────────────┘
                             ▼
                    Cost/Business + Legal
                             │
                             ▼
                    Challenge Division (critique)
                             │
                             ▼
                    Quality Gate (verdict)
```

Each stage is a Task Specification (`docs/task-specs.md`) dispatched as a
Fireworks AI chat completion call. Every specialist writes ONLY to its own
`src/engineering_studio/artifacts/<discipline>/` folder — see
[AGENTS.md §3](AGENTS.md#3-scope-control-non-negotiable-for-every-agent-call).

## Quick start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env   # then fill in FIREWORKS_API_KEY
python -m engineering_studio.cli "Design a warehouse robot"
```

## Repository layout

| Path | Purpose |
|---|---|
| `src/engineering_studio/agents/` | One module per specialist (orchestrator, research, mechanical, electrical, firmware, simulation, business, challenge, quality_gate). |
| `src/engineering_studio/fireworks_client.py` | Thin Fireworks AI chat-completions client with a local-llama fallback (model routing, never single-vendor hard-coded). |
| `src/engineering_studio/artifacts/` | Per-discipline output folders (gitignored contents; `.gitkeep` only). |
| `docs/task-specs.md` | The filled Task Specification blocks each agent call uses. |
| `tests/` | Unit tests with a mocked Fireworks client (no live network calls in CI). |
| `AGENTS.md` | Condensed standards reference (see above). |

## Status

Draft — hackathon in progress. See `docs/task-specs.md` for the current
pipeline stage definitions.

## License

MIT — see [LICENSE](LICENSE).
