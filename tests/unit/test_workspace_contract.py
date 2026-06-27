from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skill_runtime.application.bootstrap_workspace import WorkspaceBootstrapper
from skill_runtime.domain.workspace import WorkspaceContract


class WorkspaceContractTests(unittest.TestCase):
    def test_bootstrap_creates_required_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace"
            contract = WorkspaceBootstrapper(root).bootstrap()

            self.assertTrue(contract.root.exists())
            self.assertEqual(
                {path.name for path in contract.required_dirs},
                {"skills", "runs", "datasets", "logs", "reports"},
            )
            for directory in contract.required_dirs:
                self.assertTrue(directory.is_dir(), directory)

    def test_bootstrap_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace"
            bootstrapper = WorkspaceBootstrapper(root)

            first = bootstrapper.bootstrap()
            sentinel = first.skills_dir / "keep.txt"
            sentinel.write_text("ok", encoding="utf-8")

            second = bootstrapper.bootstrap()

            self.assertEqual(sentinel.read_text(encoding="utf-8"), "ok")
            self.assertTrue(second.skills_dir.is_dir())

    def test_path_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace"
            contract = WorkspaceContract(root)
            outside = root.parent / "outside"

            with self.assertRaises(ValueError):
                contract.ensure_within_root(outside)


if __name__ == "__main__":
    unittest.main()
