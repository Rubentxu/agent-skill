#!/usr/bin/env python3
"""Inspect/create isolated per-Git-worktree assets under ~/.cognicode-diagrams.

Never writes into the source Git worktree. Uses only standard library and
NO Git queries, repository file reads or architecture inference. Projectors use only derived assets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

SCHEMA_VERSION = 1
DIRECTORIES = ("evidence", "inputs", "lenses", "sessions", "exports")
LENS_DIRECTORIES = ("sources", "renders", "reports")
VALID_LENS = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z")


class WorkspaceError(ValueError):
    """Invalid repository, workspace or requested destination."""


def supplied_repository_root(path: Path) -> Path:
    """Use an explicit path as an opaque identity; never call Git or inspect files.

    Caller must provide the root, not an arbitrary nested directory.
    """
    if path.is_symlink():
        raise WorkspaceError("raíz de repositorio enlazada no permitida")
    try:
        root = path.expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise WorkspaceError(f"ruta de repositorio inválida: {exc}") from exc
    if not root.is_dir() or ".cognicode-diagrams" in root.parts:
        raise WorkspaceError("proporcione la raíz explícita, fuera del workspace derivado")
    return root


def _no_symlinks(path: Path) -> None:
    """Reject symlinks for any existing component of a workspace destination."""
    for component in (path, *path.parents):
        if component.is_symlink():
            raise WorkspaceError(f"ruta de workspace con enlace simbólico: {component}")


def workspace_path(repo: Path, *, home: Path | None = None) -> Path:
    repo = repo.resolve(strict=True)
    home_dir = (Path.home() if home is None else home).expanduser().resolve(strict=True)
    base = home_dir / ".cognicode-diagrams" / "workspaces"
    _no_symlinks(base)
    if base.is_relative_to(repo):
        raise WorkspaceError("HOME está dentro del repositorio: no se escribirá en Git")
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", repo.name).strip("._-")[:50] or "repo"
    digest = hashlib.sha256(os.fsencode(str(repo))).hexdigest()[:12]
    workspace = base / f"{slug}--{digest}"
    _no_symlinks(workspace)
    if workspace.is_relative_to(repo):
        raise WorkspaceError("el destino está dentro del repositorio")
    return workspace


def _manifest(repo: Path, workspace: Path) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "repository": {"name": repo.name, "path": str(repo)},
        "workspace": str(workspace),
    }


def _status(repo: Path, workspace: Path) -> str:
    _no_symlinks(workspace)
    if not workspace.exists():
        return "absent"
    if not workspace.is_dir():
        return "invalid"
    manifest_path = workspace / "workspace.json"
    _no_symlinks(manifest_path)
    if not manifest_path.is_file():
        return "invalid"
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "invalid"
    if data != _manifest(repo, workspace):
        return "invalid"
    for subdir in DIRECTORIES:
        target = workspace / subdir
        _no_symlinks(target)
        if not target.is_dir():
            return "incomplete"
    return "ready"


def inspect(repo_dir: Path, *, home: Path | None = None) -> dict:
    repo = supplied_repository_root(repo_dir)
    path = workspace_path(repo, home=home)
    return {"repository": str(repo), "workspace": str(path), "status": _status(repo, path)}


def _mkdir_secure(path: Path) -> None:
    _no_symlinks(path)
    path.mkdir(parents=True, exist_ok=True)
    _no_symlinks(path)
    if not path.is_dir():
        raise WorkspaceError(f"no es directorio: {path}")


def init(repo_dir: Path, *, home: Path | None = None) -> dict:
    info = inspect(repo_dir, home=home)
    status = info["status"]
    if status == "invalid":
        raise WorkspaceError("workspace existente con identidad incorrecta o contenido inesperado")
    repo = Path(info["repository"])
    target = Path(info["workspace"])
    _mkdir_secure(target)
    manifest = target / "workspace.json"
    _no_symlinks(manifest)
    if status == "absent":
        # Exclusive create: never replace a preexisting file.
        try:
            with manifest.open("x", encoding="utf-8") as handle:
                json.dump(_manifest(repo, target), handle, ensure_ascii=False, indent=2)
                handle.write("\n")
        except FileExistsError as exc:
            raise WorkspaceError("workspace inicializado concurrentemente; revisar antes de reutilizar") from exc
    for subdir in DIRECTORIES:
        _mkdir_secure(target / subdir)
    return inspect(repo, home=home)


def init_lens(repo_dir: Path, lens: str, *, home: Path | None = None) -> dict:
    if not VALID_LENS.fullmatch(lens):
        raise WorkspaceError("identificador de lente no válido")
    info = inspect(repo_dir, home=home)
    if info["status"] != "ready":
        raise WorkspaceError("workspace no preparado; ejecutar init antes")
    dest = Path(info["workspace"]) / "lenses" / lens
    for subdir in LENS_DIRECTORIES:
        _mkdir_secure(dest / subdir)
    return {**info, "lens": lens, "lens_path": str(dest)}


def target_path(repo_dir: Path, relative: str, *, home: Path | None = None) -> dict:
    info = inspect(repo_dir, home=home)
    if info["status"] != "ready":
        raise WorkspaceError("workspace no preparado; ejecutar init antes")
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or any(part in {"..", "."} for part in rel.parts):
        raise WorkspaceError("destino absoluto o traversal prohibido")
    dest = Path(info["workspace"]) / rel
    _no_symlinks(dest)
    if not dest.is_relative_to(Path(info["workspace"])):
        raise WorkspaceError("destino fuera del workspace")
    return {**info, "path": str(dest)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("inspect", "init", "init-lens", "path"))
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--lens", help="Para init-lens: lente del catálogo")
    parser.add_argument("--relative", help="Para path: ruta relativa al workspace")
    args = parser.parse_args(argv)
    try:
        if args.action == "inspect":
            result = inspect(args.repo)
        elif args.action == "init":
            result = init(args.repo)
        elif args.action == "init-lens":
            if args.lens is None:
                parser.error("init-lens requiere --lens")
            result = init_lens(args.repo, args.lens)
        else:
            if args.relative is None:
                parser.error("path requiere --relative")
            result = target_path(args.repo, args.relative)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (WorkspaceError, OSError) as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
