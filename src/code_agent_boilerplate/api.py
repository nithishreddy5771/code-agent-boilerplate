"""HTTP entry point for the boilerplate."""

from fastapi import FastAPI

from . import __version__
from .config import settings
from .deep_agent import DeepAgentUnavailable, run_deep_agent
from .models import CreateRunRequest, DeepAgentRunRequest, DeepAgentRunResponse, RunPlan
from .workflow import plan_run

app = FastAPI(title=settings.code_agent_name, version=__version__)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "environment": settings.code_agent_env, "version": __version__}


@app.post("/v1/runs", response_model=RunPlan, status_code=201)
def create_run(request: CreateRunRequest) -> RunPlan:
    return plan_run(request)


@app.post("/v1/deep-agent/runs", response_model=DeepAgentRunResponse, status_code=201)
def create_deep_agent_run(request: DeepAgentRunRequest) -> DeepAgentRunResponse:
    """Create a sandboxed Deep Agent run; live Bedrock invocation is opt-in."""
    try:
        return run_deep_agent(request, settings)
    except (DeepAgentUnavailable, ValueError) as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc
