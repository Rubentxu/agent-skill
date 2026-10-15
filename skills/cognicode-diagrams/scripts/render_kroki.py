#!/usr/bin/env python3
"""Render one textual diagram via a pre-existing local Kroki server.

Read-only for source; writes only the requested preview. stdlib only.
Never starts a container, installs software, calls cloud services or touches CogniCode.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

MAX_INPUT = 1024 * 1024
MAX_OUTPUT = 16 * 1024 * 1024
MIME = {"svg": "image/svg+xml", "png": "image/png"}
ENDPOINTS = {"mermaid": "mermaid", "structurizr": "structurizr", "plantuml": "plantuml"}


class RenderError(RuntimeError):
    """Rendering was not completed; never claim a successful preview."""


def local_base_url(url: str) -> str:
    """Allow only an explicit HTTP loopback Kroki endpoint; no cloud fallback."""
    parsed = urlsplit(url)
    if (parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}
            or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in {"", "/"}):
        raise RenderError("Kroki debe ser HTTP loopback local, sin credenciales, path ni query")
    if not parsed.port:
        raise RenderError("Indica el puerto de Kroki explícitamente (p. ej., :8000)")
    return url.rstrip("/")


def build_request(source: str, kind: str, image_format: str, view_key: str | None = None) -> bytes:
    if kind not in ENDPOINTS or image_format not in MIME:
        raise RenderError("Formato de entrada o de salida no admitido")
    if not source.strip():
        raise RenderError("Fuente vacía: no hay diagrama que renderizar")
    if len(source.encode("utf-8")) > MAX_INPUT:
        raise RenderError("La fuente supera el máximo de 1 MiB")
    if view_key and kind != "structurizr":
        raise RenderError("--view-key solo aplica a Structurizr DSL")
    body = {"diagram_source": source, "diagram_type": ENDPOINTS[kind], "output_format": image_format}
    if view_key:
        body["diagram_options"] = {"view-key": view_key}
    return json.dumps(body, ensure_ascii=False).encode("utf-8")


def verify_image(blob: bytes, kind: str, content_type: str) -> None:
    if not blob or len(blob) > MAX_OUTPUT:
        raise RenderError("Salida vacía o demasiado grande")
    if kind == "png":
        if not blob.startswith(b"\x89PNG\r\n\x1a\n"):
            raise RenderError("Kroki no devolvió una imagen PNG")
    elif kind == "svg":
        # XML declarations and BOM are permitted. Reject HTML errors, not just the HTTP status.
        normalized = blob.lstrip(b"\xef\xbb\xbf \r\n\t")
        if b"<svg" not in normalized[:4000] or b"<html" in normalized[:4000].lower():
            raise RenderError("Kroki no devolvió un SVG")
    if content_type and MIME[kind] not in content_type.lower():
        raise RenderError(f"Tipo de respuesta inesperado: {content_type}")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def render(source_file: Path, output: Path, diagram_type: str, image_format: str,
           base_url: str = "http://127.0.0.1:8000", view_key: str | None = None,
           timeout: float = 20.0) -> None:
    base = local_base_url(base_url)
    if source_file.is_symlink() or not source_file.is_file():
        raise RenderError("Fuente ausente o enlace simbólico: no seguir rutas inesperadas")
    if source_file.stat().st_size > MAX_INPUT:
        raise RenderError("La fuente supera el máximo de 1 MiB")
    source = source_file.read_text(encoding="utf-8")
    data = build_request(source, diagram_type, image_format, view_key)
    if timeout <= 0 or timeout > 120:
        raise RenderError("timeout fuera del rango (0, 120] segundos")
    if output.exists() and output.is_symlink():
        raise RenderError("La salida no puede ser un enlace simbólico")
    if output.suffix.lower() != "." + image_format:
        raise RenderError(f"Salida esperada: .{image_format}")
    request = Request(base + "/", data=data, headers={"Content-Type": "application/json", "Accept": MIME[image_format]}, method="POST")
    try:
        with build_opener(ProxyHandler({}), NoRedirect()).open(request, timeout=timeout) as response:
            body = response.read(MAX_OUTPUT + 1)
            verify_image(body, image_format, response.headers.get("Content-Type", ""))
    except HTTPError as e:
        detail = e.read(2048).decode("utf-8", errors="replace").strip()
        raise RenderError(f"Kroki HTTP {e.code}: {detail[:400]}") from e
    except (URLError, TimeoutError, OSError) as e:
        raise RenderError(f"Kroki local no disponible: {e}") from e

    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(dir=output.parent, prefix=".kroki-", delete=False) as f:
            tmp = Path(f.name)
            f.write(body)
        os.replace(tmp, output)
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--type", choices=tuple(ENDPOINTS), required=True)
    parser.add_argument("--format", choices=tuple(MIME), default="svg")
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--view-key", help="Identificador de vista para Structurizr DSL")
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()
    try:
        render(args.source, args.output, args.type, args.format, args.url, args.view_key, args.timeout)
    except (RenderError, UnicodeError, ValueError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"RENDERED: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
