from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skill_runtime.application.bootstrap_workspace import WorkspaceBootstrapper
from skill_runtime.application.revise_skill import SkillReviser
from skill_runtime.application.version_skill import SkillVersioner
from skill_runtime.domain.runs import RuntimeModelConfig


class FakeRevisionModel:
    def generate(self, *, system_prompt: str, user_prompt: str, config: RuntimeModelConfig) -> str:
        return """---
name: echo-skill
description: Revised echo skill with tighter instructions.
---

# Revised Echo Skill

Return a concise response in one sentence.
"""


class ReviseSkillTests(unittest.TestCase):
    def test_revise_creates_new_version(self) -> None:
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
            base = SkillVersioner(workspace).snapshot("echo-skill", version_id="v1")
            run_root = workspace / "runs" / "echo-skill" / "run-1"
            (run_root / "artifacts").mkdir(parents=True, exist_ok=True)
            (run_root / "run.json").write_text(
                json.dumps(
                    {
                        "run_id": "run-1",
                        "skill_id": "echo-skill",
                        "skill_version_id": base.version_id,
                        "status": "completed",
                    }
                ),
                encoding="utf-8",
            )
            (run_root / "eval.json").write_text(json.dumps({"issues": []}), encoding="utf-8")
            (run_root / "feedback.json").write_text(json.dumps({"recommendations": ["Be concise"]}), encoding="utf-8")

            result = SkillReviser(workspace, model_client=FakeRevisionModel()).revise(
                skill_id="echo-skill",
                run_id="run-1",
                model_config=RuntimeModelConfig(
                    provider="openai_compatible",
                    model="demo-model",
                    base_url="https://example.com/v1",
                    api_key="secret",
                    temperature=0.0,
                    max_tokens=64,
                    timeout_seconds=10,
                ),
            )

            self.assertTrue(result.package_root.is_dir())
            self.assertTrue((result.package_root / "SKILL.md").is_file())
            self.assertNotEqual(result.version_id, base.version_id)


if __name__ == "__main__":
    unittest.main()

