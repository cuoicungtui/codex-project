from __future__ import annotations

import unittest

from skill_runtime.application.runtime_config import load_runtime_model_config


class RuntimeConfigTests(unittest.TestCase):
    def test_load_runtime_model_config_reads_env(self) -> None:
        env = {
            "SMALL_LLM_PROVIDER": "openai_compatible",
            "SMALL_LLM_MODEL": "demo-model",
            "SMALL_LLM_BASE_URL": "https://example.com/v1",
            "SMALL_LLM_API_KEY": "secret",
            "SMALL_LLM_TEMPERATURE": "0.1",
            "SMALL_LLM_MAX_TOKENS": "128",
            "SMALL_LLM_TIMEOUT_SECONDS": "10",
        }

        config = load_runtime_model_config(env)

        self.assertEqual(config.provider, "openai_compatible")
        self.assertEqual(config.model, "demo-model")
        self.assertEqual(config.max_tokens, 128)


if __name__ == "__main__":
    unittest.main()

