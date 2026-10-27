from code_agent_boilerplate.models import CreateRunRequest, RunStage
from code_agent_boilerplate.workflow import plan_run


def test_plan_requires_human_gates() -> None:
    plan = plan_run(
        CreateRunRequest(
            repository={
                "id": "example-service",
                "url": "git@github.com:example-org/example-service.git",
                "allowed_edit_paths": ["src/", "tests/"],
            },
            request="Add a health endpoint.",
        )
    )

    assert plan.status == "planned"
    assert plan.next_stage is RunStage.ANALYSE
    assert RunStage.IMPLEMENT in plan.human_gates
