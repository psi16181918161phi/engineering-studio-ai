"""WHAT: Test-support utilities shipped as part of the installable package.
WHY: `runs.py` needs a deterministic, no-network pipeline implementation
for CI-safe end-to-end (Playwright) runs against a real, live `uvicorn`
process — a subprocess boundary means `monkeypatch` (used by the unit
test suite) cannot reach across into it, so an environment-variable
opt-in (`ENGINEERING_STUDIO_FAKE_PIPELINE=1`) is the only way to swap the
implementation for an out-of-process server.
HOW: `fake_pipeline.fake_run_pipeline` matches `agents.orchestrator.
run_pipeline`'s exact signature so `runs.py` can substitute it with zero
call-site changes.
"""
