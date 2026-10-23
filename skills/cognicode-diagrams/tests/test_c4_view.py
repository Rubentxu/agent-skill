"""Tests for the C4 derived view: the view as data, traced to the ledger.

The selection is curated — which claims make a view, which C4 question it
answers, which class each element has. The view is derived: a projector
reads the ledger and publishes elements, relations and holes, with the
digests of the material it came from and the basis its queries declare.
Nothing in the view is written by hand.
"""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
import c4_view
import evidence_contract as contract
import workspace


def bloque_json(relativa: str, marca: str) -> dict:
    """Read one JSON block the documents publish, by its mark."""
    import re
    text = (Path(__file__).resolve().parent / relativa).read_text(encoding="utf-8")
    if marca in {"seleccion", "vista"}:
        blocks = re.findall(r"```json " + marca + r"\n(.*?)```", text, re.S)
    else:
        blocks = [b for b in re.findall(r"```json[^\n]*\n(.*?)```", text, re.S)
                  if f'"{marca}"' in b]
    if not blocks:
        raise AssertionError(f"el documento no publica el bloque esperado ({marca})")
    return json.loads(blocks[0])


class C4ViewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "code"
        self.repo.mkdir()
        # The checkout is unreadable by contract; the projector must not
        # need it either.
        (self.repo / "SENTINEL_DO_NOT_READ").write_text("TOP_SECRET", encoding="utf-8")
        self.home = self.root / "home"
        self.home.mkdir()
        workspace.init(self.repo, home=self.home)
        self.w = Path(workspace.inspect(self.repo, home=self.home)["workspace"])
        self.queries = self.w / "evidence/queries.json"
        self.claims = self.w / "evidence/claims.json"
        self.reports = self.w / "lenses/c4/reports"
        self.reports.mkdir(parents=True, exist_ok=True)
        self.views = self.w / "lenses/c4/views"

    def tearDown(self):
        self.tmp.cleanup()

    # -- material helpers ---------------------------------------------------

    def consulta(self, qid="Q-1", symbols=("App::Entry",), **extra):
        query = {"query_id": qid, "mode": "structured", "status": "ok",
                 "source": "cognicode", "observation_plane": "static",
                 "symbol_ids": list(symbols),
                 "basis": "cognicode-cli 0.101.25 sha=abc",
                 "repository_revision": "rev-abc123"}
        query.update(extra)
        return query

    def entidad(self, cid="C-1", symbol="App::Entry", **extra):
        claim = {"claim_id": cid, "kind": "entity", "provenance": "OBSERVED_CODE",
                 "plane": "static", "coverage": "complete",
                 "symbol_id": symbol, "query_ids": ["Q-1"]}
        claim.update(extra)
        return claim

    def arista(self, cid="R-1", src="App::Entry", dst="App::Store", **extra):
        claim = {"claim_id": cid, "kind": "relation", "provenance": "OBSERVED_CODE",
                 "plane": "static", "coverage": "complete",
                 "relation_source": "graph_edge", "relation_id": "edge-1",
                 "from_symbol": src, "to_symbol": dst, "query_ids": ["Q-2"]}
        claim.update(extra)
        return claim

    def escribir_ledger(self, queries, claims):
        self.queries.write_text(json.dumps(
            {"schema_version": contract.CONTRACT_VERSION, "queries": queries}),
            encoding="utf-8")
        self.claims.write_text(json.dumps(
            {"schema_version": contract.CONTRACT_VERSION, "claims": claims}),
            encoding="utf-8")

    def seleccion(self, claim_ids, kinds, question="C2", name="prueba", **extra):
        seleccion = {"schema_version": 1, "lens": "c4", "question": question,
                     "label": "Vista de prueba", "claim_ids": list(claim_ids),
                     "kinds": dict(kinds)}
        seleccion.update(extra)
        (self.reports / f"{name}.atlas.json").write_text(
            json.dumps(seleccion, ensure_ascii=False, indent=2), encoding="utf-8")
        return name

    def derivar(self, name="prueba", emit=False):
        args = ["--repo", str(self.repo), "--home", str(self.home), "--view", name]
        if emit:
            args.append("--emit")
        return c4_view.main(args)

    def derivada(self, name="prueba"):
        return json.loads((self.views / f"{name}.json").read_text(encoding="utf-8"))

    # -- the derivation -----------------------------------------------------

    def test_un_elemento_deriva_con_su_simbolo_su_clase_y_su_sitio(self):
        self.escribir_ledger(
            [self.consulta(symbol_ids=["App::Entry", "App::Store"],
                           symbol_locations={"App::Entry": {"path": "src/entry.rs", "line": 10}}),
             self.consulta(qid="Q-2", symbols=("App::Store",))],
            [self.entidad(), self.entidad(cid="C-2", symbol="App::Store",
                                          query_ids=["Q-2"])])
        self.seleccion(["C-1", "C-2"], {"C-1": "component", "C-2": "container"})
        self.assertEqual(self.derivar(), 0)
        vista = c4_view.derive(self.w, "prueba")
        self.assertEqual(len(vista["elements"]), 2)
        entry = next(e for e in vista["elements"] if e["id"] == "App::Entry")
        self.assertEqual(entry["kind"], "component")
        self.assertEqual(entry["claim_ids"], ["C-1"])
        self.assertEqual(entry["location"], {"path": "src/entry.rs", "line": 10})
        store = next(e for e in vista["elements"] if e["id"] == "App::Store")
        self.assertEqual(store["kind"], "container")
        self.assertNotIn("location", store)

    def test_dos_afirmaciones_del_mismo_simbolo_son_un_elemento(self):
        self.escribir_ledger(
            [self.consulta(symbol_ids=["App::Entry"])],
            [self.entidad(), self.entidad(cid="C-2", coverage="partial")])
        self.seleccion(["C-1", "C-2"], {"C-1": "component", "C-2": "component"})
        self.assertEqual(self.derivar(), 0)
        vista = c4_view.derive(self.w, "prueba")
        self.assertEqual(len(vista["elements"]), 1)
        self.assertEqual(vista["elements"][0]["claim_ids"], ["C-1", "C-2"])
        self.assertEqual(vista["elements"][0]["coverage"], "partial")

    def test_una_arista_corroborada_pasa_con_su_identificador(self):
        self.escribir_ledger(
            [self.consulta(symbol_ids=["App::Entry", "App::Store"]),
             self.consulta(qid="Q-2", symbol_ids=["App::Entry", "App::Store"],
                           relation_ids=["edge-1"])],
            [self.entidad(), self.entidad(cid="C-2", symbol="App::Store",
                                          query_ids=["Q-1"]),
             self.arista()])
        self.seleccion(["C-1", "C-2", "R-1"],
                       {"C-1": "component", "C-2": "component"})
        self.assertEqual(self.derivar(), 0)
        vista = c4_view.derive(self.w, "prueba")
        self.assertEqual(len(vista["relations"]), 1)
        arista = vista["relations"][0]
        self.assertEqual((arista["source"], arista["target"]),
                         ("App::Entry", "App::Store"))
        self.assertEqual(arista["claim_id"], "R-1")
        self.assertEqual(arista["relation_id"], "edge-1")

    def test_una_referencia_es_un_hueco_nunca_una_arista(self):
        referencia = {"claim_id": "R-2", "kind": "relation",
                      "provenance": "OBSERVED_CODE", "plane": "static",
                      "coverage": "partial", "relation_source": "reference_link",
                      "from_symbol": "App::Entry", "to_symbol": "App::Store",
                      "query_ids": ["Q-1"],
                      "reference": {"query_id": "Q-1", "index": 0,
                                    "path": "src/entry.rs", "line": 3}}
        self.escribir_ledger(
            [self.consulta(symbol_ids=["App::Entry", "App::Store"],
                           reference_hits=[{"index": 0, "path": "src/entry.rs", "line": 3}])],
            [self.entidad(), self.entidad(cid="C-2", symbol="App::Store"),
             referencia])
        self.seleccion(["C-1", "C-2", "R-2"],
                       {"C-1": "component", "C-2": "component"})
        self.assertEqual(self.derivar(), 0)
        vista = c4_view.derive(self.w, "prueba")
        self.assertEqual(vista["relations"], [])
        self.assertEqual(len(vista["holes"]), 1)
        self.assertIn("referencia", vista["holes"][0]["reason"])

    def test_una_afirmacion_no_corroborada_es_un_hueco_con_motivo(self):
        self.escribir_ledger(
            [self.consulta(symbol_ids=["App::Entry"])],
            [self.entidad(symbol="App::Other")])
        self.seleccion(["C-1"], {"C-1": "component"})
        self.assertEqual(self.derivar(), 0)
        vista = c4_view.derive(self.w, "prueba")
        self.assertEqual(vista["elements"], [])
        self.assertEqual(len(vista["holes"]), 1)
        self.assertTrue(vista["holes"][0]["reason"],
                        "un hueco dice por qué no está")

    def test_una_afirmacion_que_no_esta_en_el_ledger_es_un_hueco(self):
        self.escribir_ledger([self.consulta()], [self.entidad()])
        self.seleccion(["C-1", "C-99"], {"C-1": "component", "C-99": "component"})
        self.assertEqual(self.derivar(), 0)
        vista = c4_view.derive(self.w, "prueba")
        self.assertEqual(vista["holes"][0]["claim_id"], "C-99")

    def test_un_elemento_sin_clase_en_la_seleccion_es_un_hueco(self):
        self.escribir_ledger([self.consulta()], [self.entidad()])
        self.seleccion(["C-1"], {})
        self.assertEqual(self.derivar(), 0)
        vista = c4_view.derive(self.w, "prueba")
        self.assertEqual(vista["elements"], [])
        self.assertIn("clase", vista["holes"][0]["reason"])

    def test_una_arista_con_extremo_fuera_de_la_seleccion_es_un_hueco(self):
        self.escribir_ledger(
            [self.consulta(symbol_ids=["App::Entry", "App::Store"]),
             self.consulta(qid="Q-2", symbol_ids=["App::Entry", "App::Store"],
                           relation_ids=["edge-1"])],
            [self.entidad(), self.arista()])
        self.seleccion(["C-1", "R-1"], {"C-1": "component"})
        self.assertEqual(self.derivar(), 0)
        vista = c4_view.derive(self.w, "prueba")
        self.assertEqual(vista["relations"], [])
        self.assertTrue(any("extremo" in h["reason"] for h in vista["holes"]),
                        vista["holes"])

    def test_un_self_loop_es_un_hueco(self):
        self.escribir_ledger(
            [self.consulta(symbol_ids=["App::Entry"]),
             self.consulta(qid="Q-2", symbol_ids=["App::Entry"],
                           relation_ids=["edge-1"])],
            [self.entidad(), self.arista(src="App::Entry", dst="App::Entry")])
        self.seleccion(["C-1", "R-1"], {"C-1": "component"})
        self.assertEqual(self.derivar(), 0)
        vista = c4_view.derive(self.w, "prueba")
        self.assertEqual(vista["relations"], [])

    def test_una_afirmacion_de_intencion_es_un_hueco(self):
        self.escribir_ledger(
            [self.consulta()],
            [self.entidad(cid="C-5", provenance="CURATED_INTENT")])
        self.seleccion(["C-5"], {"C-5": "component"})
        self.assertEqual(self.derivar(), 0)
        vista = c4_view.derive(self.w, "prueba")
        self.assertEqual(vista["elements"], [])

    def test_la_clase_fuera_del_vocabulario_rechaza_la_seleccion(self):
        self.escribir_ledger([self.consulta()], [self.entidad()])
        self.seleccion(["C-1"], {"C-1": "widget"})
        self.assertEqual(self.derivar(), 2)
        self.assertFalse(self.views.exists(), "una seleccion invalida no crea vistas")

    def test_la_pregunta_debe_ser_c1_c2_o_c3(self):
        self.escribir_ledger([self.consulta()], [self.entidad()])
        self.seleccion(["C-1"], {"C-1": "component"}, question="C4")
        self.assertEqual(self.derivar(), 2)

    def test_la_seleccion_sin_afirmaciones_se_rechaza(self):
        self.escribir_ledger([self.consulta()], [self.entidad()])
        self.seleccion([], {})
        self.assertEqual(self.derivar(), 2)

    def test_el_presupuesto_de_legibilidad_se_exige(self):
        queries = [self.consulta(qid=f"Q-{i}", symbols=(f"App::S{i}",))
                   for i in range(1, 17)]
        claims = [self.entidad(cid=f"C-{i}", symbol=f"App::S{i}",
                               query_ids=[f"Q-{i}"]) for i in range(1, 17)]
        self.escribir_ledger(queries, claims)
        self.seleccion([f"C-{i}" for i in range(1, 17)],
                       {f"C-{i}": "component" for i in range(1, 17)})
        self.assertEqual(self.derivar(), 2)
        self.assertFalse(self.views.exists(), "una seleccion invalida no crea vistas")

    def test_inputs_declara_el_material_del_que_deriva(self):
        self.escribir_ledger([self.consulta()], [self.entidad()])
        self.seleccion(["C-1"], {"C-1": "component"})
        self.assertEqual(self.derivar(emit=True), 0)
        vista = self.derivada()
        inputs = vista["inputs"]
        self.assertEqual(set(inputs),
                         {"evidence/claims.json", "evidence/queries.json"})
        for relative, digest in inputs.items():
            self.assertEqual(
                hashlib.sha256((self.w / relative).read_bytes()).hexdigest(),
                digest, relative)

    def test_la_base_se_deriva_de_las_consultas_que_sostienen_la_vista(self):
        self.escribir_ledger(
            [self.consulta(), self.consulta(qid="Q-2", symbols=("App::Store",))],
            [self.entidad(),
             self.entidad(cid="C-2", symbol="App::Store", query_ids=["Q-2"])])
        self.seleccion(["C-1", "C-2"], {"C-1": "component", "C-2": "container"})
        self.assertEqual(self.derivar(emit=True), 0)
        vista = self.derivada()
        self.assertEqual(vista["basis"]["identity"], "cognicode-cli 0.101.25 sha=abc")
        self.assertEqual(vista["basis"]["status"], "reported_unverified")
        self.assertEqual(vista["basis"]["revision"], "rev-abc123")

    def test_la_base_en_conflicto_se_declara_como_tal(self):
        self.escribir_ledger(
            [self.consulta(),
             self.consulta(qid="Q-2", symbols=("App::Store",),
                           basis="cognicode-cli 0.101.25 sha=otro")],
            [self.entidad(),
             self.entidad(cid="C-2", symbol="App::Store", query_ids=["Q-2"])])
        self.seleccion(["C-1", "C-2"], {"C-1": "component", "C-2": "container"})
        self.assertEqual(self.derivar(), 0)
        self.assertEqual(c4_view.derive(self.w, "prueba")["basis"]["status"], "conflict")

    def test_emit_escribe_la_vista_y_rechaza_pisar_lo_ajeno(self):
        self.escribir_ledger([self.consulta()], [self.entidad()])
        self.seleccion(["C-1"], {"C-1": "component"})
        self.assertEqual(self.derivar(emit=True), 0)
        vista = self.derivada()
        self.assertEqual(vista["generator"], c4_view.GENERATOR)
        self.assertEqual(vista["status"], "complete")
        ajeno = self.views / "prueba.json"
        ajeno.write_text(json.dumps({"generator": "someone-else"}), encoding="utf-8")
        self.assertEqual(self.derivar(emit=True), 2)
        self.assertEqual(json.loads(ajeno.read_text(encoding="utf-8"))["generator"],
                         "someone-else")

    def test_una_vista_con_huecos_o_cobertura_parcial_se_declara_parcelada(self):
        self.escribir_ledger(
            [self.consulta()],
            [self.entidad(), self.entidad(cid="C-2", symbol="App::Store",
                                          coverage="partial")])
        self.seleccion(["C-1", "C-2"], {"C-1": "component", "C-2": "component"})
        self.assertEqual(self.derivar(emit=True), 0)
        self.assertEqual(self.derivada()["status"], "partial")

    def test_el_ledger_ilegible_bloquea_la_derivacion(self):
        self.queries.write_text(json.dumps(
            {"schema_version": 7, "queries": []}), encoding="utf-8")
        self.claims.write_text(json.dumps(
            {"schema_version": 7, "claims": []}), encoding="utf-8")
        self.seleccion(["C-1"], {"C-1": "component"})
        self.assertEqual(self.derivar(), 2)

    def test_el_proyector_no_lee_el_checkout(self):
        self.escribir_ledger([self.consulta()], [self.entidad()])
        self.seleccion(["C-1"], {"C-1": "component"})
        self.derivar(emit=True)
        self.assertFalse((self.w / "SENTINEL_DO_NOT_READ").exists())


