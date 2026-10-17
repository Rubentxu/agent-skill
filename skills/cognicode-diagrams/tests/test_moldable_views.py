"""Small end-to-end tests of derived contextual navigation; no external harness."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
import atlas
import affordances
import editorial
import moldable_views as moldable
import report_thinking as report
import workspace


class MoldableNavigationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "target"
        self.repo.mkdir()
        (self.repo / "NEVER_READ_THIS.txt").write_text("SECRET_IN_TARGET")
        self.home = root / "home"
        self.home.mkdir()
        workspace.init(self.repo, home=self.home)
        workspace.init_lens(self.repo, "c4", home=self.home)
        self.w = Path(workspace.inspect(self.repo, home=self.home)["workspace"])
        self.q = self.w / "evidence/queries.json"
        self.c = self.w / "evidence/claims.json"
        self.v = self.w / "evidence/terms.json"
        self.q.write_text(json.dumps([
            {"query_id": "Q-1", "mode": "structured", "status": "ok",
             "source": "cognicode", "observation_plane": "static",
             "symbol_ids": ["App::Entry", "App::Store"], "relation_ids": ["edge-1"]}
        ]))
        self.c.write_text(json.dumps([
            {"claim_id": "C-1", "kind": "entity", "provenance": "OBSERVED_CODE",
             "symbol_id": "App::Entry", "coverage": "complete", "query_ids": ["Q-1"]},
            {"claim_id": "C-2", "kind": "entity", "provenance": "OBSERVED_CODE",
             "symbol_id": "App::Store", "coverage": "complete", "query_ids": ["Q-1"]},
            {"claim_id": "R-1", "kind": "relation", "provenance": "OBSERVED_CODE",
             "from_symbol": "App::Entry", "to_symbol": "App::Store", "relation_id": "edge-1",
             "relation_source": "graph_edge", "coverage": "partial", "plane": "static",
             "attributes": {"kind": "calls"}, "query_ids": ["Q-1"]}
        ]))
        self.v.write_text(json.dumps([
            {"context_id": "orquestacion", "term_id": "paso", "status": "accepted",
             "curator": "Experto", "label": "Paso del proceso",
             "definition": "Una tarea independiente.", "symbol_ids": ["App::Entry"]},
            {"context_id": "almacen", "term_id": "paso", "status": "candidate",
             "label": "Movimiento de almacén",
             "definition": "Un movimiento.", "symbol_ids": ["App::Entry"]}
        ]))

    def tearDown(self):
        self.tmp.cleanup()

    def test_available_links_from_same_evidence_and_no_checkout_read(self):
        self.assertEqual(moldable.build(self.repo, "App::Entry", home=self.home, check=True)["reports"], 0)
        self.assertFalse((self.w / "navigation").exists())
        report.build(self.repo, "symbol-passport", symbol="App::Entry",
                     context="orquestacion", home=self.home)
        report.build(self.repo, "term-card", context="orquestacion",
                     term="paso", home=self.home)
        report_path = self.w / "lenses/c4/reports/context.atlas.json"
        report_path.write_text(json.dumps({
            "schema_version": 1, "plane": "implementation", "label": "Recorrido confirmado",
            "claim_ids": ["C-1", "C-2", "R-1"],
            "assets": ["lenses/c4/sources/context.mmd"]
        }))
        (self.w / "lenses/c4/sources/context.mmd").write_text("flowchart LR\nA-->B\n")
        editorial.render(self.repo, "context", home=self.home, link=True)
        out = moldable.build(self.repo, "App::Entry", context="orquestacion", home=self.home)
        payload = json.loads(Path(out["json"]).read_text())
        html = Path(out["html"]).read_text()
        self.assertEqual([r["rel"] for r in payload["reports"]],
                         ["open-passport", "open-term-card"])
        self.assertEqual(payload["language"]["label"], "Paso del proceso")
        self.assertEqual(payload["language"]["status"], "accepted")
        self.assertEqual(payload["evidence"]["claim_ids"], ["C-1", "R-1"])
        self.assertEqual(payload["views"][0]["status"], "ready")
        self.assertIn("context.editorial.html", html)
        self.assertIn("symbol-passport-", html)
        self.assertIn("term-card-", html)
        self.assertNotIn("SECRET_IN_TARGET", html)
        nav = Path(atlas.build(self.repo, home=self.home)["markdown"]).read_text()
        self.assertIn("Navegación moldable", nav)
        self.assertIn("Paso del proceso", nav)
        self.assertEqual(atlas.check(self.repo, home=self.home)["status"], "CURRENT")
        self.assertEqual(moldable.build(self.repo, "App::Entry", context="orquestacion",
                                       home=self.home), out)

    def test_unselected_context_preserves_ambiguity(self):
        page = moldable.project(self.w, "App::Entry")
        self.assertEqual(page["language"]["label"], "App::Entry")
        self.assertEqual(page["language"]["status"], "unmapped")
        self.assertEqual(len(page["language"]["alternative_contexts"]), 2)

    def test_scoped_passports_do_not_overwrite_other_contexts(self):
        sales = report.build(self.repo, "symbol-passport", symbol="App::Entry",
                             context="almacen", home=self.home)
        orchestration = report.build(self.repo, "symbol-passport", symbol="App::Entry",
                                     context="orquestacion", home=self.home)
        self.assertNotEqual(sales["json"], orchestration["json"])
        self.assertTrue(Path(sales["json"]).is_file())
        self.assertTrue(Path(orchestration["json"]).is_file())
        self.assertEqual(json.loads(Path(sales["json"]).read_text())["language"]["status"], "candidate")
        self.assertEqual(json.loads(Path(orchestration["json"]).read_text())["language"]["status"], "accepted")

    def test_only_real_correlated_entity_views_linked(self):
        view = self.w / "lenses/c4/reports/noclaim.atlas.json"
        view.write_text(json.dumps({"schema_version": 1, "label": "Wrong",
                                    "claim_ids": ["C-2"], "assets": []}))
        self.assertEqual(moldable.project(self.w, "App::Entry")["views"], [])
        claims = json.loads(self.c.read_text())
        claims[0]["symbol_id"] = "Forged"
        self.c.write_text(json.dumps(claims))
        with self.assertRaisesRegex(report.ReportError, "not corroborated"):
            moldable.project(self.w, "Forged")

    def test_stale_page_requires_regeneration(self):
        report.build(self.repo, "symbol-passport", symbol="App::Entry", home=self.home)
        moldable.build(self.repo, "App::Entry", home=self.home)
        atlas.build(self.repo, home=self.home)
        terms = json.loads(self.v.read_text())
        terms[0]["label"] = "Un paso cambiado"
        self.v.write_text(json.dumps(terms))
        self.assertEqual(atlas.check(self.repo, home=self.home)["status"], "STALE")
        with self.assertRaisesRegex(Exception, "stale"):
            atlas.build(self.repo, home=self.home)
        moldable.build(self.repo, "App::Entry", home=self.home)
        self.assertEqual(atlas.build(self.repo, home=self.home)["status"], "ATLAS_SOURCE_READY")

    def test_unowned_page_refused(self):
        j, _ = moldable.paths(self.w, "App::Entry", None)
        j.parent.mkdir(parents=True)
        j.write_text("unowned")
        with self.assertRaisesRegex(moldable.MoldableError, "unowned"):
            moldable.build(self.repo, "App::Entry", home=self.home)


class MoldableRoutingTests(unittest.TestCase):
    def state(self, **changes):
        return {"intent": "moldable", "workspace": "ready", "evidence_origin": "cognicode",
                "basis": "unknown", "claim_coverage": "partial",
                "moldable": {"symbol": "App::Entry", **changes}}

    def test_preflight_render_atlas_review(self):
        s = self.state()
        self.assertEqual(affordances.affordances(s)["recommended"], "inspect-moldable")
        s["moldable"]["prepared"] = "ready"
        self.assertEqual(affordances.affordances(s)["recommended"], "render-moldable")
        s["moldable"]["render"] = "ready"
        self.assertEqual(affordances.affordances(s)["recommended"], "build-atlas")
        s["moldable"]["atlas_source"] = "ready"
        self.assertEqual(affordances.affordances(s)["recommended"], "open-moldable")
        s["moldable"]["visual_review"] = "passed"
        self.assertEqual(affordances.affordances(s)["status"], "PARTIAL")

    def test_unknown_provenance_or_unsafe_context_never_fallback(self):
        s = self.state(prepared="ready")
        s["evidence_origin"] = "other"
        self.assertEqual(affordances.affordances(s)["_links"], [])
        self.assertEqual(affordances.affordances(self.state(prepared="missing"))["status"], "BLOCKED")
        with self.assertRaises(affordances.InvalidState):
            affordances.affordances(self.state(context="../../outside"))


if __name__ == "__main__":
    unittest.main()
