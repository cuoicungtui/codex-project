from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class FeedbackResult:
    run_id: str
    skill_id: str
    skill_version_id: str
    summary: str
    recommendations: tuple[str, ...]
    evidence: tuple[str, ...]
    created_at: str
    feedback_json_path: Path

