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

Per `../AGENTS.md` §5 ("live-data honesty": never silently substitute a
fabricated "success" result for a failed/rate-limited live call), if the
live Fireworks AI call fails, times out, or is rate-limited during the
actual presentation, the presenter follows this explicit, truthful
fallback flow instead of ad-libbing or re-trying silently:

1. **Say it plainly, on stage.** State to the audience/judges, in one
   sentence, what happened — e.g. "the live model call just timed out /
   hit a rate limit; here is a previously recorded real run of the exact
   same pipeline so you can still see it end-to-end." This is a disclosed
   substitution, not a hidden one.
2. **Prove the app itself is still up.** Open `GET /api/health` in a
   second browser tab (or `curl http://127.0.0.1:8000/api/health`) and
   show the `{"status": "ok"}` response live — this demonstrates the
   running application/server is healthy and the failure is isolated to
   the third-party model call, not the product.
3. **Play the pre-recorded fallback run.** Use the Mode-B (mocked
   pipeline, deterministic, no live network call) recordings already
   captured by `playwright_demo_script.py` under
   `demo/recordings/video/{light,dark}/` and
   `demo/recordings/screenshots/{light,dark}/` — narrate over the video
   using the same beats as the table above (Beats 1-7). These recordings
   are explicitly labeled Mode B (mocked) in `docs/PLAYWRIGHT_INTEGRATION_PLAN.md`
   §3 and must be introduced to the audience as such, never presented as
   a live call that succeeded.
4. **Reveal a real artifact set.** Open one already-completed run's
   artifact folder (e.g. via the CLI: `python -m engineering_studio.cli artifacts --artifacts-root runs/demo/artifacts`,
   or the dashboard's "Download all (.zip)" button on a prior completed
   run) so the audience still sees genuine, previously-generated
   BOM/wiring/firmware/simulation/cost/docs output, not a mockup.
5. **Offer a second live attempt only if time allows**, after the
   fallback narration — do not silently retry mid-sentence and hope it
   resolves; call out explicitly that this is "attempt two, live" if
   taken.

**Preparation checklist (before presenting):** confirm at least one
Mode-B recording set exists under `demo/recordings/` for each of the 3
confirmed demo prompts (`demo/demo_prompts.json`); confirm at least one
completed run's artifacts exist under a known `--artifacts-root` path
that can be opened instantly without re-running the pipeline; confirm
`GET /api/health` is reachable from the presentation machine/network
before going on stage.
