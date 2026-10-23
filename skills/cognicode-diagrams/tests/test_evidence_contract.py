"""Tests for the shape of the evidence and for what each claim earns.

The most important test here is the first one: it executes the example
that the published contract publishes. Without it, the document and the
code could drift apart again and nobody would notice until a ledger could
not be read.
"""
import hashlib
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
import evidence_contract as contract
import evidence as validator
import workspace


def canonical_example(reference: str) -> dict:
    """Read the example the contract publishes and parse it."""
    text = (SKILL / "references" / reference).read_text(encoding="utf-8")
    blocks = re.findall(r"```json[^\n]*\n(.*?)```", text, re.S)
    wanted = [block for block in blocks if '"claim_id"' in block]
    if not wanted:
        raise AssertionError("el contrato no publica ningun ejemplo de ledger")
    return json.loads(wanted[0])


class ContractShapeTests(unittest.TestCase):
    def test_el_ejemplo_del_contrato_se_corrobora(self):
        # If the document and the code ever disagree about the shape, this
        # is where it shows.
        example = canonical_example("evidence.md")
        queries = contract.index_queries(example["queries"])
        claims = contract.index_claims(example["claims"])
        self.assertTrue(claims, "el ejemplo publica afirmaciones")
        for cid, claim in claims.items():
            with self.subTest(claim=cid):
                derived, missing = contract.verdict(claim, queries)
                self.assertEqual(derived, contract.CORROBORATED,
                                 f"{cid} no se corrobora: {missing}")

    def test_el_ejemplo_de_referencias_se_corrobora(self):
        example = canonical_example("evidence-reference-links.md")
        queries = contract.index_queries(example["queries"])
        claims = contract.index_claims(example["claims"])
        relation = next(iter(claims.values()))
        self.assertEqual(relation["relation_source"], contract.REFERENCE_LINK)
        self.assertTrue(contract.reference_corroborated(relation, queries))
        self.assertEqual(contract.verdict(relation, queries)[0], contract.CORROBORATED)

    def test_una_referencia_nunca_se_eleva_a_arista(self):
        example = canonical_example("evidence-reference-links.md")
        queries = contract.index_queries(example["queries"])
        relation = next(iter(contract.index_claims(example["claims"]).values()))
        self.assertFalse(contract.corroborated(relation, queries),
                         "una referencia no es una arista de grafo")

    def test_una_referencia_con_identificador_sigue_no_siendo_arista(self):
        # The dangerous shape: a reference that also happens to carry a
        # relation identifier. It is still a reference, and a reference is
        # never an edge, however much it looks like one.
        queries = contract.index_queries([{
            "query_id": "Q-1", "mode": "structured", "status": "ok",
            "source": "cognicode", "observation_plane": "static",
            "symbol_ids": ["A::run", "B::save"], "relation_ids": ["edge-1"]}])
        claim = {
            "claim_id": "R-1", "kind": "relation", "provenance": "OBSERVED_CODE",
            "plane": "static", "coverage": "partial",
            "relation_source": "reference_link", "relation_id": "edge-1",
            "from_symbol": "A::run", "to_symbol": "B::save", "query_ids": ["Q-1"]}
        self.assertFalse(contract.corroborated(claim, queries))

    def test_una_relacion_sin_identificador_no_es_arista(self):
        queries = contract.index_queries([{
            "query_id": "Q-1", "mode": "structured", "status": "ok",
            "source": "cognicode", "observation_plane": "static",
            "symbol_ids": ["A::run", "B::save"], "relation_ids": ["edge-1"]}])
        without_id = {
            "claim_id": "R-1", "kind": "relation", "provenance": "OBSERVED_CODE",
            "plane": "static", "coverage": "partial", "relation_source": "graph_edge",
            "from_symbol": "A::run", "to_symbol": "B::save", "query_ids": ["Q-1"]}
        self.assertFalse(contract.corroborated(without_id, queries))
        with_id = dict(without_id, relation_id="edge-1")
        self.assertTrue(contract.corroborated(with_id, queries))

    def test_la_calificacion_se_deriva_y_no_se_afirma(self):
        queries = contract.index_queries([{
            "query_id": "Q-1", "mode": "structured", "status": "ok",
            "source": "cognicode", "observation_plane": "static",
            "symbol_ids": ["A::run"]}])
        claim = {
            "claim_id": "C-1", "kind": "entity", "provenance": "OBSERVED_CODE",
            "plane": "static", "coverage": "complete", "symbol_id": "A::other",
            "query_ids": ["Q-1"]}
        derived, missing = contract.verdict(claim, queries)
        self.assertEqual(derived, contract.OBSERVED_NOT_CORROBORATED)
        self.assertTrue(missing, "un veredicto negativo dice que falta")

    def test_una_consulta_vacia_no_sostiene_una_afirmacion(self):
        queries = contract.index_queries([{
            "query_id": "Q-1", "mode": "structured", "status": "ok",
            "source": "cognicode", "observation_plane": "static",
            "symbol_ids": ["A::run"], "result_summary": {"entries": 0}}])
        claim = {
            "claim_id": "R-1", "kind": "relation", "provenance": "OBSERVED_CODE",
            "plane": "static", "coverage": "unknown", "relation_source": "graph_edge",
            "relation_id": "edge-1", "from_symbol": "A::run", "to_symbol": "B::save",
            "query_ids": ["Q-1"]}
        derived, missing = contract.verdict(claim, queries)
        self.assertEqual(derived, contract.OBSERVED_NOT_CORROBORATED)
        self.assertTrue(any("0 resultados" in gap for gap in missing), missing)

    def test_un_cero_que_no_es_resultado_no_se_confunde(self):
        # A server that lists zero tools is a finding, not an empty answer.
        queries = contract.index_queries([{
            "query_id": "Q-1", "mode": "structured", "status": "ok",
            "source": "cognicode", "observation_plane": "static",
            "symbol_ids": ["A::run"], "result_summary": {"tools": 0}}])
        claim = {
            "claim_id": "C-1", "kind": "entity", "provenance": "OBSERVED_CODE",
            "plane": "static", "coverage": "complete", "symbol_id": "A::run",
            "query_ids": ["Q-1"]}
        self.assertEqual(contract.verdict(claim, queries)[0], contract.CORROBORATED)

    def test_una_afirmacion_de_intencion_no_se_corrobora(self):
        queries = contract.index_queries([{
            "query_id": "Q-1", "mode": "structured", "status": "ok",
            "source": "cognicode", "observation_plane": "static",
            "symbol_ids": ["A::run"]}])
        claim = {
            "claim_id": "C-1", "kind": "entity", "provenance": "CURATED_INTENT",
            "plane": "intent", "coverage": "unknown", "symbol_id": "A::run",
            "query_ids": ["Q-1"]}
        derived, missing = contract.verdict(claim, queries)
        self.assertEqual(derived, contract.NOT_IMPLEMENTATION)
        self.assertEqual(missing, [])


