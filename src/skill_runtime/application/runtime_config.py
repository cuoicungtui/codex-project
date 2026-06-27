from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from skill_runtime.domain.runs import RuntimeModelConfig


@dataclass(frozen=True, slots=True)
class WorkspaceSettings:
    workspace_root: Path
    trace_level: str


def load_workspace_settings(env: Mapping[str, str] | None = None) -> WorkspaceSettings:
    source = env or os.environ
    root = Path(source.get("SKILL_RUNTIME_WORKSPACE_ROOT", ".")).expanduser()
    trace_level = source.get("SKILL_RUNTIME_TRACE_LEVEL", "standard")
    return WorkspaceSettings(workspace_root=root, trace_level=trace_level)


def load_runtime_model_config(env: Mapping[str, str] | None = None) -> RuntimeModelConfig:
    source = env or os.environ
    required = {
        "SMALL_LLM_PROVIDER": source.get("SMALL_LLM_PROVIDER", "").strip(),
        "SMALL_LLM_MODEL": source.get("SMALL_LLM_MODEL", "").strip(),
        "SMALL_LLM_BASE_URL": source.get("SMALL_LLM_BASE_URL", "").strip(),
        "SMALL_LLM_API_KEY": source.get("SMALL_LLM_API_KEY", "").strip(),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ValueError(f"Missing required runtime env vars: {', '.join(missing)}")

    return RuntimeModelConfig(
        provider=required["SMALL_LLM_PROVIDER"],
        model=required["SMALL_LLM_MODEL"],
        base_url=required["SMALL_LLM_BASE_URL"],
        api_key=required["SMALL_LLM_API_KEY"],
        temperature=float(source.get("SMALL_LLM_TEMPERATURE", "0.0")),
        max_tokens=int(source.get("SMALL_LLM_MAX_TOKENS", "4096")),
        timeout_seconds=int(source.get("SMALL_LLM_TIMEOUT_SECONDS", "120")),
        reasoning_effort=source.get("SMALL_LLM_REASONING_EFFORT", "").strip() or None,
    )
