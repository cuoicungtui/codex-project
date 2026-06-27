from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from skill_runtime.domain.evaluation import EvaluationIssue, EvaluationResult
from skill_runtime.domain.workspace import WorkspaceContract


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_trace(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class RunEvaluator:
    def __init__(self, workspace_root: Path) -> None:
        self._workspace = WorkspaceContract(workspace_root)

    def evaluate(
        self,
        *,
        skill_id: str,
        run_id: str,
        required_output_contains: Iterable[str] = (),
        required_trace_events: Iterable[str] = (),
    ) -> EvaluationResult:
        run_root = self._workspace.runs_dir / skill_id / run_id
        run_json_path = run_root / "run.json"
        trace_path = run_root / "trace.jsonl"
        eval_json_path = run_root / "eval.json"
        output_path = run_root / "artifacts" / "output.md"

        run_record = _load_json(run_json_path)
        trace = _load_trace(trace_path)
        output_text = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
        rubric = self._load_rubric(
            skill_id=skill_id,
            version_id=str(run_record.get("skill_version_id", "")),
        )

        issues: list[EvaluationIssue] = []
        metrics: dict[str, object] = {
            "trace_event_count": len(trace),
            "output_char_count": len(output_text.strip()),
            "has_output": bool(output_text.strip()),
            "rubric_applied": bool(rubric),
        }

        if rubric:
            required_output_contains = tuple(required_output_contains) + tuple(rubric.get("required_output_contains", []))
            required_trace_events = tuple(required_trace_events) + tuple(rubric.get("required_trace_events", []))

        for event_name in required_trace_events:
            if not any(event.get("event") == event_name for event in trace):
                issues.append(
                    EvaluationIssue(
                        code="missing_trace_event",
                        message=f"Missing required trace event: {event_name}",
                        evidence=(f"trace.jsonl lacks event {event_name}",),
                    )
                )

        for token in required_output_contains:
            if token not in output_text:
                issues.append(
                    EvaluationIssue(
                        code="output_missing_expected_text",
                        message=f"Output does not contain required text: {token}",
                        evidence=(f"output.md missing {token!r}",),
                    )
                )

        if not output_text.strip():
            issues.append(
                EvaluationIssue(
                    code="empty_output",
                    message="Run produced no usable output",
                    evidence=("artifacts/output.md is empty",),
                )
            )

        if len(trace) < 4:
            issues.append(
                EvaluationIssue(
                    code="trace_too_short",
                    message="Trace is too short to audit execution",
                    evidence=(f"trace.jsonl has only {len(trace)} events",),
                )
            )

        if run_record.get("status") != "completed":
            issues.append(
                EvaluationIssue(
                    code="run_not_completed",
                    message=f"Run finished with status {run_record.get('status')}",
                    evidence=(f"run.json status={run_record.get('status')}",),
                )
            )

        verdict = "pass" if not issues else "fail"
        score = 1.0 if verdict == "pass" else max(0.0, 1.0 - (len(issues) * 0.25))
        created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        eval_record = {
            "schema_version": 1,
            "run_id": run_id,
            "skill_id": skill_id,
            "skill_version_id": run_record.get("skill_version_id"),
            "verdict": verdict,
            "score": score,
            "metrics": metrics,
            "issues": [
                {
                    "code": issue.code,
                    "message": issue.message,
                    "evidence": list(issue.evidence),
                }
                for issue in issues
            ],
            "created_at": created_at,
        }
        eval_json_path.write_text(json.dumps(eval_record, indent=2, ensure_ascii=False), encoding="utf-8")
        return EvaluationResult(
            run_id=run_id,
            skill_id=skill_id,
            skill_version_id=str(run_record.get("skill_version_id", "")),
            verdict=verdict,
            score=score,
            issues=tuple(issues),
            metrics=metrics,
            created_at=created_at,
            eval_json_path=eval_json_path,
        )

    def _load_rubric(self, *, skill_id: str, version_id: str) -> dict[str, object]:
        if not version_id:
            return {}
        rubric_path = (
            self._workspace.skills_dir / skill_id / "versions" / version_id / skill_id / "rubric.json"
        )
        if not rubric_path.is_file():
            return {}
        return json.loads(rubric_path.read_text(encoding="utf-8"))
