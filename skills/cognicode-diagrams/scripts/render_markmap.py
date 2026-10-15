#!/usr/bin/env python3
"""Render the existing generated atlas.md to HTML using Markmap CLI (optional).

Explicit CLI action; never installs tools, starts persistent services or touches code.
An HTML render is an auxiliary projection, not a semantic architecture proof.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from atlas import AtlasError, MARKER, check
from workspace import inspect as inspect_workspace

CONTAINER_IMAGE = "cognicode-markmap:0.18.12"


class RenderError(ValueError):
    pass


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=90, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RenderError(f"no se ha ejecutado Markmap: {exc}") from exc


def render(repo: Path, *, engine: str = "podman", image: str = CONTAINER_IMAGE,
           allow_asset_network: bool = False, home: Path | None = None) -> dict:
    if engine not in {"podman", "docker", "native"}:
        raise RenderError("motor no soportado")
    if any(c in image for c in ("\n", "\r", "\x00")) or not image.startswith("cognicode-markmap:"):
        raise RenderError("solo se permite la imagen local de Markmap preparada para esta skill")
    snapshot = check(repo, home=home)
    if snapshot["status"] != "CURRENT":
        raise RenderError("atlas ausente u obsoleto: ejecutar atlas.py build")
    info = inspect_workspace(repo, home=home)
    workspace = Path(info["workspace"])
    nav = workspace / "navigation"
    output = nav / "atlas.html"
    if output.is_symlink():
        raise RenderError("destino HTML enlazado, operación rechazada")
    if output.exists() and not output.read_text(encoding="utf-8").startswith("<!-- cognicode-diagrams markmap -->"):
        raise RenderError("HTML preexistente no gestionado por la skill")
    # Markmap CLI outputs a fully formed HTML document. The marker is inserted as a comment
    # only after successful generation; old HTML is preserved on error.
    fd, tmpname = tempfile.mkstemp(dir=nav, prefix=".atlas-", suffix=".html")
    os.close(fd)
    temp = Path(tmpname)
    try:
        if engine == "native":
            binary = shutil.which("markmap")
            if binary is None:
                raise RenderError("markmap-cli no está instalado; no se instala automáticamente")
            cmd = [binary, str(nav / "atlas.md"), "--offline", "--no-open", "--output", str(temp)]
        else:
            binary = shutil.which(engine)
            if not binary:
                raise RenderError(f"{engine} no encontrado")
            # A single ephemeral invocation, no ports and no checkout mount.
            # Network disabled by default; --offline can fail with some Markmap versions if
            # supporting browser assets were not cached. Network opt-in is explicit.
            cmd = [binary, "run", "--rm", "--security-opt", "no-new-privileges",
                   "--network", "bridge" if allow_asset_network else "none",
                   "--user", f"{os.getuid()}:{os.getgid()}",
                   "-v", f"{workspace}:/data:ro,z",
                   "-v", f"{nav}:/data/navigation:rw,z",
                   image, "/data/navigation/atlas.md", "--offline", "--no-open",
                   "--output", "/data/navigation/" + temp.name]
        proc = _run(cmd)
        if proc.returncode != 0:
            raise RenderError(f"Markmap falló ({proc.returncode}): {proc.stderr.strip()[:300]}")
        if not temp.is_file():
            raise RenderError("Markmap no produjo HTML")
        html = temp.read_text(encoding="utf-8")
        if "<html" not in html.lower() or "</html>" not in html.lower() or "<script" not in html.lower():
            raise RenderError("Markmap no devolvió un HTML interactivo válido")
        temp.write_text("<!-- cognicode-diagrams markmap -->\n" + html, encoding="utf-8")
        os.replace(temp, output)
        return {"status": "RENDERED_NOT_VISUALLY_REVIEWED", "html": str(output),
                "source": str(nav / "atlas.md"), "engine": engine,
                "network": "enabled-for-assets" if allow_asset_network else "disabled"}
    finally:
        if temp.exists():
            temp.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--engine", choices=("podman", "docker", "native"), default="podman")
    parser.add_argument("--allow-asset-network", action="store_true", help="Permite red durante renderizado; autorización separada")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(render(args.repo, engine=args.engine, allow_asset_network=args.allow_asset_network), ensure_ascii=False, indent=2))
        return 0
    except (RenderError, AtlasError, ValueError, OSError) as exc:
        print(json.dumps({"status": "RENDER_FAILED", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
