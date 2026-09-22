#!/usr/bin/env python3
"""Inventario read-only de un checkout; no ejecuta scripts del repositorio.

Salida JSON: revisión Git si existe, manifest/workflows/docs por RUTA y
estadísticas indicativas de extensiones. No escanea contenido ni secretos;
no concluye conformidad y omite binarios, .git y caches conocidos.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
from typing import Optional

OMIT_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "target", "build",
    "dist", ".gradle", ".idea", ".next", "__pycache__", "vendor", ".tox",
}
MANIFESTS = {
    "pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts",
    "gradle.properties", "gradle.lockfile", "Cargo.toml", "Cargo.lock", "go.mod", "go.sum",
    "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "pyproject.toml",
    "poetry.lock", "uv.lock", "requirements.txt", "Pipfile.lock", "composer.json",
    "composer.lock", "Gemfile", "Gemfile.lock", "CMakeLists.txt", "Dockerfile",
    "Makefile", "AGENTS.md", "README.md", "CHANGELOG.md", "LICENSE", ".gitlab-ci.yml",
    "Jenkinsfile", "azure-pipelines.yml", "bitbucket-pipelines.yml", "tox.ini", "pytest.ini",
}
SUFFIXES = {
    ".java": "Java", ".kt": "Kotlin", ".kts": "Kotlin build/script", ".rs": "Rust",
    ".py": "Python", ".go": "Go", ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".cs": "C#", ".php": "PHP",
    ".c": "C", ".h": "C/C++", ".cpp": "C++", ".cc": "C++", ".hpp": "C++",
    ".rb": "Ruby", ".swift": "Swift", ".scala": "Scala", ".sh": "Shell",
}
MAX_FILES = 30000
MAX_PATHS = 180


def git(repo: Path, *args: str) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args], text=True, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, timeout=12, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def iter_paths(repo: Path):
    # No seguir symlinks; el explorador opera bajo la ruta resuelta inicialmente.
    for current, dirs, files in os.walk(repo, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in OMIT_DIRS and not (Path(current) / d).is_symlink())
        for filename in sorted(files):
            path = Path(current) / filename
            if not path.is_symlink():
                yield path.relative_to(repo).as_posix()


def is_interesting(rel: str) -> bool:
    path = Path(rel)
    if path.name in MANIFESTS or path.suffix in {".sln", ".csproj", ".slnx", ".tf"}:
        return True
    if rel.startswith((".github/workflows/", "docs/architecture/", "docs/adr/", "docs/decisions/")):
        return path.suffix.lower() in {".yml", ".yaml", ".md"}
    return False


def scan(repo: Path) -> dict:
    if not repo.is_dir():
        raise ValueError("--repo debe apuntar a un directorio accesible")
    counts: Counter[str] = Counter()
    interesting: list[str] = []
    count = 0
    truncated = False
    interesting_truncated = False
    for rel in iter_paths(repo):
        count += 1
        if count > MAX_FILES:
            truncated = True
            break
        counts[SUFFIXES.get(Path(rel).suffix, "otros")] += 1
        if is_interesting(rel):
            if len(interesting) < MAX_PATHS:
                interesting.append(rel)
            else:
                interesting_truncated = True
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(repo),
        "git": {
            "head": git(repo, "rev-parse", "HEAD"),
            "branch": git(repo, "branch", "--show-current"),
            "dirty": (
                None if (status := git(repo, "status", "--porcelain")) is None
                else bool(status)
            ),
        },
        "files_seen": min(count, MAX_FILES),
        "truncated_after_max_files": truncated,
        "interesting_paths": interesting,
        "interesting_paths_truncated": interesting_truncated,
        "indicative_file_counts": dict(sorted(counts.items())),
        "warning": "Inventario de nombres/rutas; no prueba ausencia de archivos, cumplimiento de reglas ni ejecución de tests o CI.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="raíz de código a inventariar")
    args = parser.parse_args()
    try:
        info = scan(args.repo.resolve(strict=True))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
