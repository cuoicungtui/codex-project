from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RunReport:
    report_id: str
    skill_id: str
    run_id: str
    report_root: Path
    report_json_path: Path
    report_html_path: Path
    created_at: str


@dataclass(frozen=True, slots=True)
class DashboardIndex:
    dashboard_root: Path
    index_json_path: Path
    index_html_path: Path
    created_at: str

