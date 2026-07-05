"""WHAT: Orchestrates the Engineering Studio AI pipeline: Research ->
parallel specialist fan-out -> business/legal -> (challenge/gate stubs).
WHY: Single place that knows the pipeline ORDER (Workflow-position axis);
every stage's actual work stays inside its own SpecialistAgent (SRP).
HOW: Sequential Research pass, then a thread-pool fan-out of the parallel
specialists (they don't depend on each other, only on Research), then the
Business/Legal pass which depends on all specialist outputs.
"""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from engineering_studio.agents.specialist import SpecialistAgent
from engineering_studio.fireworks_client import ModelClient
from engineering_studio.task_specs import get_task_spec

PARALLEL_DISCIPLINES = ("mechanical", "electrical", "firmware", "simulation")


def _client_for(model_env_var: str) -> ModelClient:
    """WHAT: Builds a ModelClient from a named model environment variable.

    ARGS:
        model_env_var (str): e.g. "FIREWORKS_MODEL_SPECIALIST".

    RETURNS:
        ModelClient: Configured client for the model id in that variable.

    RAISES:
        ValueError: If the environment variable is unset.
    """
    model = os.environ.get(model_env_var, "")
    if not model:
        raise ValueError(f"{model_env_var} is not set (see .env.example).")
    return ModelClient(model=model)


def run_pipeline(product_brief: str, artifacts_root: Path) -> dict[str, Path]:
    """WHAT: Runs the full Research -> fan-out -> business pipeline.

    ARGS:
        product_brief (str): One-sentence hackathon demo prompt.
        artifacts_root (Path): Root directory for all written artifacts.

    RETURNS:
        dict[str, Path]: Mapping of discipline name to its output file.

    RAISES:
        ModelUnavailableError: Propagated from any stage on hard failure;
            the pipeline stops rather than continuing with a gap.
    """
    research_client = _client_for("FIREWORKS_MODEL_RESEARCH")
    research_agent = SpecialistAgent("research", research_client, artifacts_root)
    research_spec = get_task_spec("research-problem-analysis-pass").replace(
        "{PRODUCT_BRIEF}", product_brief
    )
    research_path = research_agent.run(research_spec, product_brief)
    research_findings = research_path.read_text(encoding="utf-8")

    outputs: dict[str, Path] = {"research": research_path}

    specialist_client = _client_for("FIREWORKS_MODEL_SPECIALIST")

    def _dispatch(discipline: str) -> tuple[str, Path]:
        agent = SpecialistAgent(discipline, specialist_client, artifacts_root)
        spec = get_task_spec(f"{discipline}-specialist-pass").replace(
            "{PRODUCT_BRIEF}", product_brief
        )
        path = agent.run(spec, research_findings)
        return discipline, path

    with ThreadPoolExecutor(max_workers=len(PARALLEL_DISCIPLINES)) as pool:
        for discipline, path in pool.map(_dispatch, PARALLEL_DISCIPLINES):
            outputs[discipline] = path

    combined_upstream = "\n\n".join(
        outputs[d].read_text(encoding="utf-8") for d in PARALLEL_DISCIPLINES
    )
    business_agent = SpecialistAgent("business", specialist_client, artifacts_root)
    business_spec = get_task_spec("cost-business-legal-pass").replace(
        "{PRODUCT_BRIEF}", product_brief
    )
    outputs["business"] = business_agent.run(business_spec, combined_upstream)

    return outputs
