"""Pruebas aisladas: la utilidad solo devuelve metadatos, nunca contenido."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "context_inventory.py"
spec = importlib.util.spec_from_file_location("context_inventory", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ContextInventoryTests(unittest.TestCase):
    def test_inventory_readonly_does_not_leak_source_contents(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "AGENTS.md").write_text("TEST_SECRET_SHOULD_NOT_LEAK", encoding="utf-8")
            (root / "main.rs").write_text("fn main() {}", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "malicious.js").write_text("irrelevant", encoding="utf-8")
            before = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") )
            report = mod.scan(root)
            after = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") )
            self.assertEqual(before, after)
            self.assertIn("AGENTS.md", report["interesting_paths"])
            self.assertEqual(report["indicative_file_counts"].get("Rust"), 1)
            self.assertNotIn("TEST_SECRET_SHOULD_NOT_LEAK", repr(report))
            self.assertNotIn("malicious.js", repr(report))
            self.assertIsNone(report["git"]["head"])

    def test_excludes_symlinks_and_reports_incomplete_when_truncated(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "src").mkdir()
            (root / "src" / "file.py").write_text("pass", encoding="utf-8")
            (root / "src" / "outside.py").symlink_to(root.parent)
            report = mod.scan(root)
            self.assertEqual(report["indicative_file_counts"].get("Python"), 1)
            self.assertFalse(report["truncated_after_max_files"])


if __name__ == "__main__":
    unittest.main()
