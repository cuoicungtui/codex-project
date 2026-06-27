from __future__ import annotations

import asyncio
from pathlib import Path

from agentskills_core import SkillRegistry
from agentskills_fs.local import LocalFileSystemSkillProvider

from skill_runtime.application.runtime_config import load_workspace_settings
from skill_runtime.domain.skills import SkillIngestionResult
from skill_runtime.domain.workspace import WorkspaceContract


class SkillIngestor:
    def __init__(self, workspace_root: Path) -> None:
        self._workspace = WorkspaceContract(workspace_root)

    def ingest(self, skill_id: str) -> SkillIngestionResult:
        return asyncio.run(self._ingest(skill_id))

    async def _ingest(self, skill_id: str) -> SkillIngestionResult:
        provider = LocalFileSystemSkillProvider(self._workspace.skills_dir)
        registry = SkillRegistry()
        await registry.register(skill_id, provider)
        skill = registry.get_skill(skill_id)
        metadata = await skill.get_metadata()
        body = await skill.get_body()

        skill_root = self._workspace.skills_dir / skill_id
        present = []
        missing = []
        for relative in (
            "SKILL.md",
            "metadata.json",
            "rubric.json",
            "examples",
            "tests",
            "assets",
            "references",
            "scripts",
        ):
            target = skill_root / relative
            if target.exists():
                present.append(relative)
            else:
                missing.append(relative)

        return SkillIngestionResult(
            skill_id=skill_id,
            skill_root=skill_root,
            metadata=metadata,
            body=body,
            found_paths=tuple(present),
            missing_paths=tuple(missing),
        )


def ingest_skill_from_env(skill_id: str, env: dict[str, str] | None = None) -> SkillIngestionResult:
    settings = load_workspace_settings(env)
    return SkillIngestor(settings.workspace_root).ingest(skill_id)
