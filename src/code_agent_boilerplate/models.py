"""Public contracts for a safe code-agent run."""

from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class RunStage(StrEnum):
    ANALYSE = "analyse"
    EVALUATE = "evaluate"
    IMPLEMENT = "implement"
    TEST = "test"
    REVIEW = "review"
    DRAFT_PR = "draft_pr"


class RepositoryContract(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    url: str
    default_branch: str = "main"
    allowed_edit_paths: list[str] = Field(min_length=1)


class CreateRunRequest(BaseModel):
    repository: RepositoryContract
    request: str = Field(min_length=1, max_length=20_000)
    issue_url: str | None = None


class RunPlan(BaseModel):
    run_id: str
    status: str
    repository: str
    human_gates: list[RunStage]
    next_stage: RunStage
    safety_notes: list[str]
