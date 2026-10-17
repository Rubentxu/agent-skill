"""Small discriminating tests for the two moldable projections; no new harness."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
import atlas
import affordances
import report_thinking as report
import workspace


class ReportThinkingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "code"
        self.repo.mkdir()
        # The checkout is deliberately unreadable-by-contract; projector sees identity only.
        (self.repo / "SENTINEL_DO_NOT_READ").write_text("TOP_SECRET", encoding="utf-8")
        self.home = self.root / "home"
        self.home.mkdir()
        workspace.init(self.repo, home=self.home)
        self.w = Path(workspace.inspect(self.repo, home=self.home)["workspace"])
        self.queries = self.w / "evidence/queries.json"
        self.claims = self.w / "evidence/claims.json"
        self.terms = self.w / "evidence/terms.json"
        self.queries.write_text(json.dumps([
            {"query_id": "Q1", "mode": "structured", "status": "ok",
             "source": "cognicode", "observation_plane": "static",
             "symbol_ids": ["App::Entry", "App::Store"], "relation_ids": ["edge-1"]}
        ]), encoding="utf-8")
        self.claims.write_text(json.dumps([
            {"claim_id": "C1", "kind": "entity", "provenance": "OBSERVED_CODE",
             "symbol_id": "App::Entry", "query_ids": ["Q1"], "coverage": "complete"},
            {"claim_id": "C2", "kind": "entity", "provenance": "OBSERVED_CODE",
             "symbol_id": "App::Store", "query_ids": ["Q1"], "coverage": "complete"},
            {"claim_id": "R1", "kind": "relation", "provenance": "OBSERVED_CODE",
             "relation_source": "graph_edge", "relation_id": "edge-1",
             "from_symbol": "App::Entry", "to_symbol": "App::Store",
             "query_ids": ["Q1"], "coverage": "partial",
             "attributes": {"kind": "calls"}}
        ]), encoding="utf-8")
        self.terms.write_text(json.dumps([
            {"context_id": "orquestacion", "term_id": "paso", "label": "Paso del proceso",
             "definition": "Una tarea individual del proceso.",
             "status": "accepted", "curator": "Experto de dominio",
             "symbol_ids": ["App::Entry"], "not_this": "No es todo el proceso"},
            {"context_id": "almacen", "term_id": "paso", "label": "Movimiento del almacén",
             "definition": "Un movimiento de un lote.",
             "status": "candidate", "symbol_ids": ["App::Entry"]}
        ]), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_same_evidence_powers_term_card_passport_and_atlas(self):
        before = (self.repo / "SENTINEL_DO_NOT_READ").read_bytes()
        term = report.build(self.repo, "term-card", context="orquestacion",
                            term="paso", home=self.home)
        passport = report.build(self.repo, "symbol-passport", symbol="App::Entry",
                                context="orquestacion", home=self.home)
        t = json.loads(Path(term["json"]).read_text())
        p = json.loads(Path(passport["json"]).read_text())
        self.assertEqual(t["language"]["label"], p["language"]["label"])
        self.assertEqual(t["language"]["status"], "accepted")
        self.assertEqual(t["language"]["definition_authority"], "HUMAN_CURATED")
        self.assertEqual(t["evidence"]["claim_ids"], p["evidence"]["claim_ids"])
        self.assertIn("R1", t["evidence"]["claim_ids"])
        self.assertEqual(t["evidence"]["related_total"], 1)
        self.assertIn("¿Qué desconocemos?", Path(passport["markdown"]).read_text())
        self.assertNotIn("TOP_SECRET", Path(passport["markdown"]).read_text())
        self.assertEqual(before, (self.repo / "SENTINEL_DO_NOT_READ").read_bytes())
        nav = Path(atlas.build(self.repo, home=self.home)["markdown"]).read_text()
        self.assertIn("Informes moldables", nav)
        self.assertIn("Paso del proceso", nav)
        self.assertIn("JSON para agentes", nav)
        self.assertEqual(atlas.check(self.repo, home=self.home)["status"], "CURRENT")
        self.assertEqual(report.build(self.repo, "term-card", context="orquestacion",
                                      term="paso", home=self.home), term)

    def test_conflicting_contexts_not_silently_merged(self):
        p = report.project(self.w, "symbol-passport", symbol="App::Entry")
        self.assertEqual(p["language"]["status"], "unmapped")
        self.assertEqual(len(p["language"]["alternative_contexts"]), 2)
        self.assertEqual(p["language"]["label"], "App::Entry")
        other = report.project(self.w, "term-card", context="almacen", term="paso")
        self.assertEqual(other["language"]["status"], "candidate")
        self.assertEqual(other["language"]["definition_authority"], "PROPOSED")

    def test_acceptance_requires_real_curator(self):
        data = json.loads(self.terms.read_text())
        del data[0]["curator"]
        self.terms.write_text(json.dumps(data))
        with self.assertRaisesRegex(report.ReportError, "curator"):
            report.build(self.repo, "symbol-passport", symbol="App::Entry", home=self.home)

    def test_query_id_is_not_sufficient_to_forge_entity_or_edge(self):
        data = json.loads(self.queries.read_text())
        data[0]["relation_ids"] = []
        self.queries.write_text(json.dumps(data))
        with self.assertRaisesRegex(report.ReportError, "relation not corroborated"):
            report.build(self.repo, "symbol-passport", symbol="App::Entry", home=self.home)
        data[0]["relation_ids"] = ["edge-1"]
        data[0]["symbol_ids"] = ["Other"]
        self.queries.write_text(json.dumps(data))
        with self.assertRaisesRegex(report.ReportError, "entity not corroborated"):
            report.build(self.repo, "symbol-passport", symbol="App::Entry", home=self.home)

    def test_unsupported_source_cannot_validate_fact(self):
        data = json.loads(self.queries.read_text())
        data[0]["source"] = "github"
        self.queries.write_text(json.dumps(data))
        with self.assertRaisesRegex(report.ReportError, "corroborated"):
            report.build(self.repo, "symbol-passport", symbol="App::Entry", home=self.home)

    def test_missing_evidence_or_unowned_output_fails_closed(self):
        with self.assertRaisesRegex(report.ReportError, "symbol lacks"):
            report.build(self.repo, "symbol-passport", symbol="App::Missing", home=self.home)
        p = report.project(self.w, "symbol-passport", symbol="App::Entry")
        jpath, _ = report.paths(self.w, p)
        jpath.parent.mkdir(exist_ok=True)
        jpath.write_text("user document", encoding="utf-8")
        with self.assertRaisesRegex(report.ReportError, "unowned"):
            report.build(self.repo, "symbol-passport", symbol="App::Entry", home=self.home)
        self.assertEqual(jpath.read_text(), "user document")

    def test_check_has_no_write_and_atlas_tracks_vocab_change(self):
        out = report.build(self.repo, "term-card", context="orquestacion", term="paso",
                           home=self.home, check=True)
        self.assertEqual(out["status"], "EVIDENCE_READY")
        self.assertFalse((self.w / "reports").exists())
        report.build(self.repo, "term-card", context="orquestacion", term="paso", home=self.home)
        atlas.build(self.repo, home=self.home)
        data = json.loads(self.terms.read_text())
        data[0]["definition"] = "Una operación independiente."
        self.terms.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(atlas.check(self.repo, home=self.home)["status"], "STALE")


class ReportRoutingTests(unittest.TestCase):
    def state(self, **changes):
        return {"intent": "report", "workspace": "ready",
                "evidence_origin": "cognicode", "basis": "unknown",
                "claim_coverage": "partial",
                "report": {"kind": "symbol-passport", "symbol": "App::Entry", **changes}}

    def test_discovery_then_render_then_atlas_then_finish(self):
        s = self.state()
        self.assertEqual(affordances.affordances(s)["recommended"], "inspect-report-evidence")
        s["report"]["prepared"] = "ready"
        self.assertEqual(affordances.affordances(s)["recommended"], "render-report")
        s["report"]["render"] = "ready"
        self.assertEqual(affordances.affordances(s)["recommended"], "build-atlas")
        s["report"]["atlas_source"] = "ready"
        self.assertEqual(affordances.affordances(s)["status"], "PARTIAL")

    def test_untrusted_or_missing_evidence_blocks_without_fallback(self):
        for origin in ("other", "unknown"):
            s = self.state(prepared="ready")
            s["evidence_origin"] = origin
            self.assertEqual(affordances.affordances(s)["status"], "BLOCKED")
        self.assertEqual(affordances.affordances(self.state(prepared="missing"))["_links"], [])

    def test_workspace_and_wrong_term_are_rejected(self):
        s = self.state()
        s["workspace"] = "absent"
        self.assertEqual(affordances.affordances(s)["recommended"], "init-workspace")
        with self.assertRaises(affordances.InvalidState):
            affordances.affordances(self.state(kind="term-card", context="../secret", term="foo"))


if __name__ == "__main__":
    unittest.main()
