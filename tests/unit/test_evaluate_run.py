from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skill_runtime.application.bootstrap_workspace import WorkspaceBootstrapper
from skill_runtime.application.evaluate_run import RunEvaluator


class EvaluateRunTests(unittest.TestCase):
    def test_evaluate_passes_when_output_and_trace_are_present(self) -> None:
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
            (run_root / "trace.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps({"event": "run_started"}),
                        json.dumps({"event": "skill_loaded"}),
                        json.dumps({"event": "model_request"}),
                        json.dumps({"event": "model_response"}),
                        json.dumps({"event": "run_finished"}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (artifacts / "output.md").write_text("hello world\n", encoding="utf-8")

            result = RunEvaluator(workspace).evaluate(
                skill_id="echo-skill",
                run_id="run-1",
                required_trace_events=("model_response",),
                required_output_contains=("hello",),
            )

            self.assertEqual(result.verdict, "pass")
            self.assertEqual(result.issues, ())
            self.assertTrue(result.eval_json_path.is_file())

    def test_evaluate_reports_concrete_defects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            WorkspaceBootstrapper(workspace).bootstrap()
            run_root = workspace / "runs" / "echo-skill" / "run-2"
            artifacts = run_root / "artifacts"
            artifacts.mkdir(parents=True, exist_ok=True)
            (run_root / "run.json").write_text(
                json.dumps(
                    {
                        "run_id": "run-2",
                        "skill_id": "echo-skill",
                        "skill_version_id": "v1",
                        "status": "failed",
                    }
                ),
                encoding="utf-8",
            )
            (run_root / "trace.jsonl").write_text(json.dumps({"event": "run_started"}) + "\n", encoding="utf-8")
            (artifacts / "output.md").write_text("", encoding="utf-8")

            result = RunEvaluator(workspace).evaluate(skill_id="echo-skill", run_id="run-2")

            self.assertEqual(result.verdict, "fail")
            self.assertGreaterEqual(len(result.issues), 2)
            codes = {issue.code for issue in result.issues}
            self.assertIn("empty_output", codes)
            self.assertIn("trace_too_short", codes)


if __name__ == "__main__":
    unittest.main()

