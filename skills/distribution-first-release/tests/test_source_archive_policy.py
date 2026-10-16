from __future__ import annotations

import io
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path


@unittest.skipUnless(shutil.which("git"), "git is required")
class ExportIgnoreTests(unittest.TestCase):
    def test_source_archives_are_minimal_without_hiding_checkout(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            def git(*args):
                return subprocess.run(["git", *args], cwd=root, check=True,
                                      capture_output=True, text=False).stdout
            git("init", "-q")
            git("config", "user.name", "Skill Test")
            git("config", "user.email", "test@example.invalid")
            for name in ["docs/old.md", "test-harness/run.sh", "src/main.py", "LICENSE"]:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("fixture\n")
            (root / ".gitattributes").write_text(
                "docs/** export-ignore\n"
                "test-harness/** export-ignore\n"
            )
            git("add", ".")
            git("commit", "-qm", "sample")
            archive = git("archive", "--format=tar", "HEAD")
            with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
                files = {m.name for m in tar.getmembers() if m.isfile()}
            self.assertIn("src/main.py", files)
            self.assertIn("LICENSE", files)
            self.assertNotIn("docs/old.md", files)
            self.assertNotIn("test-harness/run.sh", files)
            self.assertTrue((root / "docs/old.md").exists())
            self.assertTrue((root / "test-harness/run.sh").exists())


if __name__ == "__main__":
    unittest.main()