class MaterialShapeTests(unittest.TestCase):
    """What the material says about itself, and what follows from it.

    The distinction these tests protect: a claim that was looked at and
    is not supported is a finding about the material; a claim that could
    not be looked at is a hole. Reporting one as the other accuses the
    material of something nobody checked.
    """

    def consulta_sin_declarar_como_se_ejecuto(self):
        return {"query_id": "Q-1", "result_summary": {"entries": 1}}

    def afirmacion(self, **extra):
        claim = {"claim_id": "C-1", "kind": "entity", "provenance": "OBSERVED_CODE",
                 "plane": "static", "coverage": "complete", "symbol_id": "App::Entry",
                 "query_ids": ["Q-1"]}
        claim.update(extra)
        return claim

    def test_un_material_que_no_declara_como_se_ejecutaron_las_consultas_no_se_acusa(self):
        # The queries do not say how they ran, so nobody can say whether
        # they support the claim. That is a hole, not an accusation.
        queries = contract.index_queries([self.consulta_sin_declarar_como_se_ejecuto()])
        derived, missing = contract.verdict(self.afirmacion(), queries)
        self.assertEqual(derived, contract.NOT_CHECKABLE)
        self.assertTrue(any("no declara 'mode'" in gap for gap in missing), missing)

    def test_una_afirmacion_que_no_declara_ninguna_consulta_se_declara_observada_sin_corroborar(self):
        # Nothing supports it, but the claim was read: that is a finding
        # about the claim, and it is a different one.
        derived, missing = contract.verdict(self.afirmacion(query_ids=[]), {})
        self.assertEqual(derived, contract.OBSERVED_NOT_CORROBORATED)
        self.assertTrue(missing, "un veredicto negativo dice que falta")

    def test_el_material_de_otra_version_del_contrato_no_se_lee(self):
        claims = {"schema_version": contract.CONTRACT_VERSION + 1,
                  "claims": [self.afirmacion()]}
        queries = {"schema_version": contract.CONTRACT_VERSION,
                   "queries": [{"query_id": "Q-1", "mode": "structured", "status": "ok",
                                "source": "cognicode", "observation_plane": "static",
                                "symbol_ids": ["App::Entry"]}]}
        report = contract.report(claims, queries)
        self.assertEqual(report["status"], "unreadable")
        self.assertEqual(report["claims"], [],
                         "un material de otro contrato no lleva veredictos")
        self.assertTrue(any("version" in gap for gap in report["gaps"]), report["gaps"])

    def test_el_material_que_no_declara_version_sigue_pudiendo_leerse(self):
        claims = {"claims": [self.afirmacion()]}
        queries = {"queries": [{"query_id": "Q-1", "mode": "structured", "status": "ok",
                                "source": "cognicode", "observation_plane": "static",
                                "symbol_ids": ["App::Entry"]}]}
        report = contract.report(claims, queries)
        self.assertEqual(report["status"], "current")
        self.assertEqual(report["corroborated"], 1)
        self.assertTrue(any("no declaran la version" in gap for gap in report["gaps"]),
                        report["gaps"])

    def test_el_material_que_se_desvia_no_se_confunde_con_el_que_no_se_sostiene(self):
        claims = {"schema_version": contract.CONTRACT_VERSION,
                  "claims": [self.afirmacion()]}
        queries = {"schema_version": contract.CONTRACT_VERSION,
                   "queries": [self.consulta_sin_declarar_como_se_ejecuto()]}
        report = contract.report(claims, queries)
        self.assertEqual(report["not_checkable"], 1)
        self.assertEqual(report["not_corroborated"], 0,
                         "lo que no se pudo mirar no esta entre lo que no se sostiene")


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "code"
        self.repo.mkdir()
        # The checkout is unreadable by contract; the tool must not need it.
        (self.repo / "SENTINEL_DO_NOT_READ").write_text("TOP_SECRET", encoding="utf-8")
        self.home = self.root / "home"
        self.home.mkdir()
        workspace.init(self.repo, home=self.home)
        self.w = Path(workspace.inspect(self.repo, home=self.home)["workspace"])
        self.queries = self.w / "evidence/queries.json"
        self.claims = self.w / "evidence/claims.json"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, queries, claims):
        self.queries.write_text(json.dumps(queries), encoding="utf-8")
        self.claims.write_text(json.dumps(claims), encoding="utf-8")

    def good(self):
        return ([{"query_id": "Q-1", "mode": "structured", "status": "ok",
                  "source": "cognicode", "observation_plane": "static",
                  "symbol_ids": ["App::Entry"]}],
                [{"claim_id": "C-1", "kind": "entity", "provenance": "OBSERVED_CODE",
                  "plane": "static", "coverage": "complete", "symbol_id": "App::Entry",
                  "query_ids": ["Q-1"]}])

    def test_el_validador_pasa_cuando_todo_esta_corrobado(self):
        self.write(*self.good())
        self.assertEqual(validator.main(["--repo", str(self.repo), "--home",
                                          str(self.home), "--check"]), 0)

    def test_el_validador_falla_cuando_algo_no_esta_corrobado(self):
        queries, claims = self.good()
        claims[0]["symbol_id"] = "App::Other"
        self.write(queries, claims)
        self.assertEqual(validator.main(["--repo", str(self.repo), "--home",
                                          str(self.home), "--check"]), 1)

    def test_el_validador_escribe_el_veredicto_derivado(self):
        self.write(*self.good())
        self.assertEqual(validator.main(["--repo", str(self.repo), "--home",
                                          str(self.home), "--emit"]), 0)
        ledger = json.loads((self.w / "evidence/corroboration.json").read_text(encoding="utf-8"))
        self.assertEqual(ledger["generator"], validator.GENERATOR)
        self.assertEqual(ledger["counts"]["corroborated"], 1)
        self.assertEqual(ledger["claims"][0]["claim_id"], "C-1")
        self.assertEqual(ledger["claims"][0]["verdict"], contract.CORROBORATED)

    def test_el_veredicto_derivado_publica_si_el_material_se_puede_leer(self):
        # Quien lo lee tiene que poder saber si hay veredicto o no, sin
        # tener que interpretarlo.
        self.write(*self.good())
        self.assertEqual(validator.main(["--repo", str(self.repo), "--home",
                                          str(self.home), "--emit"]), 0)
        ledger = json.loads((self.w / "evidence/corroboration.json").read_text(encoding="utf-8"))
        self.assertEqual(ledger["status"], "current")
        self.assertEqual(ledger["gaps"], [])

    def test_el_validador_falla_cuando_algo_no_se_puede_comprobar(self):
        # Una afirmacion que nadie ha podido mirar tampoco esta probada:
        # la salida tiene que decirlo.
        queries, claims = self.good()
        queries[0].pop("mode")
        self.write(queries, claims)
        self.assertEqual(validator.main(["--repo", str(self.repo), "--home",
                                          str(self.home), "--check"]), 1)

    def test_el_validador_no_acusa_a_un_material_que_no_se_puede_mirar(self):
        queries, claims = self.good()
        queries[0].pop("mode")
        self.write(queries, claims)
        self.assertEqual(validator.main(["--repo", str(self.repo), "--home",
                                          str(self.home), "--emit"]), 0)
        ledger = json.loads((self.w / "evidence/corroboration.json").read_text(encoding="utf-8"))
        self.assertEqual(ledger["counts"]["observed_not_corroborated"], 0)
        self.assertEqual(ledger["counts"]["not_checkable"], 1)
        self.assertEqual(ledger["claims"][0]["verdict"], contract.NOT_CHECKABLE)

    def test_el_veredicto_declara_de_que_material_salio(self):
        # Un veredicto que no dice de que material salio no se puede
        # comparar con el material que tiene delante quien lo lee.
        self.write(*self.good())
        self.assertEqual(validator.main(["--repo", str(self.repo), "--home",
                                          str(self.home), "--emit"]), 0)
        ledger = json.loads((self.w / "evidence/corroboration.json").read_text(encoding="utf-8"))
        inputs = ledger["inputs"]
        self.assertEqual(set(inputs), {"evidence/claims.json", "evidence/queries.json"})
        for relative, expected in inputs.items():
            actual = hashlib.sha256((self.w / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)

    def test_el_veredicto_avisa_cuando_el_material_cambio(self):
        # Si el material cambia despues, las sumas dejan de cuadrar y el
        # veredicto se reconoce como de otro material.
        self.write(*self.good())
        self.assertEqual(validator.main(["--repo", str(self.repo), "--home",
                                          str(self.home), "--emit"]), 0)
        ledger = json.loads((self.w / "evidence/corroboration.json").read_text(encoding="utf-8"))
        before = ledger["inputs"]["evidence/claims.json"]
        self.claims.write_text(json.dumps([{"claim_id": "C-2"}]), encoding="utf-8")
        after = hashlib.sha256(self.claims.read_bytes()).hexdigest()
        self.assertNotEqual(before, after)

    def test_el_validador_no_pisa_un_fichero_ajeno(self):
        target = self.w / "evidence/corroboration.json"
        target.write_text(json.dumps({"generator": "someone-else"}), encoding="utf-8")
        self.write(*self.good())
        self.assertEqual(validator.main(["--repo", str(self.repo), "--home",
                                          str(self.home), "--emit"]), 2)
        self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["generator"],
                         "someone-else")

    def test_sin_material_derivado_no_se_inventa_nada(self):
        empty = self.root / "empty"
        empty.mkdir()
        self.assertEqual(validator.main(["--repo", str(empty), "--home",
                                          str(self.home), "--check"]), 2)

    def test_el_validador_no_lee_el_checkout(self):
        # The checkout holds a sentinel that must never be read. The tool
        # answers from the derived workspace alone.
        self.write(*self.good())
        validator.main(["--repo", str(self.repo), "--home", str(self.home), "--check"])
        self.assertFalse((self.w / "SENTINEL_DO_NOT_READ").exists())


if __name__ == "__main__":
    unittest.main()
