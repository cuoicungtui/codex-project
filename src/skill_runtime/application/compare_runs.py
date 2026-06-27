from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from skill_runtime.domain.comparison import ComparisonResult
from skill_runtime.domain.workspace import WorkspaceContract


def generate_comparison_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]


class RunComparator:
    def __init__(self, workspace_root: Path) -> None:
        self._workspace = WorkspaceContract(workspace_root)

    def compare_runs(self, *, skill_id: str, run_id_a: str, run_id_b: str) -> ComparisonResult:
        run_a = self._load_run(skill_id, run_id_a)
        run_b = self._load_run(skill_id, run_id_b)
        diffs: list[str] = []

        if run_a["status"] != run_b["status"]:
            diffs.append(f"status: {run_a['status']} -> {run_b['status']}")
        if run_a.get("skill_version_id") != run_b.get("skill_version_id"):
            diffs.append(f"skill_version_id: {run_a.get('skill_version_id')} -> {run_b.get('skill_version_id')}")

        eval_a = self._load_eval(skill_id, run_id_a)
        eval_b = self._load_eval(skill_id, run_id_b)
        if eval_a.get("verdict") != eval_b.get("verdict"):
            diffs.append(f"verdict: {eval_a.get('verdict')} -> {eval_b.get('verdict')}")
        if eval_a.get("score") != eval_b.get("score"):
            diffs.append(f"score: {eval_a.get('score')} -> {eval_b.get('score')}")

        trace_a_len = self._trace_len(skill_id, run_id_a)
        trace_b_len = self._trace_len(skill_id, run_id_b)
        if trace_a_len != trace_b_len:
            diffs.append(f"trace events: {trace_a_len} -> {trace_b_len}")

        summary = f"Compared runs {run_id_a} and {run_id_b} for {skill_id}"
        comparison_id = generate_comparison_id()
        created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        comparison_root = self._workspace.logs_dir / "comparisons"
        comparison_root.mkdir(parents=True, exist_ok=True)
        comparison_json_path = comparison_root / f"{comparison_id}.json"
        record = {
            "schema_version": 1,
            "comparison_id": comparison_id,
            "skill_id": skill_id,
            "subject_a": run_id_a,
            "subject_b": run_id_b,
            "differences": diffs,
            "created_at": created_at,
        }
        comparison_json_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        return ComparisonResult(
            comparison_id=comparison_id,
            subject_a=run_id_a,
            subject_b=run_id_b,
            summary=summary,
            differences=tuple(diffs),
            created_at=created_at,
            comparison_json_path=comparison_json_path,
        )

    def compare_versions(self, *, skill_id: str, version_a: str, version_b: str) -> ComparisonResult:
        version_root = self._workspace.skills_dir / skill_id / "versions"
        differences: list[str] = []
        package_a = version_root / version_a / skill_id / "SKILL.md"
        package_b = version_root / version_b / skill_id / "SKILL.md"
        body_a = package_a.read_text(encoding="utf-8")
        body_b = package_b.read_text(encoding="utf-8")
        if body_a != body_b:
            differences.append("SKILL.md content differs")
        summary = f"Compared versions {version_a} and {version_b} for {skill_id}"
        comparison_id = generate_comparison_id()
        created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        comparison_root = self._workspace.logs_dir / "comparisons"
        comparison_root.mkdir(parents=True, exist_ok=True)
        comparison_json_path = comparison_root / f"{comparison_id}.json"
        record = {
            "schema_version": 1,
            "comparison_id": comparison_id,
            "skill_id": skill_id,
            "subject_a": version_a,
            "subject_b": version_b,
            "differences": differences,
            "created_at": created_at,
        }
        comparison_json_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        return ComparisonResult(
            comparison_id=comparison_id,
            subject_a=version_a,
            subject_b=version_b,
            summary=summary,
            differences=tuple(differences),
            created_at=created_at,
            comparison_json_path=comparison_json_path,
        )

    def _load_run(self, skill_id: str, run_id: str) -> dict[str, object]:
        run_root = self._workspace.runs_dir / skill_id / run_id
        return json.loads((run_root / "run.json").read_text(encoding="utf-8"))

    def _load_eval(self, skill_id: str, run_id: str) -> dict[str, object]:
        run_root = self._workspace.runs_dir / skill_id / run_id
        return json.loads((run_root / "eval.json").read_text(encoding="utf-8"))

    def _trace_len(self, skill_id: str, run_id: str) -> int:
        run_root = self._workspace.runs_dir / skill_id / run_id
        trace_path = run_root / "trace.jsonl"
        return len([line for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()])

