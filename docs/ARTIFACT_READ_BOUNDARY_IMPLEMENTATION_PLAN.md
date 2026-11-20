---
title: "Engineering Studio X artifact read boundary implementation plan"
version: "2026.1.0.0"
date: "2026-11-20"
status: "Scoped implementation and staged roadmap"
---

# Engineering Studio X artifact read boundary implementation plan

WHAT: Defines the first read-side security milestone and the gates for
subsequent security and agent competency work. WHY: A workflow stage or a
successful model call does not by itself authorize reading a file or certify a
project outcome. HOW: Tie each requirement to a proof, a local behavior test,
an accountable boundary, and a reversible publication decision.

## 1. Verified starting point

The baseline is Engineering Studio main at
`55efcd55a266a629b19ae4926038fdebe5fb0768`, with the workflow graph and atomic
run snapshot changes. Before editing, the full local suite passed 190 tests
at 100% statement and branch coverage. Bandit reported zero source findings
and zero scan errors. A broader source-plus-scripts scan reported one medium
finding in local JUnit parsing and five low findings, with no high findings.
These results describe the inspected baseline and scanner, with no assertion
about dependency advisories. No usable offline advisory database was found in
the inspected local tool and cache locations.

The workflow declares eleven executed stages in six batches. The agent
catalog describes many more roles than the executable workflow dispatches.
The runtime invokes text model clients and writes stage Markdown. It does
not demonstrate tool-backed engineering verification, project-specific
planning, or a machine-enforced quality verdict. A successful run means the
pipeline returned, which can include a generated negative verdict.

## 2. This milestone and blast radius

Close only the shared artifact read selector. The JSON preview, attachment,
and ZIP routes already delegate to `RunStore.artifact_path`. The route
contracts for canonical files stay intact. An unavailable or rejected lookup
uses the existing not-ready outcome.

| ID | Requirement | Local oracle |
|---|---|---|
| AR-01 | A requested stage must be in the executable stage catalog. | A benign unlisted stage remains unavailable even with an on-disk file. Preview and attachment return 404. |
| AR-02 | A registered run ID must be one nonempty ASCII segment using letters, digits, underscore, or hyphen. | Invalid stored ID and absent registry entry do not produce a path. Generated and safe legacy IDs retain behavior. |
| AR-03 | The canonical file must occupy the exact expected slot beneath the configured resolved root. | A simulated resolution to another slot is rejected. Missing paths and lookup errors return no artifact. |
| AR-04 | The slot must contain a regular file. | An existing directory is rejected. Legitimate text and downloads remain available. |
| AR-05 | Publication must be independently reviewed. | The proof, local report hashes, Git LFS PDF, regression, browser, mutation, and source-security records bind the candidate. |

The proof assumes stable namespace through consumption, trustworthy
filesystem resolution, and a configured trusted root. Hard links, changing
namespace, caller identity, authorization, quotas, and later read failures
require separate controls. Reviewers should not treat valid paths as proof of
trustworthy contents. There is no schema migration. Rollback is a source
revert through another locally verified PR. Restoring the old selector
reopens the rejected-path cases and requires an explicit security decision.

## 3. Proof-to-implementation sequence

1. Review the numbered companion and its hypotheses in
   [Artifact read boundary](../paper/openai_dev_week/artifact_read_boundary.tex).
2. Keep validation and resolution in RunStore. Test before expanding any
   route or capability. Preserve the existing atomic run snapshot code.
3. Run coverage and mutation checks locally. Test exact-slot decisions at
   the store boundary and behavior at the HTTP boundary.
4. Run a source security scan after each changed development stage.
   Independently review new findings, fix applicable findings, and rerun.
5. Revalidate the final committed tree before pushing and again before merge.
   Verify GitHub Actions is disabled. GitHub hosts the code review and merge.
   Build, verification, packaging, and authorized deployment run locally.

## 4. Broader proof and capability backlog

These are future obligations. Their proof and implementation status is
proposed. Prioritize controls before enabling capabilities that use them. The
[agent contract](../.github/agents/AGENT_CONTRACT.md) already describes
permissions and independent review. Those descriptions are inputs to future
runtime controls.

| Order | Gap and projects affected | Formal obligation | Acceptance and rollback |
|---|---|---|---|
| 1 | Caller ownership and tool authority for shared software and data projects | Prove deny-by-default for unknown principals, absent grants, revoked grants and cross-run access. Verify consent before side effects. | Multi-user isolation tests; disable tool grants on rollback; retain audit receipts. |
| 2 | Artifact and verdict traceability across software, CAD, embedded, and research projects | Bind byte identities to versioned candidate, plan, inputs, tool receipts, and independent review. Prove failed, stale, incomplete or contradictory evidence cannot yield approval. | Replay a fixed run with regenerated and tampered artifacts; keep previous verifier as a versioned reader, never bypass current acceptance policy silently. |
| 3 | Project competency selection. Existing stages do not certify API contract behavior, CAD constraints, firmware build and timing, or research reproducibility | Define typed capability and output contracts and ordered dependencies. Prove closure from requirements to capable producers and independent checks. Unsupported work yields an explicit blocked state. | Software API/schema checks, CAD deterministic inspection, embedded build/simulation, and research fixture reproducibility. Require restricted adapters and per-project benchmarks before activation. Roll back by disabling the affected adapter. |
| 4 | Secure actions, resumable execution, and bounded scale | Prove permit limits under concurrent admission; stage ledger monotonicity and idempotent resume; bounded queue behavior; transactional rollback of reversible effects. | Fault injection at commit/restart, fairness and load bounds, per-run budgets, human approval and compensation for external effects. Start with one worker and retain a tested previous release. |

## 5. Local security and release evidence

Run `python -m bandit -r src -f json -o <local-evidence>/bandit.json` after
each source milestone. Keep the baseline, final scan, scanner version,
triage, exact commit, and independent review together. For CVE checks, scan
the exact deployment dependency inventory against a provisioned, versioned
offline advisory database. Record the inventory digest, database digest and
as-of date. A missing or stale database means dependency status is unknown
and blocks release promotion. Dependency scanning and the source scan answer
different questions. See the release plan above for rollback and approvals.

Run the full local pytest branch gate, isolated Chromium tests and
declared mutation gate from the repository's Local CI instructions. Preserve
reports and rerun after any candidate change. A scoped mutation score is not
a claim of repository-wide mutation coverage.

## Changelog

| Version | Date | Change |
|---|---|---|
| 2026.1.0.0 | 2026-11-20 | Record the artifact selector proof and implementation gates, security scan cadence, rollback, and project competency roadmap. |
