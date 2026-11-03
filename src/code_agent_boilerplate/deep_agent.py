"""Deep Agents runtime backed by AWS Bedrock and an isolated sandbox."""

from __future__ import annotations

from uuid import uuid4

from .config import Settings
from .models import DeepAgentRunRequest, DeepAgentRunResponse
from .sandbox import create_sandbox

_WRITE_APPROVALS = {
    "write_file": True,
    "edit_file": True,
    "delete_file": True,
}

SYSTEM_PROMPT = """You are a careful code agent working in an isolated sandbox.
Only inspect and modify files within the workspace. Respect the repository's
allowed edit paths. Never seek, reveal, or create credentials. Explain your
plan before requesting a write; all writes require human approval. Do not push,
merge, deploy, or create pull requests."""


class DeepAgentUnavailable(RuntimeError):
    """Raised when optional Deep Agents dependencies are not installed."""


def _build_agent(settings: Settings, workspace: str):
    """Create a Bedrock Deep Agent lazily so planning works without AWS SDK setup."""
    try:
        from deepagents import create_deep_agent
        from deepagents.backends import FilesystemBackend
        from langchain_aws import ChatBedrockConverse
        from langgraph.checkpoint.memory import MemorySaver
    except ImportError as exc:  # pragma: no cover - depends on optional runtime install
        raise DeepAgentUnavailable(
            "Install the project's dependencies before executing a Deep Agent run."
        ) from exc

    model = ChatBedrockConverse(model_id=settings.deep_agent_model_id, region_name=settings.aws_region)
    return create_deep_agent(
        model=model,
        backend=FilesystemBackend(root_dir=workspace, virtual_mode=True),
        system_prompt=SYSTEM_PROMPT,
        interrupt_on=_WRITE_APPROVALS,
        checkpointer=MemorySaver(),
    )


def run_deep_agent(request: DeepAgentRunRequest, settings: Settings) -> DeepAgentRunResponse:
    """Stage a repo and optionally invoke Bedrock through Deep Agents.

    ``execute=False`` is deliberately the default: it lets callers validate
    contracts and sandbox boundaries before granting a live model invocation.
    """
    if not settings.deep_agent_enabled:
        raise DeepAgentUnavailable("Deep Agent execution is disabled by configuration.")

    run_id = str(uuid4())
    workspace = create_sandbox(request.repository, settings)
    response = DeepAgentRunResponse(
        run_id=run_id,
        status="sandbox_ready",
        workspace=str(workspace),
        model=f"bedrock:{settings.deep_agent_model_id}",
        approval_required_for=["write_file", "edit_file", "delete_file", "branch", "push", "draft_pr"],
    )
    if not request.execute:
        return response

    agent = _build_agent(settings, str(workspace))
    result = agent.invoke(
        {"messages": [{"role": "user", "content": request.request}]},
        config={"configurable": {"thread_id": run_id}},
    )
    messages = result.get("messages", []) if isinstance(result, dict) else []
    response.status = "awaiting_approval_or_complete"
    response.output = str(messages[-1].content) if messages else ""
    return response
