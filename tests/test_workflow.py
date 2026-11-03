from code_agent_boilerplate.config import Settings
from code_agent_boilerplate.models import CreateRunRequest, DeepAgentRunRequest, RunStage
from code_agent_boilerplate.sandbox import create_sandbox
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


def test_sandbox_copies_only_allowed_paths(tmp_path) -> None:
    source_root = tmp_path / "repositories"
    repository = source_root / "example-service"
    (repository / "src").mkdir(parents=True)
    (repository / "src" / "app.py").write_text("safe = True\n")
    (repository / ".env").write_text("TOP_SECRET=do-not-copy\n")
    (repository / "private.pem").write_text("do-not-copy\n")
    settings = Settings(
        sandbox_source_root=source_root,
        sandbox_work_root=tmp_path / "sandboxes",
    )
    request = DeepAgentRunRequest(
        repository={
            "id": "example-service",
            "url": "git@github.com:example-org/example-service.git",
            "allowed_edit_paths": ["src/"],
        },
        request="Inspect the application.",
    )

    workspace = create_sandbox(request.repository, settings)

    assert (workspace / "src" / "app.py").is_file()
    assert not (workspace / ".env").exists()
    assert not (workspace / "private.pem").exists()
