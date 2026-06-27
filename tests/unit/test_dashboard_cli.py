from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skill_runtime.application.bootstrap_workspace import WorkspaceBootstrapper
from skill_runtime.cli.main import main


class DashboardCliTests(unittest.TestCase):
    def test_export_report_and_dashboard_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            WorkspaceBootstrapper(workspace).bootstrap()
            run_root = workspace / "runs" / "echo-skill" / "run-1"
            (run_root / "artifacts").mkdir(parents=True, exist_ok=True)
            (run_root / "run.json").write_text(
                json.dumps(
                    {
                        "run_id": "run-1",
                        "skill_id": "echo-skill",
                        "skill_version_id": "v1",
                        "status": "completed",
                        "model": {"model": "demo"},
                    }
                ),
                encoding="utf-8",
            )
            (run_root / "trace.jsonl").write_text(json.dumps({"event": "run_started"}) + "\n", encoding="utf-8")
            (run_root / "eval.json").write_text(json.dumps({"verdict": "pass", "score": 1.0, "issues": []}), encoding="utf-8")
            (run_root / "feedback.json").write_text(json.dumps({"recommendations": ["keep it short"]}), encoding="utf-8")
            (run_root / "artifacts" / "output.md").write_text("hello world\n", encoding="utf-8")

            exit_code = main(["export-report", "--skill-id", "echo-skill", "--run-id", "run-1", "--workspace-root", str(workspace)])
            self.assertEqual(exit_code, 0)
            exit_code = main(["build-dashboard", "--workspace-root", str(workspace)])
            self.assertEqual(exit_code, 0)
            self.assertTrue((workspace / "reports" / "index.html").is_file())


if __name__ == "__main__":
    unittest.main()

