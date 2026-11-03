"""A small, conservative sandbox staging layer for Deep Agents.

The source repository is never mounted as the agent's writable root. Only
allowlisted paths are copied to a per-run workspace; secrets and bulky local
artifacts are excluded before the model receives filesystem tools.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from .config import Settings
from .models import RepositoryContract

_BLOCKED_NAMES = frozenset(
    {
        ".git",
        ".env",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "dist",
        "build",
    }
)
_BLOCKED_SUFFIXES = (".pem", ".key", ".p12", ".pfx")


class SandboxError(ValueError):
    """The requested repository contract cannot be safely staged."""


def _is_safe_member(path: Path) -> bool:
    return path.name not in _BLOCKED_NAMES and not path.name.endswith(_BLOCKED_SUFFIXES)


def _safe_relative_path(raw_path: str) -> Path:
    candidate = Path(raw_path.strip().rstrip("/"))
    if not raw_path.strip() or candidate.is_absolute() or ".." in candidate.parts:
        raise SandboxError(f"Invalid allowed edit path: {raw_path!r}")
    return candidate


def resolve_source_repository(contract: RepositoryContract, settings: Settings) -> Path:
    """Resolve a repository only below the configured source root."""
    root = settings.sandbox_source_root.expanduser().resolve()
    source = (root / contract.id).resolve()
    if source.parent != root or not source.is_dir():
        raise SandboxError(f"Repository {contract.id!r} is not available below SANDBOX_SOURCE_ROOT")
    return source


def create_sandbox(contract: RepositoryContract, settings: Settings) -> Path:
    """Copy only contract-approved content to an isolated per-run workspace."""
    source = resolve_source_repository(contract, settings)
    work_root = settings.sandbox_work_root.expanduser().resolve()
    destination = work_root / f"{contract.id}-{uuid4().hex}"
    destination.mkdir(parents=True, exist_ok=False)

    for allowed_path in contract.allowed_edit_paths:
        relative = _safe_relative_path(allowed_path)
        origin = (source / relative).resolve()
        if origin != source and source not in origin.parents:
            raise SandboxError(f"Path escapes repository: {allowed_path!r}")
        if not origin.exists() or not _is_safe_member(origin):
            continue
        target = destination / relative
        if origin.is_dir():
            shutil.copytree(
                origin,
                target,
                ignore=shutil.ignore_patterns(*_BLOCKED_NAMES, "*.pem", "*.key", "*.p12", "*.pfx"),
            )
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origin, target)

    return destination
