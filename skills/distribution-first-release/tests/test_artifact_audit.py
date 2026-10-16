from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "artifact_audit.py"
spec = importlib.util.spec_from_file_location("artifact_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = audit
spec.loader.exec_module(audit)


class AssetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.name = "pipelinek-1.0.0.zip"
        with zipfile.ZipFile(self.root / self.name, "w") as z:
            z.writestr("pipelinek-1.0.0/bin/pipelinek", "#!/bin/sh\n")
            z.writestr("pipelinek-1.0.0/lib/app.jar", b"compiled")
        self.sbom = "pipelinek-1.0.0.sbom.json"
        (self.root / self.sbom).write_text("{}")
        self.allow = [self.name, "SHA256SUMS", self.sbom]
        self.write_checksums()

    def write_checksums(self):
        sha = audit.digest(self.root / self.name)
        (self.root / "SHA256SUMS").write_text(f"{sha}  {self.name}\n")

    def report(self, **kwargs):
        return audit.audit_directory(self.root, self.allow, self.name, **kwargs)

    def test_good_distribution_and_manifest(self):
        r = self.report()
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["observed"][self.name]["sha256"], audit.digest(self.root / self.name))

    def test_missing_product_not_success(self):
        (self.root / self.name).unlink()
        self.assertIn(f"MISSING_ASSET:{self.name}", self.report()["issues"])

    def test_missing_manifest(self):
        (self.root / "SHA256SUMS").unlink()
        self.assertFalse(self.report()["ok"])

    def test_missing_checksum_entry(self):
        (self.root / "SHA256SUMS").write_text("")
        r = self.report()
        self.assertIn(f"MISSING_CHECKSUM:{self.name}", r["issues"])

    def test_checksum_mismatch(self):
        (self.root / "SHA256SUMS").write_text("0" * 64 + "  " + self.name + "\n")
        self.assertIn(f"CHECKSUM_MISMATCH:{self.name}", self.report()["issues"])

    def test_duplicate_checksums(self):
        (self.root / "SHA256SUMS").write_text(
            (self.root / "SHA256SUMS").read_text() * 2
        )
        self.assertIn(f"DUPLICATE_CHECKSUM:{self.name}", self.report()["issues"])

    def test_extra_asset_detected(self):
        (self.root / "HANDOFF.md").write_text("internal")
        self.assertIn("UNEXPECTED_ASSET:HANDOFF.md", self.report()["issues"])

    def test_invalid_allowlist(self):
        r = audit.audit_directory(self.root, [self.name, self.name])
        self.assertIn("INVALID_ALLOWLIST", r["issues"])

    def test_no_launcher(self):
        with zipfile.ZipFile(self.root / self.name, "w") as z:
            z.writestr("pipelinek-1.0.0/lib/app.jar", "compiled")
        self.write_checksums()
        self.assertIn(f"NO_LAUNCHER:{self.name}", self.report()["issues"])

    def test_no_compiled_jars(self):
        with zipfile.ZipFile(self.root / self.name, "w") as z:
            z.writestr("pipelinek-1.0.0/bin/pipelinek", "script")
        self.write_checksums()
        self.assertIn(f"NO_COMPILED_JARS:{self.name}", self.report()["issues"])

    def test_source_leak_in_binary_zip(self):
        with zipfile.ZipFile(self.root / self.name, "a") as z:
            z.writestr("pipelinek-1.0.0/src/main/Main.kt", "sources")
        self.write_checksums()
        self.assertTrue(any(x.startswith("SOURCE_OR_INTERNAL_PATH:") for x in self.report()["issues"]))

    def test_zip_slip(self):
        with zipfile.ZipFile(self.root / self.name, "a") as z:
            z.writestr("../escape.txt", "danger")
        self.write_checksums()
        self.assertTrue(any(x.startswith("UNSAFE_ZIP_PATH:") for x in self.report()["issues"]))

    def test_truncated_zip(self):
        (self.root / self.name).write_bytes(b"not a zip")
        self.write_checksums()
        self.assertTrue(any(x.startswith("INVALID_ZIP:") for x in self.report()["issues"]))

    def test_empty_asset_refused(self):
        (self.root / self.sbom).write_text("")
        self.assertIn(f"EMPTY_ASSET:{self.sbom}", self.report()["issues"])

    def test_cli_on_valid_zip_is_read_only(self):
        cmd = [sys.executable, str(SCRIPT), "--dist-dir", str(self.root)]
        for n in self.allow:
            cmd.extend(["--allow", n])
        cmd.extend(["--runtime-zip", self.name])
        before = {x.name: x.stat().st_mtime_ns for x in self.root.iterdir()}
        run = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertTrue(json.loads(run.stdout)["ok"])
        self.assertEqual(before, {x.name: x.stat().st_mtime_ns for x in self.root.iterdir()})

    def test_fail_cli_exit_one(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "--dist-dir", str(self.root),
            "--allow", self.name, "--runtime-zip", self.name], capture_output=True, text=True)
        self.assertEqual(run.returncode, 1)
        self.assertFalse(json.loads(run.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
