from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from skill_runtime.adapters.model_client_openai_compatible import OpenAICompatibleModelClient
from skill_runtime.application.runtime_config import load_runtime_model_config
from skill_runtime.domain.feedback import FeedbackResult
from skill_runtime.domain.runs import RuntimeModelConfig
from skill_runtime.domain.workspace import WorkspaceContract
from skill_runtime.ports.model_client import ModelClient


class FeedbackGenerator:
    def __init__(
        self,
        workspace_root: Path,
        model_client: ModelClient | None = None,
    ) -> None:
        self._workspace = WorkspaceContract(workspace_root)
        self._model_client = model_client or OpenAICompatibleModelClient()

    def generate(
        self,
        *,
        skill_id: str,
        run_id: str,
        model_config: RuntimeModelConfig | None = None,
    ) -> FeedbackResult:
        config = model_config or load_runtime_model_config()
        run_root = self._workspace.runs_dir / skill_id / run_id
        run_record = json.loads((run_root / "run.json").read_text(encoding="utf-8"))
        eval_record = json.loads((run_root / "eval.json").read_text(encoding="utf-8"))
        trace_text = (run_root / "trace.jsonl").read_text(encoding="utf-8")
        output_text = (run_root / "artifacts" / "output.md").read_text(encoding="utf-8")

        system_prompt = "\n".join(
            [
                "You are reviewing a skill run and must write concrete feedback for the next skill revision.",
                "Focus on missing steps, extra steps, output quality, and context efficiency.",
                "Return concise, actionable bullets.",
            ]
        )
        user_prompt = json.dumps(
            {
                "run": run_record,
                "evaluation": eval_record,
                "trace": trace_text,
                "output": output_text,
            },
            ensure_ascii=False,
            indent=2,
        )
        raw_feedback = self._model_client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            config=config,
        )

        lines = [line.strip("- ").strip() for line in raw_feedback.splitlines() if line.strip()]
        recommendations = tuple(line for line in lines if line)
        if not recommendations:
            recommendations = (
                "Tighten the skill contract so the runtime can follow it with fewer assumptions.",
            )

        evidence = tuple(
            f"{issue.get('code')}: {issue.get('message')}"
            for issue in eval_record.get("issues", [])
        )
        summary = f"Feedback for run {run_id} on skill {skill_id}"
        created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        feedback_path = run_root / "feedback.json"
        feedback_record = {
            "schema_version": 1,
            "run_id": run_id,
            "skill_id": skill_id,
            "skill_version_id": run_record.get("skill_version_id"),
            "summary": summary,
            "recommendations": list(recommendations),
            "evidence": list(evidence),
            "raw_feedback": raw_feedback,
            "created_at": created_at,
        }
        feedback_path.write_text(json.dumps(feedback_record, indent=2, ensure_ascii=False), encoding="utf-8")
        return FeedbackResult(
            run_id=run_id,
            skill_id=skill_id,
            skill_version_id=str(run_record.get("skill_version_id", "")),
            summary=summary,
            recommendations=recommendations,
            evidence=evidence,
            created_at=created_at,
            feedback_json_path=feedback_path,
        )
