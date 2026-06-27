from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skill_runtime.application.bootstrap_workspace import WorkspaceBootstrapper
from skill_runtime.application.compare_runs import RunComparator


class CompareRunsTests(unittest.TestCase):
    def test_compare_runs_writes_comparison_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            WorkspaceBootstrapper(workspace).bootstrap()
            for run_id, status in (("run-a", "failed"), ("run-b", "completed")):
                run_root = workspace / "runs" / "echo-skill" / run_id
                (run_root / "artifacts").mkdir(parents=True, exist_ok=True)
                (run_root / "run.json").write_text(
                    json.dumps(
                        {
                            "run_id": run_id,
                            "skill_id": "echo-skill",
                            "skill_version_id": "v1" if run_id == "run-a" else "v2",
                            "status": status,
                        }
                    ),
                    encoding="utf-8",
                )
                (run_root / "eval.json").write_text(
                    json.dumps(
                        {
                            "verdict": "fail" if run_id == "run-a" else "pass",
                            "score": 0.0 if run_id == "run-a" else 1.0,
                        }
                    ),
                    encoding="utf-8",
                )
                (run_root / "trace.jsonl").write_text(
                    json.dumps({"event": "run_started"}) + "\n" + json.dumps({"event": "run_finished"}) + "\n",
                    encoding="utf-8",
                )

            result = RunComparator(workspace).compare_runs(skill_id="echo-skill", run_id_a="run-a", run_id_b="run-b")
            self.assertTrue(result.comparison_json_path.is_file())
            self.assertGreater(len(result.differences), 0)


if __name__ == "__main__":
    unittest.main()

