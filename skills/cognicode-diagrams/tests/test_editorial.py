"""Focused tests for the optional editorial projector: no additional test harness."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
import atlas
import editorial
import workspace


class EditorialTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        self.home = root / "home"
        self.home.mkdir()
        workspace.init(self.repo, home=self.home)
        workspace.init_lens(self.repo, "c4", home=self.home)
        self.w = Path(workspace.inspect(self.repo, home=self.home)["workspace"])
        self.source = self.w / "lenses/c4/sources/context.mmd"
        self.source.write_text("flowchart LR\nA-->B\n", encoding="utf-8")
        self.report = self.w / "lenses/c4/reports/context.atlas.json"
        self.report.write_text(json.dumps({
            "schema_version": 1, "plane": "implementation", "label": "Arquitectura C4",
            "claim_ids": ["C-1", "C-2", "R-1"],
            "assets": ["lenses/c4/sources/context.mmd"]
        }), encoding="utf-8")
        self.claims = self.w / "evidence/claims.json"
        self.queries = self.w / "evidence/queries.json"
        self.queries.write_text(json.dumps([{"query_id": "Q-1"}]), encoding="utf-8")
        self.claims.write_text(json.dumps([
            {"claim_id": "C-1", "kind": "entity", "provenance": "OBSERVED_CODE",
             "symbol_id": "App::Api", "category": "surface", "coverage": "complete",
             "query_ids": ["Q-1"], "plane": "static"},
            {"claim_id": "C-2", "kind": "entity", "provenance": "OBSERVED_CODE",
             "symbol_id": "App::Store", "category": "store", "coverage": "partial",
             "query_ids": ["Q-1"], "plane": "static"},
            {"claim_id": "R-1", "kind": "relation", "provenance": "OBSERVED_CODE",
             "from_symbol": "App::Api", "to_symbol": "App::Store",
             "relation_source": "graph_edge", "attributes": {"kind": "calls"},
             "coverage": "partial", "plane": "static", "query_ids": ["Q-1"]}
        ]), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_renders_html_svg_and_is_integrated_in_existing_atlas(self):
        out = editorial.render(self.repo, "context", home=self.home)
        self.assertEqual(out["coverage"], "PARTIAL / UNKNOWN COVERAGE")
        html = Path(out["html"]).read_text(encoding="utf-8")
        svg = Path(out["svg"]).read_text(encoding="utf-8")
        self.assertIn('data-claim-id="R-1"', html)
        self.assertIn('data-query-ids="Q-1"', svg)
        self.assertIn('data-plane="static"', svg)
        self.assertIn('http-equiv="Content-Security-Policy"', html)
        self.assertNotIn("<script", html)
        self.assertIn("App::Api", html)
        self.assertEqual(editorial.render(self.repo, "context", home=self.home), out)
        report = json.loads(self.report.read_text(encoding="utf-8"))
        report["assets"] += [
            "lenses/c4/renders/context.editorial.svg",
            "lenses/c4/renders/context.editorial.html"]
        self.report.write_text(json.dumps(report), encoding="utf-8")
        result = atlas.build(self.repo, home=self.home)
        nav = Path(result["markdown"]).read_text(encoding="utf-8")
        self.assertIn("context.editorial.html", nav)
        self.assertIn("context.editorial.svg", nav)
        self.assertNotIn("![context.editorial.html]", nav)
        self.assertEqual(atlas.check(self.repo, home=self.home)["status"], "CURRENT")

    def test_reference_link_cannot_be_forged_into_graph_edge(self):
        claims = json.loads(self.claims.read_text(encoding="utf-8"))
        claims[-1]["relation_source"] = "reference_link"
        self.claims.write_text(json.dumps(claims), encoding="utf-8")
        with self.assertRaisesRegex(editorial.EditorialError, "reference_link"):
            editorial.render(self.repo, "context", home=self.home)

    def test_missing_query_blocks_render(self):
        self.queries.write_text("[]", encoding="utf-8")
        with self.assertRaisesRegex(editorial.EditorialError, "unsubstantiated"):
            editorial.render(self.repo, "context", home=self.home)

    def test_incomplete_edge_endpoint_blocks_render(self):
        claims = json.loads(self.claims.read_text(encoding="utf-8"))
        claims[-1]["to_symbol"] = "Missing"
        self.claims.write_text(json.dumps(claims), encoding="utf-8")
        with self.assertRaisesRegex(editorial.EditorialError, "endpoint"):
            editorial.render(self.repo, "context", home=self.home)

    def test_unsafe_editorial_html_not_indexed_or_served(self):
        target = self.w / "lenses/c4/renders/malicious.editorial.html"
        target.write_text("<script>alert(1)</script>", encoding="utf-8")
        with self.assertRaisesRegex(atlas.AtlasError, "contrato de seguridad"):
            atlas.build(self.repo, home=self.home)

    def test_unowned_output_not_overwritten(self):
        target = self.w / "lenses/c4/renders/context.editorial.svg"
        target.write_text("not ours", encoding="utf-8")
        with self.assertRaisesRegex(editorial.EditorialError, "non-editorial"):
            editorial.render(self.repo, "context", home=self.home)
        self.assertEqual(target.read_text(encoding="utf-8"), "not ours")

    def test_escape_hostile_symbol_and_title(self):
        claims = json.loads(self.claims.read_text(encoding="utf-8"))
        claims[0]["symbol_id"] = "Api<unsafe>"
        claims[-1]["from_symbol"] = "Api<unsafe>"
        self.claims.write_text(json.dumps(claims), encoding="utf-8")
        html = Path(editorial.render(self.repo, "context", home=self.home)["html"]).read_text(encoding="utf-8")
        self.assertIn("Api&lt;unsafe&gt;", html)
        self.assertNotIn("<unsafe>", html)

    def test_custom_profile_applies_to_html_and_svg(self):
        folder = self.home / ".cognicode-diagrams/profiles"
        folder.mkdir(parents=True, exist_ok=True)
        folder.joinpath("dark.json").write_text(json.dumps({
            "paper": "#111827", "surface": "#1f2937", "ink": "#ffffff",
            "stroke": "#e5e7eb", "muted": "#cbd5e1", "connector": "#94a3b8"
        }), encoding="utf-8")
        out = editorial.render(self.repo, "context", home=self.home, profile="dark")
        self.assertEqual(out["profile"], "dark")
        self.assertIn("#111827", Path(out["html"]).read_text(encoding="utf-8"))
        self.assertIn("#1f2937", Path(out["svg"]).read_text(encoding="utf-8"))

    def test_unreadable_profile_fails_without_output(self):
        folder = self.home / ".cognicode-diagrams/profiles"
        folder.mkdir(parents=True, exist_ok=True)
        folder.joinpath("bad.json").write_text(json.dumps({
            "paper": "#ffffff", "surface": "#ffffff", "ink": "#ffffff",
            "stroke": "#ffffff", "muted": "#ffffff", "connector": "#ffffff"
        }), encoding="utf-8")
        with self.assertRaisesRegex(editorial.EditorialError, "contrast"):
            editorial.render(self.repo, "context", home=self.home, profile="bad")
        self.assertFalse((self.w / "lenses/c4/renders/context.editorial.html").exists())

    def test_derived_inputs_only_and_no_output_for_invalid_view(self):
        report = json.loads(self.report.read_text(encoding="utf-8"))
        report["assets"] = ["../../repo/README.md"]
        self.report.write_text(json.dumps(report), encoding="utf-8")
        with self.assertRaisesRegex(editorial.EditorialError, "invalid view asset"):
            editorial.render(self.repo, "context", home=self.home)
        self.assertFalse((self.w / "lenses/c4/renders/context.editorial.html").exists())


if __name__ == "__main__":
    unittest.main()
