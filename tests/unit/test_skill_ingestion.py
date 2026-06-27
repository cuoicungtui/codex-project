from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skill_runtime.application.bootstrap_workspace import WorkspaceBootstrapper
from skill_runtime.application.ingest_skill import SkillIngestor


class SkillIngestionTests(unittest.TestCase):
    def test_ingest_reads_skill_md_and_optional_file_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            WorkspaceBootstrapper(workspace).bootstrap()
            source_skill = workspace / "skills" / "echo-skill"
            source_skill.mkdir(parents=True, exist_ok=True)
            (source_skill / "SKILL.md").write_text(
                """---
name: echo-skill
description: Echo the task input back in a concise form.
---

# Echo Skill

Return a concise version of the user's input.
""",
                encoding="utf-8",
            )

            result = SkillIngestor(workspace).ingest("echo-skill")

            self.assertEqual(result.metadata["name"], "echo-skill")
            self.assertIn("SKILL.md", result.found_paths)
            self.assertIn("metadata.json", result.missing_paths)
            self.assertEqual(result.skill_root, source_skill)


if __name__ == "__main__":
    unittest.main()
