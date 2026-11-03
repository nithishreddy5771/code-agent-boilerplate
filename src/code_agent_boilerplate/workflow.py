"""Human-gated workflow planning.

Provider calls are intentionally absent from the starter. Wire adapters into this
module only after deciding your authorization, sandbox, and approval policies.
"""

from uuid import uuid4

from .models import CreateRunRequest, RunPlan, RunStage

HUMAN_GATES = [RunStage.EVALUATE, RunStage.IMPLEMENT, RunStage.DRAFT_PR]


def plan_run(request: CreateRunRequest) -> RunPlan:
    return RunPlan(
        run_id=str(uuid4()),
        status="planned",
        repository=request.repository.id,
        human_gates=HUMAN_GATES,
        next_stage=RunStage.ANALYSE,
        safety_notes=[
            "Only edit paths listed in the repository contract.",
            "Require explicit approval before implementation and draft-PR creation.",
            "Keep credentials outside request payloads and source control.",
        ],
    )
