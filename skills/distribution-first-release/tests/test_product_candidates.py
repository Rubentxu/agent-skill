from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "product_candidates.py"
spec = importlib.util.spec_from_file_location("product_candidates", SCRIPT)
tool = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = tool
spec.loader.exec_module(tool)


class ProductDiscoveryTests(unittest.TestCase):
    def test_multimodule_and_ignored_noise(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "pom.xml").write_text("<project><artifactId>root</artifactId><packaging>pom</packaging></project>")
            lib = root / "lib"
            lib.mkdir()
            (lib / "pom.xml").write_text("<project><artifactId>public-sdk</artifactId></project>")
            (root / "tests").mkdir()
            (root / "tests" / "package.json").write_text('{"name":"test-only","bin":"x"}')
            (root / "private").mkdir()
            (root / "private" / "package.json").write_text('{"name":"internal","private":true,"main":"index.js"}')
            result = tool.discover(root)
            self.assertEqual([(p["name"], p["kind"]) for p in result["products"]],
                             [("root", "library"), ("public-sdk", "library")])
            self.assertEqual(result["status"], "CANDIDATES_ONLY_NOT_CERTIFIED")

    def test_gradle_publish_and_application(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "build.gradle.kts").write_text('plugins { id("maven-publish"); id("java-library") }')
            names = [x["kind"] for x in tool.discover(root)["products"]]
            self.assertEqual(names, ["library"])

    def test_cargo_publish_false_and_default_bin(self):
        if tool.tomllib is None:
            self.skipTest("tomllib not installed")
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "Cargo.toml").write_text('[package]\nname="hidden"\nversion="0.1.0"\npublish=false\n')
            self.assertEqual(tool.discover(root)["products"], [])
            (root / "Cargo.toml").write_text('[package]\nname="tool"\nversion="0.1.0"\n')
            (root / "src").mkdir()
            (root / "src" / "main.rs").write_text('fn main() {}')
            self.assertEqual(tool.discover(root)["products"][0]["kind"], "cli")

    def test_python_and_docker_are_unconfirmed(self):
        if tool.tomllib is None:
            self.skipTest("tomllib not installed")
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "pyproject.toml").write_text('[build-system]\nrequires=["setuptools"]\n[project]\nname="alpha"\nversion="0.1"\n[project.scripts]\nhello="alpha:main"\n')
            (root / "Dockerfile").write_text("FROM scratch\n")
            items = tool.discover(root)["products"]
            self.assertEqual({p["kind"] for p in items}, {"cli", "container"})
            self.assertTrue(all(p["channel"] is None and not p["consumer_verified"] for p in items))

    def test_symlink_does_not_get_read(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "Dockerfile").symlink_to("/etc/passwd")
            result = tool.discover(root)
            self.assertEqual(result["products"], [])
            self.assertTrue(result["warnings"])

    def test_cli_read_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "package.json").write_text('{"name":"lib","exports":"./index.js"}')
            result = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(root)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["products"][0]["kind"], "library")
            self.assertEqual(sorted(p.name for p in root.iterdir()), ["package.json"])


if __name__ == "__main__":
    unittest.main()
