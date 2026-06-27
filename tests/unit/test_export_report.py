from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skill_runtime.application.bootstrap_workspace import WorkspaceBootstrapper
from skill_runtime.application.export_report import ReportExporter


class ExportReportTests(unittest.TestCase):
    def test_export_creates_json_and_html(self) -> None:
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
            (run_root / "trace.jsonl").write_text(
                json.dumps({"event": "run_started", "timestamp": "2026-06-27T00:00:00Z"}) + "\n",
                encoding="utf-8",
            )
            (run_root / "eval.json").write_text(json.dumps({"verdict": "pass", "score": 1.0, "issues": []}), encoding="utf-8")
            (run_root / "feedback.json").write_text(json.dumps({"recommendations": ["keep it short"]}), encoding="utf-8")
            (run_root / "artifacts" / "output.md").write_text("hello world\n", encoding="utf-8")

            result = ReportExporter(workspace).export_run_report(skill_id="echo-skill", run_id="run-1")

            self.assertTrue(result.report_json_path.is_file())
            self.assertTrue(result.report_html_path.is_file())
            report = json.loads(result.report_json_path.read_text(encoding="utf-8"))
            self.assertEqual(report["skill_id"], "echo-skill")

    def test_dashboard_index_lists_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            WorkspaceBootstrapper(workspace).bootstrap()
            run_root = workspace / "runs" / "echo-skill" / "run-1"
            (run_root / "artifacts").mkdir(parents=True, exist_ok=True)
            (run_root / "run.json").write_text(json.dumps({"run_id": "run-1", "skill_id": "echo-skill", "skill_version_id": "v1", "status": "completed"}), encoding="utf-8")
            (run_root / "trace.jsonl").write_text(json.dumps({"event": "run_started"}) + "\n", encoding="utf-8")
            (run_root / "eval.json").write_text(json.dumps({"verdict": "pass", "score": 1.0, "issues": []}), encoding="utf-8")
            (run_root / "feedback.json").write_text(json.dumps({"recommendations": ["keep it short"]}), encoding="utf-8")
            (run_root / "artifacts" / "output.md").write_text("hello world\n", encoding="utf-8")
            ReportExporter(workspace).export_run_report(skill_id="echo-skill", run_id="run-1")

            index = ReportExporter(workspace).build_dashboard_index()
            self.assertTrue(index.index_json_path.is_file())
            self.assertTrue(index.index_html_path.is_file())
            html_text = index.index_html_path.read_text(encoding="utf-8")
            self.assertIn("Total Runs", html_text)
            self.assertIn("Score Trend", html_text)
            self.assertIn("<svg", html_text)
            self.assertIn("Average Score", html_text)


if __name__ == "__main__":
    unittest.main()
