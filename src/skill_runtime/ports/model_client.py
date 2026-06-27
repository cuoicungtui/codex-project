from __future__ import annotations

from typing import Protocol

from skill_runtime.domain.runs import RuntimeModelConfig


class ModelClient(Protocol):
    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        config: RuntimeModelConfig,
    ) -> str: ...

