from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class WorkspaceContract:
    root: Path

    @property
    def skills_dir(self) -> Path:
        return self.root / "skills"

    @property
    def runs_dir(self) -> Path:
        return self.root / "runs"

    @property
    def datasets_dir(self) -> Path:
        return self.root / "datasets"

    @property
    def logs_dir(self) -> Path:
        return self.root / "logs"

    @property
    def reports_dir(self) -> Path:
        return self.root / "reports"

    @property
    def required_dirs(self) -> tuple[Path, ...]:
        return (
            self.skills_dir,
            self.runs_dir,
            self.datasets_dir,
            self.logs_dir,
            self.reports_dir,
        )

    def ensure_within_root(self, candidate: Path) -> Path:
        root = self.root.resolve()
        resolved = candidate.resolve()
        if resolved == root or root in resolved.parents:
            return resolved
        msg = f"Path escapes workspace root: {candidate}"
        raise ValueError(msg)

    def relative_to_root(self, candidate: Path) -> Path:
        return self.ensure_within_root(candidate).relative_to(self.root.resolve())
