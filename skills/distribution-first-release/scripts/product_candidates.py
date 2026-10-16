#!/usr/bin/env python3
"""Conservative, read-only product candidate inventory. Never publishes or builds."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

try:
    import tomllib
except ImportError:
    tomllib = None

SKIP = {
    ".git", ".gradle", ".idea", ".venv", "venv", "node_modules", "target",
    "build", "dist", "out", "vendor", "__pycache__", ".tox", ".pytest_cache",
    "test-harness", "tests", "test", "fixtures", "samples", "legacy", "old",
}
MANIFESTS = {"pom.xml", "build.gradle.kts", "build.gradle", "Cargo.toml", "package.json", "pyproject.toml", "Dockerfile"}
MAX_SIZE = 1024 * 1024
MAX_DEPTH = 8


def load_text(path: Path) -> str:
    if path.is_symlink() or path.stat().st_size > MAX_SIZE:
        raise ValueError("manifest symlink or too large")
    return path.read_text(encoding="utf-8")


def product(path: Path, kind: str, name: str, reason: str, confidence: str = "low") -> dict:
    return {
        "id": f"{path.as_posix()}::{kind}",
        "module": path.as_posix(),
        "kind": kind,
        "name": name,
        "status": "candidate_unconfirmed",
        "confidence": confidence,
        "evidence": reason,
        "channel": None,
        "consumer_verified": False,
    }


def inspect(directory: Path, relative: Path, names: set[str]) -> tuple[list[dict], list[str]]:
    result: list[dict] = []
    warnings: list[str] = []
    loc = relative.as_posix()
    for filename in sorted(names & MANIFESTS):
        file = directory / filename
        try:
            raw = load_text(file)
            if filename == "pom.xml":
                root = ElementTree.fromstring(raw)
                packaging = root.findtext("{*}packaging", default="jar")
                artifact = root.findtext("{*}artifactId") or directory.name
                if packaging == "pom":
                    continue  # Parent/aggregator, not a standalone JAR.
                kind = "plugin" if packaging == "maven-plugin" else "library"
                result.append(product(relative, kind, artifact, f"{loc}/pom.xml: packaging={packaging}"))
            elif filename in {"build.gradle", "build.gradle.kts"}:
                # Heuristic only: Gradle plugins and conventions may come from elsewhere.
                if re.search(r"\bmaven-publish\b", raw):
                    kind = "plugin" if ("java-gradle-plugin" in raw or "gradlePlugin {" in raw) else "library"
                    result.append(product(relative, kind, directory.name, f"{loc}/{filename}: maven-publish", "medium"))
                elif re.search(r"\bapplication\b", raw) or "application {" in raw:
                    result.append(product(relative, "application", directory.name, f"{loc}/{filename}: application plugin"))
            elif filename == "Cargo.toml":
                if tomllib is None:
                    warnings.append(f"{loc}/Cargo.toml: Python >=3.11 required for parsing")
                    continue
                data = tomllib.loads(raw)
                pkg = data.get("package", {})
                if not isinstance(pkg, dict) or not pkg or pkg.get("publish") is False or pkg.get("publish") == []:
                    continue
                kind = "cli" if "bin" in data or ("src/main.rs" in names) else "library"
                result.append(product(relative, kind, str(pkg.get("name", directory.name)), f"{loc}/Cargo.toml: publish allowed"))
            elif filename == "package.json":
                data = json.loads(raw)
                if not isinstance(data, dict) or data.get("private") is True or not data.get("name"):
                    continue
                if "bin" in data:
                    kind = "cli"
                elif any(k in data for k in ("exports", "main", "module", "types")):
                    kind = "library"
                else:
                    continue
                result.append(product(relative, kind, str(data["name"]), f"{loc}/package.json: entrypoints"))
            elif filename == "pyproject.toml":
                if tomllib is None:
                    warnings.append(f"{loc}/pyproject.toml: Python >=3.11 required for parsing")
                    continue
                data = tomllib.loads(raw)
                pkg = data.get("project", {})
                if not isinstance(pkg, dict) or not pkg.get("name") or "build-system" not in data:
                    continue
                kind = "cli" if pkg.get("scripts") or pkg.get("gui-scripts") else "library"
                result.append(product(relative, kind, str(pkg["name"]), f"{loc}/pyproject.toml: build-system/project"))
            elif filename == "Dockerfile":
                result.append(product(relative, "container", directory.name, f"{loc}/Dockerfile: build recipe (not proof of published image)"))
        except (OSError, UnicodeError, ValueError, ElementTree.ParseError, TypeError) as exc:
            warnings.append(f"{loc}/{filename}: {type(exc).__name__} while reading/parsing")
    return result, warnings


def discover(root: Path) -> dict:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("repository path is not a directory")
    candidates: list[dict] = []
    warnings: list[str] = []
    for current, dirs, files in os.walk(root, followlinks=False):
        here = Path(current)
        depth = len(here.relative_to(root).parts)
        dirs[:] = sorted(d for d in dirs if d not in SKIP and
                         not (here / d).is_symlink() and depth < MAX_DEPTH)
        names = set(files)
        rel = here.relative_to(root)
        found, errors = inspect(here, rel, names)
        candidates.extend(found)
        warnings.extend(errors)
    candidates.sort(key=lambda x: x["id"])
    return {
        "schema_version": 1,
        "scope": str(root),
        "status": "CANDIDATES_ONLY_NOT_CERTIFIED",
        "products": candidates,
        "warnings": warnings,
        "next": "Confirm ALL modules, compile/publish tasks, contractual artifacts and registry routes before any release",
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, required=True)
    args = p.parse_args()
    try:
        print(json.dumps(discover(args.repo), indent=2, ensure_ascii=False))
    except (OSError, ValueError) as exc:
        print(f"INVENTORY_FAILED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
