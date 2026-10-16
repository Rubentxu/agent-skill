#!/usr/bin/env python3
"""Read-only local asset-set and JVM ZIP shape audit; NOT a release certifier."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

SHA_RE = re.compile(r"^([a-f0-9]{64}) [ *](.+)$")
ARCHIVE_EXT = (".zip", ".jar", ".war", ".tar.gz", ".tgz", ".exe", ".deb", ".rpm", ".dmg", ".msi", ".whl", ".nupkg")
FORBIDDEN = {".git", "src", "test", "tests", "evidence", "__pycache__", ".gradle", ".idea", ".worktrees"}
# Reject these as directory components inside an installable JVM distribution.
# Not every .jar with META-INF or legal docs is a source archive.


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inspect_jvm_zip(path: Path) -> list[str]:
    issues: list[str] = []
    try:
        with zipfile.ZipFile(path) as zf:
            entries = zf.infolist()
            if not entries:
                return [f"EMPTY_ZIP:{path.name}"]
            components = []
            for info in entries:
                n = info.filename
                parts = PurePosixPath(n).parts
                if n.startswith("/") or "\\" in n or ".." in parts or not parts:
                    issues.append(f"UNSAFE_ZIP_PATH:{n}")
                    continue
                filetype = stat.S_IFMT(info.external_attr >> 16)
                if filetype == stat.S_IFLNK:
                    issues.append(f"ZIP_SYMLINK:{n}")
                # Strip a single archive root directory (Gradle distZip convention).
                normalized = parts[1:] if len(parts) > 1 and all(
                    len(PurePosixPath(x.filename).parts) > 1 and
                    PurePosixPath(x.filename).parts[0] == parts[0] for x in entries
                ) else parts
                components.append(normalized)
                if any(p.lower() in FORBIDDEN for p in normalized):
                    issues.append(f"SOURCE_OR_INTERNAL_PATH:{n}")
                if n.endswith(("-sources.jar", "-tests.jar", ".class")) and "lib" not in normalized:
                    issues.append(f"UNEXPECTED_SOURCE_OR_CLASS:{n}")
            if not any(c and c[0] == "bin" and len(c) > 1 for c in components):
                issues.append(f"NO_LAUNCHER:{path.name}")
            if not any(c and c[0] == "lib" and len(c) > 1 and c[-1].endswith(".jar") for c in components):
                issues.append(f"NO_COMPILED_JARS:{path.name}")
    except (OSError, zipfile.BadZipFile, ValueError) as exc:
        issues.append(f"INVALID_ZIP:{path.name}:{type(exc).__name__}")
    return issues


def audit_directory(dist: Path, expected: list[str], jvm_zip: str | None = None) -> dict:
    issues: list[str] = []
    observed: dict[str, dict] = {}
    if not dist.is_dir():
        return {"ok": False, "issues": [f"MISSING_DIRECTORY:{dist}"], "observed": observed}
    if not expected or len(expected) != len(set(expected)) or any(
        not n or "/" in n or "\\" in n or n in (".", "..") for n in expected
    ):
        return {"ok": False, "issues": ["INVALID_ALLOWLIST"], "observed": observed}
    actual = {p.name for p in dist.iterdir()}
    for name in sorted(set(expected) - actual):
        issues.append(f"MISSING_ASSET:{name}")
    for name in sorted(actual - set(expected)):
        issues.append(f"UNEXPECTED_ASSET:{name}")
    for name in sorted(actual & set(expected)):
        p = dist / name
        if p.is_symlink() or not p.is_file():
            issues.append(f"NOT_REGULAR_FILE:{name}")
            continue
        observed[name] = {"size": p.stat().st_size, "sha256": digest(p)}
        if p.stat().st_size == 0:
            issues.append(f"EMPTY_ASSET:{name}")
    if jvm_zip:
        if jvm_zip not in expected:
            issues.append(f"UNLISTED_JVM_ZIP:{jvm_zip}")
        elif jvm_zip in observed:
            issues.extend(inspect_jvm_zip(dist / jvm_zip))
    sums = dist / "SHA256SUMS"
    if "SHA256SUMS" in expected and "SHA256SUMS" in observed:
        rows: dict[str, str] = {}
        for line in sums.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            m = SHA_RE.fullmatch(line)
            if not m:
                issues.append("INVALID_CHECKSUM_LINE")
                continue
            sha, source = m.groups()
            basename = PurePosixPath(source).name
            if basename in rows:
                issues.append(f"DUPLICATE_CHECKSUM:{basename}")
            rows[basename] = sha
        for name in sorted(rows):
            if name not in expected or name == "SHA256SUMS":
                issues.append(f"UNEXPECTED_CHECKSUM:{name}")
            elif name in observed and observed[name]["sha256"] != rows[name]:
                issues.append(f"CHECKSUM_MISMATCH:{name}")
        for name in expected:
            if name.lower().endswith(ARCHIVE_EXT) and name not in rows:
                issues.append(f"MISSING_CHECKSUM:{name}")
    return {"ok": not issues, "issues": sorted(issues), "observed": observed}


def tracked_distributions(git_root: Path, threshold_mib: int = 1) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-C", str(git_root), "ls-files", "-z"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError(f"cannot inspect git tracked files: {exc}") from exc
    issues = []
    for raw in out.split(b"\0"):
        if not raw:
            continue
        name = raw.decode("utf-8", errors="surrogateescape")
        p = git_root / name
        if p.is_file() and p.stat().st_size >= threshold_mib * 1024 * 1024 and (
            name.startswith(("evidence/", "docs/", "dist/", "build/", "artifacts/")) and
            name.lower().endswith(ARCHIVE_EXT)
        ):
            issues.append(f"TRACKED_GENERATED_ARTIFACT:{name}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, required=True)
    parser.add_argument("--allow", action="append", default=[], help="exact asset filename; repeat")
    parser.add_argument("--runtime-zip", help="JVM distribution ZIP; verifies bin/lib and internal paths")
    parser.add_argument("--git-root", type=Path, help="optionally inspect tracked generated archives")
    args = parser.parse_args()
    report = audit_directory(args.dist_dir, args.allow, args.runtime_zip)
    if args.git_root:
        try:
            report["issues"].extend(tracked_distributions(args.git_root))
        except ValueError as exc:
            report["issues"].append(f"GIT_INSPECTION_FAILED:{exc}")
        report["issues"].sort()
        report["ok"] = not report["issues"]
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
