from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from agentskills_core import SkillRegistry
from agentskills_fs.local import LocalFileSystemSkillProvider

from skill_runtime.adapters.model_client_openai_compatible import OpenAICompatibleModelClient
from skill_runtime.application.runtime_config import load_runtime_model_config, load_workspace_settings
from skill_runtime.domain.runs import RunResult, RuntimeModelConfig
from skill_runtime.domain.workspace import WorkspaceContract
from skill_runtime.ports.model_client import ModelClient


def generate_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]


class JsonlTraceWriter:
    def __init__(self, path: Path, run_id: str) -> None:
        self._path = path
        self._run_id = run_id
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: str, payload: dict[str, object]) -> None:
        entry = {
            "schema_version": 1,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "run_id": self._run_id,
            "event": event,
            "payload": payload,
        }
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False))
            handle.write("\n")


class RunExecutor:
    def __init__(
        self,
        workspace_root: Path,
        model_client: ModelClient | None = None,
    ) -> None:
        self._workspace = WorkspaceContract(workspace_root)
        self._model_client = model_client or OpenAICompatibleModelClient()

    def execute(
        self,
        *,
        skill_id: str,
        version_id: str,
        input_text: str,
        run_id: str | None = None,
        model_config: RuntimeModelConfig | None = None,
    ) -> RunResult:
        config = model_config or load_runtime_model_config()
        effective_run_id = run_id or generate_run_id()
        run_root = self._workspace.runs_dir / skill_id / effective_run_id
        artifacts_dir = run_root / "artifacts"
        output_path = artifacts_dir / "output.md"
        output_html_path = artifacts_dir / "output.html"
        run_json_path = run_root / "run.json"
        trace_path = run_root / "trace.jsonl"

        run_root.mkdir(parents=True, exist_ok=False)
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        trace = JsonlTraceWriter(trace_path, effective_run_id)
        status = "running"
        started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        completed_at = started_at
        error_message: str | None = None

        run_record = {
            "schema_version": 1,
            "run_id": effective_run_id,
            "skill_id": skill_id,
            "skill_version_id": version_id,
            "status": status,
            "started_at": started_at,
            "completed_at": None,
            "workspace_root": str(self._workspace.root),
            "artifacts_dir": str(artifacts_dir),
            "trace_path": str(trace_path),
            "output_path": str(output_path),
            "output_html_path": None,
            "input": {"text": input_text},
            "model": config.public_dict(),
        }
        run_json_path.write_text(json.dumps(run_record, indent=2, ensure_ascii=False), encoding="utf-8")
        trace.append("run_started", {"skill_id": skill_id, "version_id": version_id})

        version_package_root = self._workspace.skills_dir / skill_id / "versions" / version_id / skill_id
        provider = LocalFileSystemSkillProvider(version_package_root.parent)
        registry = SkillRegistry()

        try:
            asyncio.run(registry.register(skill_id, provider))
            skill = registry.get_skill(skill_id)
            metadata = asyncio.run(skill.get_metadata())
            body = asyncio.run(skill.get_body())
            trace.append(
                "skill_loaded",
                {
                    "skill_id": skill_id,
                    "version_id": version_id,
                    "metadata_name": metadata.get("name", skill_id),
                },
            )
            system_prompt = "\n".join(
                [
                    f"You are executing skill {skill_id} version {version_id}.",
                    "Follow the skill instructions exactly.",
                    "Return a concise output that satisfies the task input.",
                    "Skill metadata:",
                    json.dumps(metadata, ensure_ascii=False, indent=2),
                    "Skill body:",
                    body,
                ]
            )
            user_prompt = f"Task input:\n{input_text}"
            trace.append(
                "model_request",
                {
                    "provider": config.provider,
                    "model": config.model,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                },
            )
            output_text = self._model_client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                config=config,
            )
            output_path.write_text(output_text + "\n", encoding="utf-8")
            if output_text.lstrip().startswith("<") or "<html" in output_text.lower():
                output_html_path.write_text(output_text + "\n", encoding="utf-8")
                run_record["output_html_path"] = str(output_html_path)
            trace.append(
                "model_response",
                {
                    "output_chars": len(output_text),
                    "output_preview": output_text[:500],
                },
            )
            status = "completed"
        except Exception as exc:  # pragma: no cover - smoke path still captures failure
            status = "failed"
            error_message = f"{type(exc).__name__}: {exc}"
            output_path.write_text(error_message + "\n", encoding="utf-8")
            trace.append("run_failed", {"error": error_message})
        finally:
            completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            run_record.update(
                {
                    "status": status,
                    "completed_at": completed_at,
                    "error_message": error_message,
                }
            )
            run_json_path.write_text(json.dumps(run_record, indent=2, ensure_ascii=False), encoding="utf-8")
            trace.append("run_finished", {"status": status})

        return RunResult(
            run_id=effective_run_id,
            run_root=run_root,
            run_json_path=run_json_path,
            trace_path=trace_path,
            artifacts_dir=artifacts_dir,
            output_path=output_path,
            output_html_path=output_html_path if output_html_path.exists() else None,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            error_message=error_message,
        )


def run_skill_from_env(
    *,
    skill_id: str,
    version_id: str,
    input_text: str,
    env: dict[str, str] | None = None,
) -> RunResult:
    settings = load_workspace_settings(env)
    model_config = load_runtime_model_config(env)
    return RunExecutor(settings.workspace_root).execute(
        skill_id=skill_id,
        version_id=version_id,
        input_text=input_text,
        model_config=model_config,
    )
