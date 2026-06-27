from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import yaml

from skill_runtime.adapters.model_client_openai_compatible import OpenAICompatibleModelClient
from skill_runtime.application.runtime_config import load_runtime_model_config
from skill_runtime.application.version_skill import SkillVersioner, generate_version_id
from skill_runtime.domain.runs import RuntimeModelConfig
from skill_runtime.domain.skills import SkillVersionSnapshot
from skill_runtime.domain.workspace import WorkspaceContract
from skill_runtime.ports.model_client import ModelClient


def generate_revision_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]


def _hash_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _compose_skill_md(original_skill_md: str, revised_text: str) -> str:
    from agentskills_core import split_frontmatter

    original_frontmatter, original_body = split_frontmatter(original_skill_md)
    revised_frontmatter, revised_body = split_frontmatter(revised_text)

    merged_frontmatter = dict(original_frontmatter)
    if revised_frontmatter:
        merged_frontmatter.update(revised_frontmatter)
    if "name" not in merged_frontmatter:
        merged_frontmatter["name"] = original_frontmatter.get("name")
    if "description" not in merged_frontmatter:
        merged_frontmatter["description"] = original_frontmatter.get("description")

    body = revised_body.strip() if revised_body.strip() else revised_text.strip()
    if not body:
        body = original_body.strip()

    frontmatter_yaml = yaml.safe_dump(merged_frontmatter, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{frontmatter_yaml}\n---\n\n{body.rstrip()}\n"


class SkillReviser:
    def __init__(
        self,
        workspace_root: Path,
        model_client: ModelClient | None = None,
    ) -> None:
        self._workspace = WorkspaceContract(workspace_root)
        self._model_client = model_client or OpenAICompatibleModelClient()

    def revise(
        self,
        *,
        skill_id: str,
        run_id: str,
        base_version_id: str | None = None,
        model_config: RuntimeModelConfig | None = None,
    ) -> SkillVersionSnapshot:
        config = model_config or load_runtime_model_config()
        run_root = self._workspace.runs_dir / skill_id / run_id
        run_record = json.loads((run_root / "run.json").read_text(encoding="utf-8"))
        eval_record = json.loads((run_root / "eval.json").read_text(encoding="utf-8"))
        feedback_record = json.loads((run_root / "feedback.json").read_text(encoding="utf-8"))
        source_version_id = base_version_id or str(run_record.get("skill_version_id"))
        source_version_root = self._workspace.skills_dir / skill_id / "versions" / source_version_id
        source_package_root = source_version_root / skill_id
        if not source_package_root.is_dir():
            raise FileNotFoundError(f"Source skill version not found: {source_package_root}")

        skill_body = (source_package_root / "SKILL.md").read_text(encoding="utf-8")
        system_prompt = "\n".join(
            [
                "You are revising a skill package based on run evidence and feedback.",
                "Preserve the Agent Skills format and keep the skill runnable by smaller models.",
                "Return a complete revised SKILL.md with YAML frontmatter and markdown body.",
            ]
        )
        user_prompt = json.dumps(
            {
                "skill_id": skill_id,
                "source_version_id": source_version_id,
                "skill_body": skill_body,
                "run": run_record,
                "evaluation": eval_record,
                "feedback": feedback_record,
            },
            ensure_ascii=False,
            indent=2,
        )
        revised_skill_md = self._model_client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            config=config,
        )
        revised_skill_md = _compose_skill_md(skill_body, revised_skill_md)

        revision_id = generate_revision_id()
        version_id = generate_version_id()
        version_root = self._workspace.skills_dir / skill_id / "versions" / version_id
        package_root = version_root / skill_id
        version_root.mkdir(parents=True, exist_ok=True)
        package_root.mkdir(parents=True, exist_ok=False)
        for item in source_package_root.iterdir():
            if item.name == "SKILL.md":
                continue
            destination = package_root / item.name
            if item.is_dir():
                shutil.copytree(item, destination)
            else:
                shutil.copy2(item, destination)

        (package_root / "SKILL.md").write_text(revised_skill_md.rstrip() + "\n", encoding="utf-8")
        content_hash = _hash_tree(package_root)
        manifest_path = version_root / "version.json"
        created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        manifest = {
            "schema_version": 1,
            "revision_id": revision_id,
            "skill_id": skill_id,
            "version_id": version_id,
            "source_version_id": source_version_id,
            "created_at": created_at,
            "reason": "revised from feedback.json and eval.json",
            "content_hash": content_hash,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        return SkillVersionSnapshot(
            skill_id=skill_id,
            version_id=version_id,
            source_root=self._workspace.skills_dir / skill_id,
            version_root=version_root,
            package_root=package_root,
            manifest_path=manifest_path,
            created_at=created_at,
            content_hash=content_hash,
        )
