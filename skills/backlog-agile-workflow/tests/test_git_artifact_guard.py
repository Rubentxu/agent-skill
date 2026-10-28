"""Classification and optional Git-index probing; never untracks real files."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SRC = Path(__file__).resolve().parents[1] / "scripts/git_artifact_guard.py"
spec = importlib.util.spec_from_file_location("git_artifact_guard_skill", SRC)
guard = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = guard
spec.loader.exec_module(guard)


class ClassificationTests(unittest.TestCase):
    def test_managed_backlog_and_roadmap(self):
        for path in ("backlog/tasks/task-1 - Example.md", ".backlog/config.yml",
                     "backlog.config.yml", "ROADMAP.md", "docs/adr/ADR-31.md",
                     "docs/specs/SPEC-02.md", "docs/roadmaps/R4.md",
                     "plans/roadmap.md", "specifications/inputs.json"):
            with self.subTest(path=path):
                self.assertIsNotNone(guard.classify(path))

    def test_groma_architecture_is_private_in_consumer_repos(self):
        for path in ("groma/config.json", "groma/index.md", ".groma/systems/a.md",
                     "groma-export/index.html", "groma-bundle.zip", "docs/groma/config.json"):
            with self.subTest(path=path):
                self.assertIsNotNone(guard.classify(path))
        self.assertIsNone(guard.classify("skills/backlog-agile-workflow/references/groma-integration.md"))

    def test_archive_detection(self):
        for path in ("roadmap-backup.zip", "delivery-specs.zip", "ADR-bundle.tar.gz",
                     "project-plan-2026.7z", "docs/adr/snapshots.zip"):
            self.assertIsNotNone(guard.classify(path))
        for path in ("releases/application.zip", "dist/product.tar.gz",
                     "libs/source.zip", "docs/api-reference.md"):
            self.assertIsNone(guard.classify(path))

    def test_skill_distribution_not_consumer_private_docs(self):
        self.assertIsNone(guard.classify("skills/pure-functional-design/ADR-002.md"))
        self.assertIsNone(guard.classify("skills/backlog-agile-workflow/ROADMAP.md"))
        self.assertIsNone(guard.classify("tests/fixtures/example.rs"))

    def test_index_audit_does_not_infer_clean_history(self):
        result = guard.audit(["src/main.rs", "ROADMAP.md", "backlog/tasks/a.md"],
                             ["ROADMAP.md"])
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertEqual(len(result["tracked"]), 2)
        self.assertTrue(result["tracked"][0]["staged"] or result["tracked"][1]["staged"])
        self.assertEqual(result["removalArgv"][0][:4], ["git", "rm", "--cached", "--"])
        self.assertIn("history", " ".join(result["effects"]).lower())

    def test_no_extra_changes_when_clean(self):
        self.assertEqual(guard.audit(["src/app.rs", "releases/app.zip"])["status"], "CLEAR")

    def test_real_temp_git_index_read_only(self):
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run(["git", "init", "-q", folder], check=True)
            root = Path(folder)
            (root / "ROADMAP.md").write_text("# Private\n")
            (root / "src").mkdir()
            (root / "src/app.rs").write_text("fn main() {}\n")
            subprocess.run(["git", "-C", folder, "add", "ROADMAP.md", "src/app.rs"], check=True)
            tracked = guard._git_paths(folder, "ls-files", "-z", "--cached")
            result = guard.audit(tracked)
            self.assertEqual([x["path"] for x in result["tracked"]], ["ROADMAP.md"])
            # The files and Git index remain unchanged by the audit.
            self.assertTrue((root / "ROADMAP.md").exists())
            self.assertEqual(tracked, guard._git_paths(folder, "ls-files", "-z", "--cached"))


if __name__ == "__main__":
    unittest.main()
