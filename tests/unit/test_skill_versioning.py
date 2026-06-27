from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skill_runtime.application.bootstrap_workspace import WorkspaceBootstrapper
from skill_runtime.application.version_skill import SkillVersioner


class SkillVersioningTests(unittest.TestCase):
    def test_snapshot_creates_versioned_copy(self) -> None:
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

            self.assertEqual(snapshot.version_id, "v1")
            self.assertTrue(snapshot.package_root.is_dir())
            self.assertTrue((snapshot.package_root / "SKILL.md").is_file())
            self.assertTrue(snapshot.manifest_path.is_file())


if __name__ == "__main__":
    unittest.main()
