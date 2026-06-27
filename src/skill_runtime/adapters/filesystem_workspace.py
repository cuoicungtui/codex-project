from __future__ import annotations

from pathlib import Path

from skill_runtime.domain.workspace import WorkspaceContract


def resolve_workspace_contract(workspace_root: str | Path) -> WorkspaceContract:
    return WorkspaceContract(Path(workspace_root).expanduser())