class CanonicalExampleTests(unittest.TestCase):
    """The example the lens publishes, executed against the ledger the
    evidence contract publishes.

    If the document and the projector ever disagree about the view, this
    is where it shows: the selection and the published view are not
    prose, they are data the test derives and compares.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.repo = self.root / "code"
        self.repo.mkdir()
        workspace.init(self.repo, home=self.home)
        self.w = Path(workspace.inspect(self.repo, home=self.home)["workspace"])

    def tearDown(self):
        self.tmp.cleanup()

    def test_el_ejemplo_del_documento_se_deriva(self):
        ledger = bloque_json("../references/evidence.md", "claim_id")
        seleccion = bloque_json("../references/lenses/c4.md", "seleccion")
        esperada = bloque_json("../references/lenses/c4.md", "vista")

        (self.w / "evidence/queries.json").write_text(
            json.dumps({"schema_version": ledger["schema_version"],
                        "queries": ledger["queries"]}), encoding="utf-8")
        (self.w / "evidence/claims.json").write_text(
            json.dumps({"schema_version": ledger["schema_version"],
                        "claims": ledger["claims"]}), encoding="utf-8")
        reports = self.w / "lenses/c4/reports"
        reports.mkdir(parents=True, exist_ok=True)
        (reports / "ejemplo.atlas.json").write_text(
            json.dumps(seleccion, ensure_ascii=False), encoding="utf-8")

        derivada = c4_view.derive(self.w, "ejemplo")
        for campo in ("question", "label", "basis", "elements", "relations",
                      "holes", "counts", "status"):
            with self.subTest(campo=campo):
                self.assertEqual(derivada[campo], esperada[campo],
                                 f"el ejemplo del documento y el proyector difieren en {campo}")


if __name__ == "__main__":
    unittest.main()
