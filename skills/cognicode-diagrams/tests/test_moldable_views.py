"""Small end-to-end tests of derived contextual navigation; no external harness."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

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

    def test_svg_nodes_link_back_to_current_contextual_pages(self):
        # Diagram -> symbol page -> passport/term/evidence -> diagram.
        report.build(self.repo, "symbol-passport", symbol="App::Entry",
                     context="orquestacion", home=self.home)
        report.build(self.repo, "term-card", context="orquestacion",
                     term="paso", home=self.home)
        manifest = self.w / "lenses/c4/reports/context.atlas.json"
        manifest.write_text(json.dumps({
            "schema_version": 1, "plane": "implementation", "label": "Recorrido",
            "claim_ids": ["C-1", "C-2", "R-1"],
            "assets": ["lenses/c4/sources/context.mmd"]
        }))
        (self.w / "lenses/c4/sources/context.mmd").write_text("flowchart LR\nA-->B\n")
        editorial.render(self.repo, "context", home=self.home, link=True)
        p = moldable.build(self.repo, "App::Entry", context="orquestacion", home=self.home)
        checked = editorial.inspect(self.repo, "context", context="orquestacion", home=self.home)
        self.assertEqual(checked["linked_nodes"], 1)
        out = editorial.render(self.repo, "context", context="orquestacion", home=self.home)
        svg = Path(out["svg"]).read_text(encoding="utf-8")
        page = Path(out["html"]).read_text(encoding="utf-8")
        root = ET.fromstring(svg[svg.index("<svg"):])
        ns = {"s": "http://www.w3.org/2000/svg"}
        anchors = root.findall(".//s:a", namespaces=ns)
        self.assertEqual(len(anchors), 1)
        anchor = anchors[0]
        self.assertTrue(anchor.attrib["href"].startswith("../../../navigation/moldable/"))
        self.assertIn("Abrir ficha contextual", anchor.attrib["aria-label"])
        node = anchor.find("s:g", ns)
        self.assertEqual(node.attrib["data-symbol-id"], "App::Entry")
        self.assertEqual(node.attrib["data-context-id"], "orquestacion")
        self.assertEqual(node.attrib["data-term-id"], "paso")
        self.assertEqual(node.attrib["data-term-status"], "accepted")
        self.assertIn("Paso del proceso", svg)
        self.assertIn("App::Entry", svg)
        self.assertIn("Abrir ficha", page)
        self.assertIn("http-equiv=\"Content-Security-Policy\"", page)
        self.assertEqual(moldable.current_page(self.w, "App::Entry", "orquestacion"),
                         Path(p["html"]))
        self.assertNotIn("SECRET_IN_TARGET", svg)
        self.assertEqual(atlas.build(self.repo, home=self.home)["status"], "ATLAS_SOURCE_READY")

        # A changed term immediately invalidates the old navigation target.
        terms = json.loads(self.v.read_text())
        terms[0]["label"] = "Paso revisado"
        self.v.write_text(json.dumps(terms))
        self.assertIsNone(moldable.current_page(self.w, "App::Entry", "orquestacion"))
        out = editorial.render(self.repo, "context", context="orquestacion", home=self.home)
        svg = Path(out["svg"]).read_text()
        self.assertIn("Paso revisado", svg)
        self.assertNotIn('class="node-link"', svg)
        moldable.build(self.repo, "App::Entry", context="orquestacion", home=self.home)
        out = editorial.render(self.repo, "context", context="orquestacion", home=self.home)
        self.assertIn('class="node-link"', Path(out["svg"]).read_text())

    def test_ambiguous_context_and_unowned_html_never_get_live_link(self):
        manifest = self.w / "lenses/c4/reports/context.atlas.json"
        manifest.write_text(json.dumps({
            "schema_version": 1, "plane": "implementation", "label": "Recorrido",
            "claim_ids": ["C-1", "C-2", "R-1"],
            "assets": ["lenses/c4/sources/context.mmd"]
        }))
        (self.w / "lenses/c4/sources/context.mmd").write_text("flowchart LR\nA-->B\n")
        # Without bounded context the model preserves ambiguous technical IDs.
        out = editorial.render(self.repo, "context", home=self.home)
        self.assertNotIn("Paso del proceso", Path(out["svg"]).read_text())
        self.assertIn("App::Entry", Path(out["svg"]).read_text())
        page = moldable.build(self.repo, "App::Entry", context="almacen", home=self.home)
        out = editorial.render(self.repo, "context", context="almacen", home=self.home)
        svg = Path(out["svg"]).read_text()
        self.assertIn("Movimiento de almacén (propuesto)", svg)
        self.assertIn('data-term-status="candidate"', svg)
        self.assertIn('class="node-link"', svg)
        Path(page["html"]).write_text(moldable.MARKER + "\n" + "<script>bad()</script>")
        out = editorial.render(self.repo, "context", context="almacen", home=self.home)
        self.assertNotIn('class="node-link"', Path(out["svg"]).read_text())

    def test_change_brief_appears_only_when_current_for_exact_symbol_and_context(self):
        prepared = report.build(self.repo, "change-impact", symbol="App::Entry",
                                context="orquestacion", goal="Modificar reintentos",
                                home=self.home)
        m = moldable.project(self.w, "App::Entry", context="orquestacion")
        self.assertEqual([x["rel"] for x in m["reports"]], ["open-change-impact"])
        self.assertEqual(m["reports"][0]["goal"], "Modificar reintentos")
        self.assertEqual(m["reports"][0]["readiness"], "PARTIAL_RESEARCH_REQUIRED")
        out = moldable.build(self.repo, "App::Entry", context="orquestacion",
                             home=self.home)
        html = Path(out["html"]).read_text(encoding="utf-8")
        self.assertIn("Preparar cambio:", html)
        self.assertIn("change-impact-", html)
        self.assertNotIn("SECRET_IN_TARGET", html)
        self.assertFalse(moldable.project(self.w, "App::Entry", context="almacen")["reports"])
        changed = json.loads(self.v.read_text())
        changed[0]["definition"] = "Responsabilidad redefinida"
        self.v.write_text(json.dumps(changed))
        self.assertNotIn("open-change-impact",
                         [x["rel"] for x in moldable.project(self.w, "App::Entry",
                                                             context="orquestacion")["reports"]])
        report.build(self.repo, "change-impact", symbol="App::Entry",
                     context="orquestacion", goal="Modificar reintentos", home=self.home)
        self.assertEqual([x["rel"] for x in moldable.project(self.w, "App::Entry",
                                                             context="orquestacion")["reports"]],
                         ["open-change-impact"])
        self.assertTrue(Path(prepared["json"]).exists())

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

    def test_invalid_matched_diagram_never_becomes_link(self):
        manifest = self.w / "lenses/c4/reports/broken.atlas.json"
        manifest.write_text(json.dumps({"schema_version": 1, "label": "Broken",
                                        "claim_ids": ["C-1"], "assets": []}))
        data = moldable.project(self.w, "App::Entry")
        self.assertEqual(data["views"][0]["status"], "invalid")
        out = moldable.build(self.repo, "App::Entry", home=self.home)
        html = Path(out["html"]).read_text()
        self.assertNotIn("Abrir diagrama", html)
        self.assertNotIn("broken.editorial.html", html)

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
