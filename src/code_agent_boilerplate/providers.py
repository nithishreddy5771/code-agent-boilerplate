"""Interfaces your infrastructure adapters should implement."""

from typing import Protocol

from .models import RepositoryContract


class KnowledgeStore(Protocol):
    def context_for(self, repository: RepositoryContract, request: str) -> str: ...


class AgentRuntime(Protocol):
    def analyse(self, request: str, context: str) -> str: ...

    def implement(self, plan: str, repository: RepositoryContract) -> str: ...


class SourceControl(Protocol):
    def create_draft_pull_request(self, repository: RepositoryContract, branch: str) -> str: ...


class TestRunner(Protocol):
    def run(self, repository: RepositoryContract, changed_paths: list[str]) -> str: ...
