from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from skill_runtime.domain.skills import SkillVersionSnapshot
from skill_runtime.domain.workspace import WorkspaceContract


def generate_version_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]


def _hash_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


class SkillVersioner:
    def __init__(self, workspace_root: Path) -> None:
        self._workspace = WorkspaceContract(workspace_root)

    def snapshot(self, skill_id: str, version_id: str | None = None) -> SkillVersionSnapshot:
        source_root = self._workspace.skills_dir / skill_id
        if not source_root.is_dir():
            raise FileNotFoundError(f"Skill root not found: {source_root}")

        effective_version_id = version_id or generate_version_id()
        version_root = source_root / "versions" / effective_version_id
        package_root = version_root / skill_id
        if version_root.exists():
            raise FileExistsError(f"Version already exists: {version_root}")

        version_root.mkdir(parents=True, exist_ok=False)
        package_root.parent.mkdir(parents=True, exist_ok=True)
        package_root.mkdir(parents=True, exist_ok=False)

        for item in source_root.iterdir():
            if item.name == "versions":
                continue
            destination = package_root / item.name
            if item.is_dir():
                shutil.copytree(item, destination)
            else:
                shutil.copy2(item, destination)

        created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        content_hash = _hash_tree(package_root)
        manifest = {
            "schema_version": 1,
            "skill_id": skill_id,
            "version_id": effective_version_id,
            "source_root": str(source_root),
            "package_root": str(package_root),
            "created_at": created_at,
            "content_hash": content_hash,
        }
        manifest_path = version_root / "version.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

        return SkillVersionSnapshot(
            skill_id=skill_id,
            version_id=effective_version_id,
            source_root=source_root,
            version_root=version_root,
            package_root=package_root,
            manifest_path=manifest_path,
            created_at=created_at,
            content_hash=content_hash,
        )
