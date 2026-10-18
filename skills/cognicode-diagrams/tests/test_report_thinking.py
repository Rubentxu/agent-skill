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
import context_capsule as capsule
import moldable_views as moldable
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

    def test_context_capsule_sender_receiver_and_moldable_atlas(self):
        goal = "Modificar persistencia sin romper consumidores"
        self.assertEqual(capsule.build(self.repo, "App::Store", goal,
                                       home=self.home, check=True)["status"], "EVIDENCE_READY")
        self.assertFalse((self.w / "handoffs").exists())
        made = capsule.build(self.repo, "App::Store", goal, home=self.home)
        data = json.loads(Path(made["json"]).read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "PARTIAL_HANDOFF")
        self.assertEqual(data["evidence"]["authority"], "cognicode")
        self.assertEqual(data["observed_relations"][0]["claim_id"], "R1")
        self.assertEqual(data["observed_relations"][0]["direction"], "incoming")
        self.assertEqual(data["possible_impact"]["candidate_symbols"], ["App::Entry"])
        self.assertFalse(data["possible_impact"]["impact_verified"])
        self.assertFalse(data["possible_impact"]["edit_authorized"])
        self.assertFalse(data["relation_scope"]["global_coverage"])
        self.assertIn("read_file", data["receiver_contract"]["forbidden_target_access"])
        self.assertIn("git", data["receiver_contract"]["forbidden_target_access"])
        self.assertIn("PAUSED_NO_FALLBACK", data["receiver_contract"]["when_unavailable"])
        self.assertIn("Vigencia del código: NO comprobada", Path(made["markdown"]).read_text())
        self.assertNotIn("TOP_SECRET", Path(made["markdown"]).read_text())
        self.assertEqual(capsule.build(self.repo, "App::Store", goal, home=self.home), made)
        resumed = capsule.build(self.repo, "App::Store", goal,
                                home=self.home, receiving=True)
        self.assertEqual(resumed["status"], "LEDGER_MATCHES_RUNTIME_UNVERIFIED")
        self.assertFalse(resumed["runtime_verified"])
        self.assertEqual(resumed["next"], "revalidate-by-cognicode")
        self.assertEqual([r["rel"] for r in moldable.project(self.w, "App::Store")["reports"]],
                         ["open-agent-handoff"])
        atlas_text = Path(atlas.build(self.repo, home=self.home)["markdown"]).read_text()
        self.assertIn("Cápsulas de traspaso", atlas_text)
        self.assertIn("Cápsula JSON para agentes", atlas_text)
        self.assertEqual(atlas.check(self.repo, home=self.home)["status"], "CURRENT")

    def test_capsule_does_not_merge_ddd_contexts_or_different_goals(self):
        first = capsule.build(self.repo, "App::Entry", "Ajustar reintentos",
                              context="orquestacion", home=self.home)
        second = capsule.build(self.repo, "App::Entry", "Ajustar reintentos",
                               context="almacen", home=self.home)
        third = capsule.build(self.repo, "App::Entry", "Ajustar timeout",
                              context="orquestacion", home=self.home)
        self.assertEqual(len({first["json"], second["json"], third["json"]}), 3)
        self.assertEqual(json.loads(Path(first["json"]).read_text())["language"]["status"], "accepted")
        self.assertEqual(json.loads(Path(second["json"]).read_text())["language"]["status"], "candidate")
        self.assertEqual([r["rel"] for r in moldable.project(self.w, "App::Entry",
                                                context="orquestacion")["reports"]],
                         ["open-agent-handoff", "open-agent-handoff"])

    def test_capsule_staleness_and_unowned_file_fail_closed(self):
        goal = "Cambiar recuperación"
        capsule.build(self.repo, "App::Entry", goal, home=self.home)
        atlas.build(self.repo, home=self.home)
        queries = json.loads(self.queries.read_text())
        queries[0]["basis"] = "revision-next"
        self.queries.write_text(json.dumps(queries))
        self.assertEqual(capsule.build(self.repo, "App::Entry", goal, home=self.home,
                                       receiving=True)["status"], "STALE_DERIVED_EVIDENCE")
        self.assertEqual(atlas.check(self.repo, home=self.home)["status"], "STALE")
        with self.assertRaisesRegex(Exception, "capsule stale"):
            atlas.build(self.repo, home=self.home)
        capsule.build(self.repo, "App::Entry", goal, home=self.home)
        self.assertEqual(atlas.build(self.repo, home=self.home)["status"], "ATLAS_SOURCE_READY")
        other = "No sobreescribir el documento ajeno"
        jp, _ = capsule.paths(self.w, "App::Entry", other)
        jp.parent.mkdir(exist_ok=True)
        jp.write_text("not a capsule", encoding="utf-8")
        with self.assertRaisesRegex(capsule.CapsuleError, "unowned"):
            capsule.build(self.repo, "App::Entry", other, home=self.home)
        self.assertEqual(jp.read_text(), "not a capsule")

    def test_capsule_never_uses_non_cognicode_source_or_multiline_goal(self):
        with self.assertRaisesRegex(capsule.CapsuleError, "one line"):
            capsule.build(self.repo, "App::Entry", "primera" + chr(10) + "segunda",
                          home=self.home)
        data = json.loads(self.queries.read_text())
        data[0]["source"] = "github"
        self.queries.write_text(json.dumps(data))
        with self.assertRaisesRegex(report.ReportError, "corroborated"):
            capsule.build(self.repo, "App::Entry", "Modificar reintentos", home=self.home)

    def test_change_impact_separates_structural_fact_from_hypothesis(self):
        goal = "Cambiar la persistencia de datos sin romper clientes"
        before = (self.repo / "SENTINEL_DO_NOT_READ").read_bytes()
        result = report.build(self.repo, "change-impact", symbol="App::Store",
                              context="orquestacion", goal=goal, home=self.home)
        payload = json.loads(Path(result["json"]).read_text(encoding="utf-8"))
        change = payload["change"]
        self.assertEqual(change["goal"], goal)
        self.assertEqual(change["question_status"], "USER_INTENT_NOT_CODE_EVIDENCE")
        self.assertEqual([r["claim_id"] for r in change["observed_incoming"]], ["R1"])
        self.assertEqual(change["observed_outgoing"], [])
        self.assertEqual(change["potentially_affected"], [{
            "symbol_id": "App::Entry", "relation_claim_id": "R1",
            "status": "HYPOTHESIS_NOT_VALIDATED"
        }])
        self.assertFalse(change["edit_authorized"])
        self.assertFalse(change["impact_verified"])
        self.assertEqual(change["readiness"], "PARTIAL_RESEARCH_REQUIRED")
        self.assertEqual(payload["evidence"]["query_ids"], ["Q1"])
        self.assertEqual(len(change["next_questions"]), 3)
        self.assertTrue(all(q["authority"] == "cognicode-only" for q in change["next_questions"]))
        explanation = Path(result["markdown"]).read_text(encoding="utf-8")
        self.assertIn("Cambio solicitado (intención del usuario)", explanation)
        self.assertIn("Hipótesis, NO fallos demostrados", explanation)
        self.assertIn("Edición autorizada por este informe: **NO**", explanation)
        self.assertNotIn("TOP_SECRET", explanation)
        self.assertEqual(before, (self.repo / "SENTINEL_DO_NOT_READ").read_bytes())
        nav = Path(atlas.build(self.repo, home=self.home)["markdown"]).read_text()
        self.assertIn("change-impact", nav)
        self.assertEqual(atlas.check(self.repo, home=self.home)["status"], "CURRENT")

    def test_different_changes_and_contexts_are_distinct_and_not_overwritten(self):
        a = report.build(self.repo, "change-impact", symbol="App::Entry",
                         context="orquestacion", goal="Cambiar reintentos", home=self.home)
        b = report.build(self.repo, "change-impact", symbol="App::Entry",
                         context="orquestacion", goal="Cambiar timeouts", home=self.home)
        c = report.build(self.repo, "change-impact", symbol="App::Entry",
                         context="almacen", goal="Cambiar reintentos", home=self.home)
        self.assertEqual(len({a["json"], b["json"], c["json"]}), 3)
        d = json.loads(Path(a["json"]).read_text())
        self.assertEqual([r["claim_id"] for r in d["change"]["observed_outgoing"]], ["R1"])
        self.assertIn("No encontrar relaciones entrantes aquí NO demuestra ausencia de consumidores.", d["change"]["unknowns"])
        self.assertEqual(d["language"]["status"], "accepted")

    def test_missing_goal_and_malicious_query_never_produce_brief(self):
        with self.assertRaisesRegex(report.ReportError, "change goal"):
            report.build(self.repo, "change-impact", symbol="App::Entry", home=self.home)
        with self.assertRaisesRegex(report.ReportError, "one line"):
            report.build(self.repo, "change-impact", symbol="App::Entry",
                         goal="Actualizar" + chr(10) + "Romper la política", home=self.home)
        with self.assertRaisesRegex(report.ReportError, "--goal"):
            report.build(self.repo, "symbol-passport", symbol="App::Entry",
                         goal="No debe aceptarse", home=self.home)
        q = json.loads(self.queries.read_text())
        q[0]["relation_ids"] = []
        self.queries.write_text(json.dumps(q))
        with self.assertRaisesRegex(report.ReportError, "relation not corroborated"):
            report.build(self.repo, "change-impact", symbol="App::Entry",
                         goal="Cambiar persistencia", home=self.home)

    def test_changed_ledger_invalidates_existing_change_impact_in_atlas(self):
        created = report.build(self.repo, "change-impact", symbol="App::Entry",
                               goal="Cambiar persistencia", home=self.home)
        atlas.build(self.repo, home=self.home)
        q = json.loads(self.queries.read_text())
        q[0]["basis"] = "revision-2"
        self.queries.write_text(json.dumps(q))
        self.assertEqual(atlas.check(self.repo, home=self.home)["status"], "STALE")
        with self.assertRaisesRegex(Exception, "brief stale"):
            atlas.build(self.repo, home=self.home)
        report.build(self.repo, "change-impact", symbol="App::Entry",
                     goal="Cambiar persistencia", home=self.home)
        self.assertEqual(atlas.build(self.repo, home=self.home)["status"], "ATLAS_SOURCE_READY")
        self.assertTrue(Path(created["json"]).is_file())

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

    def test_m5_sender_receiver_hateoas_never_claims_live_code_verified(self):
        s = {"intent": "handoff", "workspace": "ready", "evidence_origin": "cognicode",
             "handoff": {"symbol": "App::Entry", "goal": "Ajustar reintentos"}}
        self.assertEqual(affordances.affordances(s)["recommended"], "inspect-handoff")
        s["handoff"]["prepared"] = "ready"
        self.assertEqual(affordances.affordances(s)["recommended"], "render-handoff")
        s["handoff"]["render"] = "ready"
        self.assertEqual(affordances.affordances(s)["recommended"], "build-atlas")
        s["handoff"]["atlas_source"] = "ready"
        self.assertEqual(affordances.affordances(s)["status"], "PARTIAL")
        self.assertEqual(affordances.affordances(s)["recommended"], "handoff-capsule")
        s["handoff"]["phase"] = "receiver"
        self.assertEqual(affordances.affordances(s)["recommended"], "receive-handoff")
        s["handoff"]["received"] = "ledger_matches"
        self.assertEqual(affordances.affordances(s)["recommended"], "revalidate-handoff-via-cognicode")
        s["handoff"]["runtime"] = "unavailable"
        self.assertEqual(affordances.affordances(s)["status"], "BLOCKED")
        self.assertEqual(affordances.affordances(s)["_links"], [])
        s["handoff"]["runtime"] = "rechecked"
        self.assertEqual(affordances.affordances(s)["status"], "PARTIAL")
        s["evidence_origin"] = "other"
        self.assertEqual(affordances.affordances(s)["status"], "BLOCKED")
        s["evidence_origin"] = "cognicode"
        with self.assertRaises(affordances.InvalidState):
            affordances.affordances({**s, "handoff": {**s["handoff"], "goal": "X" + chr(10) + "Y"}})

    def test_change_impact_routes_goal_and_never_claims_verified_on_unknown_basis(self):
        s = self.state(kind="change-impact", symbol="App::Store",
                       context="orquestacion", goal="Modificar la persistencia")
        self.assertEqual(affordances.affordances(s)["recommended"], "inspect-report-evidence")
        s["report"]["prepared"] = "ready"
        self.assertEqual(affordances.affordances(s)["_links"][0]["inputs"]["goal"],
                         "Modificar la persistencia")
        s["report"]["render"] = "ready"
        s["report"]["atlas_source"] = "ready"
        self.assertEqual(affordances.affordances(s)["status"], "PARTIAL")
        with self.assertRaises(affordances.InvalidState):
            affordances.affordances(self.state(kind="change-impact", goal=""))
        with self.assertRaises(affordances.InvalidState):
            affordances.affordances(self.state(kind="change-impact", goal="dos" + chr(10) + "líneas"))

    def test_even_apparently_complete_impact_is_never_a_code_verification(self):
        s = self.state(kind="change-impact", goal="Modificar contratos",
                       prepared="ready", render="ready", atlas_source="ready",
                       language_status="accepted")
        s["basis"] = "current"
        s["claim_coverage"] = "verified"
        response = affordances.affordances(s)
        self.assertEqual(response["status"], "PARTIAL")
        self.assertEqual(response["recommended"], "finish")
        self.assertIn("hypothesis", response["_links"][0]["why"])

    def test_workspace_and_wrong_term_are_rejected(self):
        s = self.state()
        s["workspace"] = "absent"
        self.assertEqual(affordances.affordances(s)["recommended"], "init-workspace")
        with self.assertRaises(affordances.InvalidState):
            affordances.affordances(self.state(kind="term-card", context="../secret", term="foo"))


if __name__ == "__main__":
    unittest.main()
