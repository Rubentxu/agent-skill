"""Offline tests; mock Kroki's HTTP contract, never pull containers or hit public network."""
from __future__ import annotations

import gc
import importlib.util
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest
import warnings
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("render_kroki", ROOT / "scripts/render_kroki.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

SVG = b'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="50"></svg>'
PNG = b'\x89PNG\r\n\x1a\n' + b'example-bytes-for-unit-test'


class Handler(BaseHTTPRequestHandler):
    responses = []
    requests = []

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        payload = json.loads(self.rfile.read(length))
        self.requests.append(payload)
        status, media, data, extra_headers = self.responses.pop(0)
        self.send_response(status)
        self.send_header("Content-Type", media)
        for name, value in extra_headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


class KrokiTests(unittest.TestCase):
    def setUp(self):
        Handler.requests = []
        Handler.responses = []
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.home = Path(self.temp.name)
        self.workspace = self.home / ".cognicode-diagrams" / "workspaces" / "repo--123456789abc"
        self.source = self.workspace / "lenses" / "c4" / "sources" / "source.mmd"
        self.source.parent.mkdir(parents=True)
        self.source.write_text("C4Context\n    System(foo, \"Service\")\n", encoding="utf-8")
        self.target = self.workspace / "lenses" / "c4" / "renders" / "diagram.svg"
        self.target.parent.mkdir(parents=True)
        self.home_patch = patch.object(module.Path, "home", return_value=self.home)
        self.home_patch.start()
        self.addCleanup(self.home_patch.stop)

    def test_mermaid_renders_from_source_and_svg(self):
        Handler.responses = [(200, "image/svg+xml", SVG, {})]
        module.render(self.source, self.target, "mermaid", "svg", self.url)
        self.assertEqual(self.target.read_bytes(), SVG)
        self.assertEqual(Handler.requests[0]["diagram_type"], "mermaid")
        self.assertIn("C4Context", Handler.requests[0]["diagram_source"])
        self.assertNotIn("diagram_options", Handler.requests[0])

    def test_structurizr_view_key_is_forwarded(self):
        Handler.responses = [(200, "image/png", PNG, {})]
        self.source = self.source.rename(self.source.with_suffix(".dsl"))
        self.source.write_text('workspace "Test" {}', encoding="utf-8")
        dst = self.target.with_suffix(".png")
        module.render(self.source, dst, "structurizr", "png", self.url, "Containers")
        self.assertEqual(Handler.requests[0]["diagram_options"], {"view-key": "Containers"})
        self.assertEqual(dst.read_bytes(), PNG)

    def test_errors_do_not_overwrite_existing_image(self):
        self.target.write_bytes(SVG)
        Handler.responses = [(400, "text/plain", b"bad C4", {})]
        with self.assertRaisesRegex(module.RenderError, "HTTP 400"):
            module.render(self.source, self.target, "mermaid", "svg", self.url)
        self.assertEqual(self.target.read_bytes(), SVG)

    def test_error_200_not_svg_rejected(self):
        Handler.responses = [(200, "text/html", b"<html>Fail</html>", {})]
        with self.assertRaisesRegex(module.RenderError, "SVG"):
            module.render(self.source, self.target, "mermaid", "svg", self.url)
        self.assertFalse(self.target.exists())

    def test_redirect_is_refused(self):
        Handler.responses = [(302, "text/html", b"", {"Location": "https://external.example/"})]
        with self.assertRaisesRegex(module.RenderError, "HTTP 302"):
            module.render(self.source, self.target, "mermaid", "svg", self.url)
        self.assertFalse(self.target.exists())

    def test_output_limit_enforced(self):
        Handler.responses = [(200, "image/svg+xml", b"<svg>" + b"x" * (module.MAX_OUTPUT + 1), {})]
        with self.assertRaisesRegex(module.RenderError, "grande"):
            module.render(self.source, self.target, "mermaid", "svg", self.url)
        self.assertFalse(self.target.exists())

    def test_bad_mime_rejected(self):
        Handler.responses = [(200, "application/octet-stream", SVG, {})]
        with self.assertRaisesRegex(module.RenderError, "inesperado"):
            module.render(self.source, self.target, "mermaid", "svg", self.url)

    def test_remote_or_credentials_not_allowed(self):
        for url in ("https://kroki.io", "http://example.com:8000", "http://127.0.0.1:8000/evil", "http://u:p@localhost:8000", "http://127.0.0.1:8000/?foo=1"):
            with self.subTest(url=url), self.assertRaises(module.RenderError):
                module.local_base_url(url)

    def test_invalid_view_key_for_mermaid(self):
        with self.assertRaisesRegex(module.RenderError, "view-key"):
            module.build_request("graph TD; A-->B", "mermaid", "svg", "Containers")

    def test_source_size_limit(self):
        with self.assertRaisesRegex(module.RenderError, "máximo"):
            module.build_request("x" * (module.MAX_INPUT + 1), "mermaid", "svg")

    def test_symlink_output_rejected(self):
        existing = self.target.parent / "existing.svg"
        existing.write_bytes(SVG)
        self.target.symlink_to(existing)
        with self.assertRaisesRegex(module.RenderError, "enlace simbólico"):
            module.render(self.source, self.target, "mermaid", "svg", self.url)
        self.assertEqual(existing.read_bytes(), SVG)

    def test_rejects_source_from_original_repository(self):
        repo = self.home / "source-repository"
        repo.mkdir()
        forbidden = repo / "model.mmd"
        forbidden.write_text("C4Context", encoding="utf-8")
        with self.assertRaisesRegex(module.RenderError, "artefactos derivados"):
            module.render(forbidden, self.target, "mermaid", "svg", self.url)
        self.assertEqual(Handler.requests, [])

    def test_rejects_destination_outside_derived_workspace(self):
        with self.assertRaisesRegex(module.RenderError, "artefactos derivados"):
            module.render(self.source, self.home / "escape.svg", "mermaid", "svg", self.url)
        self.assertEqual(Handler.requests, [])

    def test_rejects_cross_workspace_source_destination(self):
        dst = self.home / ".cognicode-diagrams" / "workspaces" / "foreign--123456789abc" / "lenses" / "c4" / "renders" / "foo.svg"
        with self.assertRaisesRegex(module.RenderError, "deben compartir"):
            module.render(self.source, dst, "mermaid", "svg", self.url)

    def test_unreachable_local_returns_error(self):
        with self.assertRaisesRegex(module.RenderError, "no disponible"):
            module.render(self.source, self.target, "mermaid", "svg", "http://127.0.0.1:1", timeout=0.3)

    def test_refused_response_leaves_no_socket_open(self):
        Handler.responses = [(400, "text/plain", b"bad C4", {})]
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            with self.assertRaisesRegex(module.RenderError, "HTTP 400"):
                module.render(self.source, self.target, "mermaid", "svg", self.url)
            gc.collect()
        leaked = [w for w in caught if issubclass(w.category, ResourceWarning)]
        self.assertEqual(leaked, [], f"la respuesta rechazada quedó sin cerrar: {leaked}")


if __name__ == "__main__":
    unittest.main()
