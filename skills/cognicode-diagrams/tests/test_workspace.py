"""Isolated workspace contract, including no-write-in-Git and hostile paths."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "workspace.py"
spec = importlib.util.spec_from_file_location("cognicode_diagrams_workspace", SCRIPT)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.home = self.base / "home"
        self.home.mkdir()
        self.repos = self.base / "projects"
        self.repos.mkdir()
        self.repo = self.repos / "pipelinek"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)

    def test_inspect_does_not_create_anything(self):
        result = module.inspect(self.repo, home=self.home)
        self.assertEqual(result["status"], "absent")
        self.assertFalse((self.home / ".cognicode-diagrams").exists())

    def test_init_uses_home_and_repo_name(self):
        result = module.init(self.repo, home=self.home)
        path = Path(result["workspace"])
        self.assertEqual(result["status"], "ready")
        self.assertTrue(path.is_relative_to(self.home / ".cognicode-diagrams" / "workspaces"))
        self.assertTrue(path.name.startswith("pipelinek--"))
        for folder in module.DIRECTORIES:
            self.assertTrue((path / folder).is_dir())
        self.assertEqual(json.loads((path / "workspace.json").read_text())["repository"]["path"], str(self.repo))

    def test_idempotent_and_no_repo_changes(self):
        one = module.init(self.repo, home=self.home)
        two = module.init(self.repo, home=self.home)
        self.assertEqual(one, two)
        status = subprocess.check_output(["git", "-C", str(self.repo), "status", "--porcelain"], text=True)
        self.assertEqual(status, "")
        self.assertEqual(list(self.repo.iterdir()), [self.repo / ".git"])

    def test_same_dir_name_different_projects_get_distinct_paths(self):
        other = self.base / "other" / "pipelinek"
        other.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(other)], check=True)
        a = module.init(self.repo, home=self.home)
        b = module.init(other, home=self.home)
        self.assertNotEqual(a["workspace"], b["workspace"])

    def test_root_is_explicit_without_git_auto_discovery(self):
        inner = self.repo / "src" / "nested"
        inner.mkdir(parents=True)
        self.assertEqual(module.init(self.repo, home=self.home)["repository"], str(self.repo))
        self.assertEqual(module.inspect(inner, home=self.home)["repository"], str(inner))

    def test_invalid_directory_rejected(self):
        with self.assertRaises(module.WorkspaceError):
            module.init(self.base / "does-not-exist", home=self.home)

    def test_workspace_never_calls_git(self):
        from unittest.mock import patch
        with patch.object(subprocess, "run", side_effect=AssertionError("Git forbidden")):
            result = module.init(self.repo, home=self.home)
        self.assertEqual(result["status"], "ready")

    def test_home_inside_git_checkout_rejected(self):
        nested_home = self.repo / "fake-home"
        nested_home.mkdir()
        with self.assertRaises(module.WorkspaceError):
            module.init(self.repo, home=nested_home)

    def test_symlinked_workspace_root_rejected(self):
        (self.home / ".cognicode-diagrams").symlink_to(self.repo, target_is_directory=True)
        with self.assertRaises(module.WorkspaceError):
            module.init(self.repo, home=self.home)

    def test_identity_collision_must_fail_closed(self):
        first = module.init(self.repo, home=self.home)
        manifest = Path(first["workspace"]) / "workspace.json"
        fake = json.loads(manifest.read_text())
        fake["repository"]["path"] = "/other-repo"
        manifest.write_text(json.dumps(fake))
        with self.assertRaises(module.WorkspaceError):
            module.init(self.repo, home=self.home)

    def test_init_lens_creates_only_requested_lens(self):
        module.init(self.repo, home=self.home)
        result = module.init_lens(self.repo, "vertical-slice", home=self.home)
        for subdir in module.LENS_DIRECTORIES:
            self.assertTrue((Path(result["lens_path"]) / subdir).is_dir())
        with self.assertRaises(module.WorkspaceError):
            module.init_lens(self.repo, "../bad", home=self.home)

    def test_path_rejects_escape(self):
        module.init(self.repo, home=self.home)
        for value in ("../out", "/tmp/absolute", "lenses/../../bad"):
            with self.subTest(value=value), self.assertRaises(module.WorkspaceError):
                module.target_path(self.repo, value, home=self.home)

    def test_path_rejects_symlink_escape(self):
        info = module.init(self.repo, home=self.home)
        (Path(info["workspace"]) / "danger").symlink_to(self.repo, target_is_directory=True)
        with self.assertRaises(module.WorkspaceError):
            module.target_path(self.repo, "danger/some-output.svg", home=self.home)

    def test_path_allows_regular_relative_output(self):
        info = module.init(self.repo, home=self.home)
        target = module.target_path(self.repo, "lenses/c4/sources/context.mmd", home=self.home)
        self.assertTrue(Path(target["path"]).is_relative_to(Path(info["workspace"])))


if __name__ == "__main__":
    unittest.main()
