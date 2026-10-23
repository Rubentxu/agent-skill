"""Tests for the recorder: the only writer of the ledger.

Version 2 of the contract has one shape and one writer. These tests
protect the three halves of that promise: the payload the agent brings is
facts and not form (old spellings and self-made identifiers are refused),
the shape and the identifier are stamped here, and no ledger is left
published without its derived verdict.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
import evidence_contract as contract
import record
import workspace


class RecorderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "code"
        self.repo.mkdir()
        # The checkout is unreadable by contract; the recorder must not
        # need it either.
        (self.repo / "SENTINEL_DO_NOT_READ").write_text("TOP_SECRET", encoding="utf-8")
        self.home = self.root / "home"
        self.home.mkdir()
        workspace.init(self.repo, home=self.home)
        self.w = Path(workspace.inspect(self.repo, home=self.home)["workspace"])
        self.queries = self.w / "evidence/queries.json"
        self.claims = self.w / "evidence/claims.json"
        self.corroboration = self.w / "evidence/corroboration.json"

    def tearDown(self):
        self.tmp.cleanup()

    def payload(self, content, name="payload.json"):
        path = self.root / name
        path.write_text(json.dumps(content), encoding="utf-8")
        return str(path)

    def consulta(self, **extra):
        facts = {"mode": "structured", "status": "ok", "source": "cognicode",
                 "observation_plane": "static", "operation": "find_usages",
                 "symbol_ids": ["App::Entry"]}
        facts.update(extra)
        return facts

    def afirmacion(self, **extra):
        facts = {"kind": "entity", "provenance": "OBSERVED_CODE", "plane": "static",
                 "coverage": "complete", "symbol_id": "App::Entry",
                 "query_ids": ["Q-1"]}
        facts.update(extra)
        return facts

    def registrar_consulta(self, facts):
        return record.main(["query", "--repo", str(self.repo), "--home",
                            str(self.home), "--payload", self.payload(facts, "q.json")])

    def registrar_afirmacion(self, facts):
        return record.main(["claim", "--repo", str(self.repo), "--home",
                            str(self.home), "--payload", self.payload(facts, "c.json")])

    def leer(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_registra_una_consulta_en_un_workspace_nuevo(self):
        self.assertEqual(self.registrar_consulta(self.consulta()), 0)
        material = self.leer(self.queries)
        self.assertEqual(material["schema_version"], contract.CONTRACT_VERSION)
        self.assertEqual(len(material["queries"]), 1)
        registrada = material["queries"][0]
        self.assertEqual(registrada["query_id"], "Q-1")
        for field in ("mode", "status", "source", "observation_plane", "symbol_ids"):
            self.assertIn(field, registrada, field)

    def test_registra_una_afirmacion_y_publica_el_veredicto(self):
        self.assertEqual(self.registrar_consulta(self.consulta()), 0)
        self.assertEqual(self.registrar_afirmacion(self.afirmacion()), 0)
        material = self.leer(self.claims)
        self.assertEqual(material["schema_version"], contract.CONTRACT_VERSION)
        self.assertEqual(material["claims"][0]["claim_id"], "C-1")
        # El veredicto viaja con el material: registrar deja publicado lo
        # que la afirmacion gana, no solo la afirmacion.
        self.assertTrue(self.corroboration.is_file(),
                        "registrar publica el veredicto derivado")
        verdict = self.leer(self.corroboration)
        self.assertEqual(verdict["counts"]["corroborated"], 1)

    def test_registrar_un_hecho_sin_corroborar_no_es_un_fallo(self):
        # Registrar anota hechos; comprobar es otro paso. El registro sale
        # bien y el veredicto dice lo que dice.
        self.assertEqual(self.registrar_consulta(self.consulta()), 0)
        self.assertEqual(self.registrar_afirmacion(
            self.afirmacion(symbol_id="App::Other")), 0)
        verdict = self.leer(self.corroboration)
        self.assertEqual(verdict["counts"]["observed_not_corroborated"], 1)

    def test_la_afirmacion_cuya_consulta_no_existe_se_rechaza(self):
        self.registrar_consulta(self.consulta())
        self.assertEqual(self.registrar_afirmacion(
            self.afirmacion(query_ids=["Q-99"])), 2)
        # El libro par existe desde la primera consulta — el veredicto se
        # deriva de los dos — pero la afirmacion rechazada no entra en el.
        self.assertEqual(self.leer(self.claims)["claims"], [],
                         "una afirmacion que cita consultas que no existen no se registra")

    def test_el_payload_con_grafia_antigua_se_rechaza(self):
        # La forma la decide el registro: el payload trae hechos, no forma.
        self.assertEqual(self.registrar_afirmacion(
            self.afirmacion(id="C-9")), 2)
        self.assertEqual(self.registrar_afirmacion(
            self.afirmacion(status="OBSERVED_CODE")), 2)
        self.assertEqual(self.registrar_consulta(
            self.consulta(id="Q-9")), 2)
        self.assertFalse(self.claims.is_file())
        self.assertFalse(self.queries.is_file())

    def test_el_payload_que_trae_su_identificador_se_rechaza(self):
        # El identificador lo sella el registro, y lo sella una sola vez.
        self.assertEqual(self.registrar_consulta(
            self.consulta(query_id="Q-1")), 2)
        self.assertEqual(self.registrar_afirmacion(
            self.afirmacion(claim_id="C-1")), 2)
        self.assertFalse(self.queries.is_file())
        self.assertFalse(self.claims.is_file())

    def test_el_payload_sin_lo_requerido_se_rechaza(self):
        incompleta = self.consulta()
        incompleta.pop("mode")
        self.assertEqual(self.registrar_consulta(incompleta), 2)
        self.assertFalse(self.queries.is_file())

    def test_la_afirmacion_de_entidad_sin_simbolo_se_rechaza(self):
        self.registrar_consulta(self.consulta())
        sin_simbolo = self.afirmacion()
        sin_simbolo.pop("symbol_id")
        self.assertEqual(self.registrar_afirmacion(sin_simbolo), 2)
        self.assertEqual(self.leer(self.claims)["claims"], [])

    def test_las_enumeraciones_invalidas_se_rechazan(self):
        # Un estado que el contrato no conoce es una afirmacion que nadie
        # sabra leer despues: mejor no dejarla entrar.
        self.assertEqual(self.registrar_consulta(self.consulta(status="FINE")), 2)
        self.assertEqual(self.registrar_afirmacion(self.afirmacion(coverage="TOTAL")), 2)
        self.assertEqual(self.registrar_afirmacion(
            self.afirmacion(provenance="SAW_IT")), 2)
        self.assertFalse(self.queries.is_file())
        self.assertFalse(self.claims.is_file())

    def test_una_relacion_con_referencia_se_registra_y_se_corrobora(self):
        self.assertEqual(self.registrar_consulta(self.consulta(
            symbol_ids=["App::Entry", "App::Store"],
            reference_hits=[{"index": 0, "path": "src/app.rs", "line": 3}])), 0)
        relacion = {"kind": "relation", "provenance": "OBSERVED_CODE",
                    "plane": "static", "coverage": "partial",
                    "relation_source": "reference_link",
                    "from_symbol": "App::Entry", "to_symbol": "App::Store",
                    "query_ids": ["Q-1"],
                    "reference": {"query_id": "Q-1", "index": 0,
                                  "path": "src/app.rs", "line": 3}}
        self.assertEqual(self.registrar_afirmacion(relacion), 0)
        verdict = self.leer(self.corroboration)
        self.assertEqual(verdict["counts"]["corroborated"], 1)

    def test_una_relacion_graph_edge_incompleta_se_rechaza(self):
        self.registrar_consulta(self.consulta())
        incompleta = {"kind": "relation", "provenance": "OBSERVED_CODE",
                      "plane": "static", "coverage": "partial",
                      "relation_source": "graph_edge",
                      "from_symbol": "App::Entry", "to_symbol": "App::Store",
                      "query_ids": ["Q-1"]}
        self.assertEqual(self.registrar_afirmacion(incompleta), 2)
        self.assertEqual(self.leer(self.claims)["claims"], [])

    def test_el_registro_migra_el_material_legado_que_se_puede_renovar(self):
        legado = {"schema_version": 1, "queries": [
            {"id": "Q-1", "mode": "structured", "status": "ok",
             "source": "cognicode", "observation_plane": "static",
             "symbol_ids": ["App::Entry"]}]}
        self.queries.write_text(json.dumps(legado), encoding="utf-8")
        self.assertEqual(self.registrar_consulta(
            self.consulta(symbol_ids=["App::Store"])), 0)
        renovado = self.leer(self.queries)
        self.assertEqual(renovado["schema_version"], contract.CONTRACT_VERSION)
        # La grafia antigua se renombro, no se perdio, y la nueva entrada
        # siguio a la que ya estaba.
        self.assertEqual(renovado["queries"][0]["query_id"], "Q-1")
        self.assertNotIn("id", renovado["queries"][0])
        self.assertEqual(renovado["queries"][1]["query_id"], "Q-2")

    def test_el_registro_se_niega_a_renovar_lo_irreparable(self):
        roto = {"schema_version": 1, "queries": [
            {"id": "Q-1", "status": "ok", "source": "cognicode",
             "observation_plane": "static", "symbol_ids": ["App::Entry"]}]}
        self.queries.write_text(json.dumps(roto), encoding="utf-8")
        antes = self.queries.read_bytes()
        self.assertEqual(self.registrar_consulta(self.consulta()), 2)
        self.assertEqual(self.queries.read_bytes(), antes,
                         "lo que no se puede renovar sin perder no se toca")

    def test_el_identificador_sellado_no_pisa_a_los_que_hay(self):
        material = {"schema_version": contract.CONTRACT_VERSION, "queries": [
            {"query_id": "Q-1", "mode": "structured", "status": "ok",
             "source": "cognicode", "observation_plane": "static",
             "symbol_ids": ["App::Entry"]},
            {"query_id": "Q-3", "mode": "structured", "status": "ok",
             "source": "cognicode", "observation_plane": "static",
             "symbol_ids": ["App::Store"]}]}
        self.queries.write_text(json.dumps(material), encoding="utf-8")
        self.assertEqual(self.registrar_consulta(
            self.consulta(symbol_ids=["App::Other"])), 0)
        self.assertEqual(self.leer(self.queries)["queries"][2]["query_id"], "Q-4")

    def test_un_payload_que_no_es_un_objeto_se_rechaza(self):
        path = self.payload(["no", "soy", "un", "objeto"], "lista.json")
        self.assertEqual(record.main(["query", "--repo", str(self.repo), "--home",
                                      str(self.home), "--payload", path]), 2)
        self.assertFalse(self.queries.is_file())

    def test_el_registro_no_lee_el_checkout(self):
        self.registrar_consulta(self.consulta())
        self.registrar_afirmacion(self.afirmacion())
        self.assertFalse((self.w / "SENTINEL_DO_NOT_READ").exists())


if __name__ == "__main__":
    unittest.main()
