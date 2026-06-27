from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RuntimeModelConfig:
    provider: str
    model: str
    base_url: str
    api_key: str
    temperature: float
    max_tokens: int
    timeout_seconds: int

    def public_dict(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass(frozen=True, slots=True)
class RunResult:
    run_id: str
    run_root: Path
    run_json_path: Path
    trace_path: Path
    artifacts_dir: Path
    output_path: Path
    output_html_path: Path | None
    status: str
    started_at: str
    completed_at: str
    error_message: str | None = None
