from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class SkillIngestionResult:
    skill_id: str
    skill_root: Path
    metadata: dict[str, Any]
    body: str
    found_paths: tuple[str, ...]
    missing_paths: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SkillVersionSnapshot:
    skill_id: str
    version_id: str
    source_root: Path
    version_root: Path
    package_root: Path
    manifest_path: Path
    created_at: str
    content_hash: str

