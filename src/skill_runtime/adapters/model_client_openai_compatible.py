from __future__ import annotations

from openai import OpenAI

from skill_runtime.domain.runs import RuntimeModelConfig


class OpenAICompatibleModelClient:
    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        config: RuntimeModelConfig,
    ) -> str:
        client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout_seconds,
        )
        response = client.chat.completions.create(
            model=config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
        content = response.choices[0].message.content or ""
        return content.strip()

