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
import evidence_contract as contract
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
        # A claim nobody corroborates is never presented as a fact: it leaves the
        # facts and is named as unproven, so a reader can see the gap.
        data = json.loads(self.queries.read_text())
        data[0]["relation_ids"] = []
        self.queries.write_text(json.dumps(data))
        built = report.build(self.repo, "symbol-passport", symbol="App::Entry", home=self.home)
        forged = json.loads(Path(built["json"]).read_text())
        self.assertNotIn("R1", forged["evidence"]["claim_ids"])
        self.assertEqual(forged["evidence"]["relations"], [])
        self.assertEqual([c["claim_id"] for c in forged["evidence"]["uncorroborated_claims"]], ["R1"])
        markdown = Path(built["markdown"]).read_text()
        self.assertNotIn("App::Entry → App::Store", markdown)
        self.assertIn("R1", markdown)
        data[0]["relation_ids"] = ["edge-1"]
        data[0]["symbol_ids"] = ["Other"]
        self.queries.write_text(json.dumps(data))
        # Without corroborated entity evidence for the target there is no report.
        with self.assertRaisesRegex(report.ReportError, "lacks corroborated"):
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

    def test_handoff_frontier_reuses_existing_cognicode_research_protocol(self):
        goal = "Modificar persistencia sin romper consumidores"
        capsule.build(self.repo, "App::Store", goal, home=self.home)
        first = capsule.build(self.repo, "App::Store", goal, home=self.home,
                              next_step=True)
        self.assertEqual(first["status"], "PARTIAL")
        self.assertEqual(first["action"], "discover-capabilities")
        self.assertFalse(first["runtime_verified"])
        state = {"observation_origin": "cognicode", "research": {
            "question": {"id": "Q-change", "kind": "change_impact",
                         "text": goal, "target": "App::Store", "language": "rust"},
            "catalog": "unknown",
        }}
        location = self.w / "handoffs" / "receiver-state.json"
        location.write_text(json.dumps(state), encoding="utf-8")
        out = capsule.build(self.repo, "App::Store", goal, home=self.home,
                            next_step=True, research_snapshot=location)
        self.assertEqual(out["action"], "discover-capabilities")
        state["research"]["catalog"] = "observed"
        location.write_text(json.dumps(state))
        out = capsule.build(self.repo, "App::Store", goal, home=self.home,
                            next_step=True, research_snapshot=location)
        self.assertEqual(out["action"], "preflight-language")
        self.assertEqual(out["status"], "PARTIAL")
        self.assertFalse(out["runtime_verified"])

    def test_handoff_frontier_blocks_mismatch_other_sources_and_direct_paths(self):
        goal = "Ajustar recuperación"
        capsule.build(self.repo, "App::Entry", goal, home=self.home)
        state = {"observation_origin": "github", "research": {
            "question": {"id": "Q-1", "kind": "change_impact",
                         "text": goal, "target": "App::Entry", "language": "rust"},
            "catalog": "observed"
        }}
        self.assertEqual(capsule.next_question(self.w, "App::Entry", goal,
                                              research_state=state)["status"], "BLOCKED")
        state["observation_origin"] = "cognicode"
        state["research"]["question"]["target"] = "App::Other"
        self.assertEqual(capsule.next_question(self.w, "App::Entry", goal,
                                              research_state=state)["status"], "BLOCKED")
        direct = self.repo / "SENTINEL_DO_NOT_READ"
        with self.assertRaisesRegex(report.ReportError, "outside derived workspace"):
            capsule.build(self.repo, "App::Entry", goal, home=self.home,
                          next_step=True, research_snapshot=direct)
        # No package-specific exception can grant file-reading access if CogniCode fails.
        old = json.loads(self.queries.read_text())
        old[0]["basis"] = "changed-revision"
        self.queries.write_text(json.dumps(old))
        self.assertEqual(capsule.build(self.repo, "App::Entry", goal,
                                      home=self.home, next_step=True)["status"], "PAUSED")

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

    def _with_use(self, *, reference_hits=None):
        queries = json.loads(self.queries.read_text())
        queries.append({
            "query_id": "Q2", "mode": "symbol_context", "status": "ok",
            "source": "cognicode", "observation_plane": "static",
            "symbol_ids": ["App::Entry", "App::Store"],
            "reference_hits": [{"index": 0, "path": "src/entry.rs", "line": 42}]
            if reference_hits is None else reference_hits,
        })
        self.queries.write_text(json.dumps(queries))
        claims = json.loads(self.claims.read_text())
        claims.append({
            "claim_id": "U1", "kind": "relation", "provenance": "OBSERVED_CODE",
            "relation_source": "reference_link", "from_symbol": "App::Entry",
            "to_symbol": "App::Store",
            "reference": {"query_id": "Q2", "index": 0, "path": "src/entry.rs", "line": 42},
            "query_ids": ["Q1", "Q2"], "coverage": "partial",
        })
        self.claims.write_text(json.dumps(claims))

    def test_localised_use_reaches_the_brief_as_a_hypothesis_and_never_as_an_edge(self):
        self._with_use()
        built = report.build(self.repo, "change-impact", symbol="App::Store",
                             goal="Cambiar la persistencia", home=self.home)
        data = json.loads(Path(built["json"]).read_text())
        # It is a use, not an edge.
        self.assertEqual([u["claim_id"] for u in data["evidence"]["uses"]], ["U1"])
        self.assertNotIn("U1", [r["claim_id"] for r in data["evidence"]["relations"]])
        # The brief keeps both classes apart and labels them.
        statuses = {a["relation_claim_id"]: a["status"] for a in data["change"]["potentially_affected"]}
        self.assertEqual(statuses["R1"], "HYPOTHESIS_NOT_VALIDATED")
        self.assertEqual(statuses["U1"], "HYPOTHESIS_REFERENCE_USE_NOT_CALL")
        use = [a for a in data["change"]["potentially_affected"] if a["relation_claim_id"] == "U1"][0]
        self.assertEqual(use["symbol_id"], "App::Entry")
        self.assertEqual(use["reference"],
                         {"query_id": "Q2", "path": "src/entry.rs", "line": 42})
        markdown = Path(built["markdown"]).read_text()
        self.assertIn("Usos entrantes observados", markdown)
        self.assertIn("NO llamadas", markdown)
        self.assertIn("Un uso acredita que un símbolo aparece en ese sitio.", markdown)

    def test_use_without_its_row_leaves_the_facts_and_is_named(self):
        self._with_use(reference_hits=[])
        built = report.build(self.repo, "change-impact", symbol="App::Store",
                             goal="Cambiar la persistencia", home=self.home)
        data = json.loads(Path(built["json"]).read_text())
        self.assertEqual(data["evidence"]["uses"], [])
        self.assertNotIn("U1", data["evidence"]["claim_ids"])
        self.assertEqual([c["claim_id"] for c in data["evidence"]["uncorroborated_claims"]], ["U1"])
        self.assertNotIn("Usos entrantes observados (posibles consumidores, NO llamadas)\n\n- App::Entry",
                         Path(built["markdown"]).read_text())

    def test_engine_impact_declaration_is_shown_and_stays_a_hypothesis(self):
        queries = json.loads(self.queries.read_text())
        queries.append({
            "query_id": "Q3", "mode": "structured", "status": "partial",
            "source": "cognicode", "observation_plane": "static",
            "symbol_ids": ["App::Store"],
            "impact": {"risk_level": "HIGH", "direct_dependents": 1,
                       "total_impacted_symbols": 2, "impacted_files_count": 1,
                       "affected_symbols": ["App::Entry", "App::Store"],
                       "affected_files": ["src/app.rs"]},
            "limitations": ["El impacto declarado es transitivo."],
        })
        self.queries.write_text(json.dumps(queries))
        built = report.build(self.repo, "change-impact", symbol="App::Store",
                             goal="Cambiar la persistencia", home=self.home)
        data = json.loads(Path(built["json"]).read_text())
        self.assertEqual(data["change"]["observed_impact"][0]["risk_level"], "HIGH")
        # The query is cited even though no claim cites it.
        self.assertIn("Q3", data["evidence"]["query_ids"])
        candidates = [a for a in data["change"]["potentially_affected"]
                      if a["status"] == "HYPOTHESIS_ENGINE_IMPACT_TRANSITIVE"]
        self.assertEqual([a["symbol_id"] for a in candidates], ["App::Entry"])
        # The target itself is not a candidate to review.
        self.assertNotIn("App::Store", [a["symbol_id"] for a in candidates])
        markdown = Path(built["markdown"]).read_text()
        self.assertIn("Hechos de impacto declarados por CogniCode", markdown)
        self.assertIn("nivel de riesgo HIGH", markdown)
        self.assertIn("El impacto declarado es transitivo.", markdown)

    def test_query_limitations_reach_the_reader(self):
        queries = json.loads(self.queries.read_text())
        queries[0]["limitations"] = ["La respuesta es parcial."]
        self.queries.write_text(json.dumps(queries))
        built = report.build(self.repo, "symbol-passport", symbol="App::Entry", home=self.home)
        markdown = Path(built["markdown"]).read_text()
        self.assertIn("Límites de las consultas que lo sostienen", markdown)
        self.assertIn("La respuesta es parcial.", markdown)

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
        built = report.build(self.repo, "change-impact", symbol="App::Entry",
                             goal="Cambiar persistencia", home=self.home)
        data = json.loads(Path(built["json"]).read_text())
        # The brief is produced, but it never shows an uncorroborated edge.
        self.assertEqual(data["change"]["observed_incoming"], [])
        self.assertEqual(data["change"]["potentially_affected"], [])
        self.assertNotIn("R1", data["evidence"]["claim_ids"])
        self.assertIn("No hay ninguna arista de grafo corroborada en este ámbito: "
                      "solo se han observado usos localizados.", data["change"]["unknowns"])

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


