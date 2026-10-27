"""HTTP entry point for the boilerplate."""

from fastapi import FastAPI

from . import __version__
from .config import settings
from .models import CreateRunRequest, RunPlan
from .workflow import plan_run

app = FastAPI(title=settings.code_agent_name, version=__version__)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "environment": settings.code_agent_env, "version": __version__}


@app.post("/v1/runs", response_model=RunPlan, status_code=201)
def create_run(request: CreateRunRequest) -> RunPlan:
    return plan_run(request)
