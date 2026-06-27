from __future__ import annotations

from pathlib import Path

from skill_runtime.domain.workspace import WorkspaceContract


class WorkspaceBootstrapper:
    def __init__(self, workspace_root: Path) -> None:
        self._contract = WorkspaceContract(workspace_root)

    @property
    def contract(self) -> WorkspaceContract:
        return self._contract

    def bootstrap(self) -> WorkspaceContract:
        self._contract.root.mkdir(parents=True, exist_ok=True)
        for directory in self._contract.required_dirs:
            directory.mkdir(parents=True, exist_ok=True)
        return self._contract
