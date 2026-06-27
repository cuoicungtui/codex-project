from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skill_runtime.application.bootstrap_workspace import WorkspaceBootstrapper
from skill_runtime.application.run_skill import RunExecutor
from skill_runtime.application.version_skill import SkillVersioner
from skill_runtime.domain.runs import RuntimeModelConfig


class FakeModelClient:
    def generate(self, *, system_prompt: str, user_prompt: str, config: RuntimeModelConfig) -> str:
        return f"FAKE::{user_prompt}"


class RunExecutionTests(unittest.TestCase):
    def test_run_writes_run_trace_and_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            WorkspaceBootstrapper(workspace).bootstrap()
            skill_root = workspace / "skills" / "echo-skill"
            skill_root.mkdir(parents=True, exist_ok=True)
            (skill_root / "SKILL.md").write_text(
                """---
name: echo-skill
description: Echo the task input back in a concise form.
---

# Echo Skill
""",
                encoding="utf-8",
            )
            snapshot = SkillVersioner(workspace).snapshot("echo-skill", version_id="v1")
            config = RuntimeModelConfig(
                provider="openai_compatible",
                model="demo-model",
                base_url="https://example.com/v1",
                api_key="secret",
                temperature=0.0,
                max_tokens=64,
                timeout_seconds=10,
            )

            result = RunExecutor(workspace, model_client=FakeModelClient()).execute(
                skill_id="echo-skill",
                version_id=snapshot.version_id,
                input_text="hello world",
                run_id="run-1",
                model_config=config,
            )

            self.assertEqual(result.status, "completed")
            self.assertTrue(result.run_json_path.is_file())
            self.assertTrue(result.trace_path.is_file())
            self.assertTrue(result.output_path.is_file())
            self.assertIn("hello world", result.output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
