from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    comparison_id: str
    subject_a: str
    subject_b: str
    summary: str
    differences: tuple[str, ...]
    created_at: str
    comparison_json_path: Path

