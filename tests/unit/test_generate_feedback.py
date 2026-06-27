from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skill_runtime.application.bootstrap_workspace import WorkspaceBootstrapper
from skill_runtime.application.generate_feedback import FeedbackGenerator
from skill_runtime.domain.runs import RuntimeModelConfig


class FakeFeedbackModel:
    def generate(self, *, system_prompt: str, user_prompt: str, config: RuntimeModelConfig) -> str:
        return "- Add explicit constraints\n- Trim unnecessary steps"


class GenerateFeedbackTests(unittest.TestCase):
    def test_generate_feedback_writes_feedback_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            WorkspaceBootstrapper(workspace).bootstrap()
            run_root = workspace / "runs" / "echo-skill" / "run-1"
            artifacts = run_root / "artifacts"
            artifacts.mkdir(parents=True, exist_ok=True)
            (run_root / "run.json").write_text(
                json.dumps(
                    {
                        "run_id": "run-1",
                        "skill_id": "echo-skill",
                        "skill_version_id": "v1",
                        "status": "completed",
                    }
                ),
                encoding="utf-8",
            )
            (run_root / "eval.json").write_text(
                json.dumps(
                    {
                        "issues": [
                            {
                                "code": "empty_output",
                                "message": "Run produced no usable output",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (run_root / "trace.jsonl").write_text(json.dumps({"event": "run_started"}) + "\n", encoding="utf-8")
            (artifacts / "output.md").write_text("output\n", encoding="utf-8")

            result = FeedbackGenerator(workspace, model_client=FakeFeedbackModel()).generate(
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

            self.assertTrue(result.feedback_json_path.is_file())
            feedback = json.loads(result.feedback_json_path.read_text(encoding="utf-8"))
            self.assertIn("Add explicit constraints", feedback["recommendations"][0])
            self.assertEqual(feedback["skill_id"], "echo-skill")


if __name__ == "__main__":
    unittest.main()

