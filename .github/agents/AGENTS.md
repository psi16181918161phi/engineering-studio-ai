# Agent Definition Governance

All `.agent.md` files in this directory and every subdirectory inherit
`AGENT_CONTRACT.md`. Before an agent acts, it must resolve applicable standards
and conflicts with `STANDARDS_ROUTER.yaml`. Role-specific instructions may make
the contract stricter but may not weaken or silently override it.

Every new or materially changed role must provide a narrow mission, triggers and
non-triggers, required inputs, allowed/forbidden scope, standards route IDs,
evidence requirements, tool permissions, procedure, failure/retry behavior,
acceptance criteria, a registered output schema reference, escalation rules,
positive and negative examples, evaluation fixtures, and SemVer compatibility
notes. These elements may be stated in the role or inherited from
`AGENT_CONTRACT.md`; inherited elements remain mandatory at runtime.

The files in this subtree are governance definitions, not proof that a runtime
stage is wired. Documentation must distinguish `defined`, `registered`,
`enforced`, and `evaluated` lifecycle states.