class ReportBasisRevisionTests(unittest.TestCase):
    """The revision travels from the evidence; it is never assumed."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "code"
        self.repo.mkdir()
        self.home = self.root / "home"
        self.home.mkdir()
        workspace.init(self.repo, home=self.home)
        self.w = Path(workspace.inspect(self.repo, home=self.home)["workspace"])
        self.queries = self.w / "evidence/queries.json"
        self.claims = self.w / "evidence/claims.json"
        self.queries.write_text(json.dumps([
            {"query_id": "Q1", "mode": "structured", "status": "ok",
             "source": "cognicode", "observation_plane": "static",
             "basis": "cognicode-cli 0.101.21 sha=9f3c source=cli",
             "symbol_ids": ["App::Entry", "App::Store"], "relation_ids": ["edge-1"]}
        ]), encoding="utf-8")
        self.claims.write_text(json.dumps([
            {"claim_id": "C1", "kind": "entity", "provenance": "OBSERVED_CODE",
             "symbol_id": "App::Entry", "query_ids": ["Q1"], "coverage": "complete"}
        ]), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def declare(self, query_id, revision=None):
        """Add a supporting query that may declare the revision it looked at."""
        queries = json.loads(self.queries.read_text())
        query = {"query_id": query_id, "mode": "structured", "status": "ok",
                 "source": "cognicode", "observation_plane": "static",
                 "basis": "cognicode-cli 0.101.21 sha=9f3c source=cli",
                 "symbol_ids": ["App::Entry"]}
        if revision is not None:
            query["repository_revision"] = revision
        queries.append(query)
        self.queries.write_text(json.dumps(queries), encoding="utf-8")
        claims = json.loads(self.claims.read_text())
        claims.append({"claim_id": "C-" + query_id, "kind": "entity",
                       "provenance": "OBSERVED_CODE", "symbol_id": "App::Entry",
                       "query_ids": [query_id], "coverage": "complete"})
        self.claims.write_text(json.dumps(claims), encoding="utf-8")

    def basis(self):
        return report.project(self.w, "symbol-passport", symbol="App::Entry")["evidence"]["basis"]

    def test_queries_declaring_the_same_revision_publish_it_in_the_basis(self):
        self.declare("Q2", revision="rev-abc123")
        queries = json.loads(self.queries.read_text())
        queries[0]["repository_revision"] = "rev-abc123"
        self.queries.write_text(json.dumps(queries), encoding="utf-8")
        self.assertEqual(self.basis(),
                         {"identity": "cognicode-cli 0.101.21 sha=9f3c source=cli",
                          "status": "reported_unverified", "revision": "rev-abc123"})
        # The revision does not depend on the engine identity being declared.
        without_identity = [{k: v for k, v in q.items() if k != "basis"} for q in queries]
        self.queries.write_text(json.dumps(without_identity), encoding="utf-8")
        self.assertEqual(self.basis(),
                         {"identity": None, "status": "unknown", "revision": "rev-abc123"})

    def test_queries_declaring_different_revisions_publish_no_revision(self):
        self.declare("Q2", revision="rev-def456")
        queries = json.loads(self.queries.read_text())
        queries[0]["repository_revision"] = "rev-abc123"
        self.queries.write_text(json.dumps(queries), encoding="utf-8")
        basis = self.basis()
        # A conflict is never resolved by choosing one of the declared revisions.
        self.assertNotIn("revision", basis)
        self.assertEqual(basis["status"], "reported_unverified")

    def test_queries_declaring_no_revision_leave_the_basis_key_absent(self):
        self.declare("Q2")
        basis = self.basis()
        # The key is absent, not null: its absence means the revision is unknown.
        self.assertNotIn("revision", basis)
        self.assertEqual(basis, {"identity": "cognicode-cli 0.101.21 sha=9f3c source=cli",
                                 "status": "reported_unverified"})

    def test_a_query_with_a_revision_is_still_valid_for_the_evidence_contract(self):
        queries = json.loads(self.queries.read_text())
        queries[0]["repository_revision"] = "rev-abc123"
        self.queries.write_text(json.dumps(queries), encoding="utf-8")
        self.assertIn("repository_revision", contract.QUERY_OPTIONAL)
        indexed = contract.index_queries(queries)
        claims = contract.index_claims(json.loads(self.claims.read_text()))
        for cid, claim in claims.items():
            with self.subTest(claim=cid):
                self.assertEqual(contract.verdict(claim, indexed)[0], contract.CORROBORATED)
        # A query that omits the optional field is still a valid query.
        without = [{k: v for k, v in q.items() if k != "repository_revision"}
                   for q in queries]
        self.assertTrue(contract.index_queries(without))

    def test_the_report_states_the_declared_revision_without_calling_it_current(self):
        queries = json.loads(self.queries.read_text())
        queries[0]["repository_revision"] = "rev-abc123"
        self.queries.write_text(json.dumps(queries), encoding="utf-8")
        built = report.build(self.repo, "symbol-passport", symbol="App::Entry", home=self.home)
        markdown = Path(built["markdown"]).read_text(encoding="utf-8")
        lines = [line for line in markdown.splitlines() if "rev-abc123" in line]
        self.assertEqual(len(lines), 1)
        for word in ("vigente", "actual"):
            self.assertNotIn(word, lines[0])


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
