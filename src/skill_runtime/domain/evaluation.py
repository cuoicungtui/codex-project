from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class EvaluationIssue:
    code: str
    message: str
    evidence: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    run_id: str
    skill_id: str
    skill_version_id: str
    verdict: str
    score: float
    issues: tuple[EvaluationIssue, ...]
    metrics: dict[str, object]
    created_at: str
    eval_json_path: Path

