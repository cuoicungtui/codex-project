from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from skill_runtime.application.bootstrap_workspace import WorkspaceBootstrapper
from skill_runtime.application.run_skill import RunExecutor
from skill_runtime.application.runtime_config import load_runtime_model_config
from skill_runtime.application.version_skill import SkillVersioner


class LiveModelSmokeTests(unittest.TestCase):
    def test_live_model_smoke(self) -> None:
        required_env = [
            "SMALL_LLM_PROVIDER",
            "SMALL_LLM_MODEL",
            "SMALL_LLM_BASE_URL",
            "SMALL_LLM_API_KEY",
        ]
        if os.environ.get("SKILL_RUNTIME_LIVE_SMOKE") != "1":
            self.skipTest("Live smoke is opt-in via SKILL_RUNTIME_LIVE_SMOKE=1")
        if any(not os.environ.get(name) for name in required_env):
            self.skipTest("Runtime model env is not configured")

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

Return a concise response.
""",
                encoding="utf-8",
            )
            snapshot = SkillVersioner(workspace).snapshot("echo-skill", version_id="live-smoke")
            config = load_runtime_model_config()
            result = RunExecutor(workspace).execute(
                skill_id="echo-skill",
                version_id=snapshot.version_id,
                input_text="say hello in one sentence",
                run_id="live-smoke-run",
                model_config=config,
            )
            self.assertEqual(result.status, "completed", msg=result.error_message)
            self.assertTrue(result.output_path.read_text(encoding="utf-8").strip())


if __name__ == "__main__":
    unittest.main()
