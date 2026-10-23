#!/usr/bin/env python3
"""The only writer of the ledger of a workspace.

The agent brings the facts of one observation; this tool owns the shape.
It stamps the identifier, the version of the contract and the canonical
names, appends atomically, and publishes the derived verdict with the
material, so a ledger is never published without its verdict.

    python3 scripts/record.py query --repo <raiz> --payload <fichero|->
    python3 scripts/record.py claim  --repo <raiz> --payload <fichero|->

Under version 2 nobody writes the ledger by hand: the payload is facts,
not form, and an old spelling or a self-made identifier is refused at the
door. Material written before the shape was fixed is migrated when every
entry can be renewed without loss — the migration is reported — and when
it cannot, recording refuses and says why, because a renewal that lost
entries would be a ledger that lies about what it contains.

Never reads the checkout: it only writes the derived workspace under HOME.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import evidence_contract as contract
import evidence as validator
import workspace as ws

SKILL_NAME = "cognicode-diagrams"
MAX_PAYLOAD = 1024 * 1024
QUERIES_FILE = "queries.json"
CLAIMS_FILE = "claims.json"


class RecordError(ValueError):
    """The payload or the ledger cannot be recorded as it stands."""


# ---------------------------------------------------------------------------
# The payload: facts, not form.
# ---------------------------------------------------------------------------

def load_payload(path: str) -> dict:
    if path == "-":
        raw = sys.stdin.buffer.read()
    else:
        fuente = Path(path)
        if fuente.is_symlink() or not fuente.is_file():
            raise RecordError(f"el payload no es un fichero legible: {path}")
        if fuente.stat().st_size > MAX_PAYLOAD:
            raise RecordError("el payload es demasiado grande")
        raw = fuente.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise RecordError(f"el payload no es JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise RecordError("el payload no es un objeto")
    return payload


def _reject_forma_propia(payload: dict, aliases: dict, owned: tuple[str, ...]) -> None:
    """Refuse the keys that decide the shape: they belong to the recorder."""
    for key in owned:
        if key in payload:
            raise RecordError(
                f"el payload declara '{key}': el identificador y la version los sella el registro"
            )
    for canonical, spellings in aliases.items():
        for spelling in spellings:
            if spelling in payload:
                raise RecordError(
                    f"el payload usa '{spelling}': bajo la version "
                    f"{contract.CONTRACT_VERSION} se escribe '{canonical}'"
                )


def validate_query(payload: dict) -> None:
    _reject_forma_propia(payload, contract.QUERY_ALIASES, ("query_id", "schema_version"))
    for field in ("mode", "status", "source", "observation_plane"):
        if not isinstance(payload.get(field), str) or not payload[field].strip():
            raise RecordError(f"falta '{field}'")
    vocabularios = {
        "mode": contract.QUERY_MODES,
        "status": contract.QUERY_STATUSES,
        "source": contract.QUERY_SOURCES,
        "observation_plane": contract.QUERY_PLANES,
    }
    for field, vocabulario in vocabularios.items():
        if payload[field] not in vocabulario:
            raise RecordError(
                f"'{field}' es '{payload[field]}', que no es un valor del contrato"
            )
    symbol_ids = payload.get("symbol_ids")
    if not isinstance(symbol_ids, list) or any(
        not isinstance(symbol, str) or not symbol.strip() for symbol in symbol_ids
    ):
        raise RecordError(
            "falta 'symbol_ids': una consulta declara los simbolos que resolvio, "
            "aunque no resolviera ninguno"
        )


def validate_claim(payload: dict, queries: dict[str, dict]) -> None:
    _reject_forma_propia(payload, contract.CLAIM_ALIASES, ("claim_id", "schema_version"))
    for field in ("kind", "provenance", "plane", "coverage"):
        if not isinstance(payload.get(field), str) or not payload[field].strip():
            raise RecordError(f"falta '{field}'")
    if payload["kind"] not in contract.CLAIM_KINDS:
        raise RecordError(f"'kind' es '{payload['kind']}', que no es un valor del contrato")
    if payload["provenance"] not in contract.CLAIM_PROVENANCE:
        raise RecordError(
            f"'provenance' es '{payload['provenance']}', que no es una procedencia del contrato"
        )
    if payload["coverage"] not in contract.CLAIM_COVERAGES:
        raise RecordError(
            f"'coverage' es '{payload['coverage']}', que no es una cobertura del contrato"
        )
    query_ids = payload.get("query_ids")
    if not isinstance(query_ids, list) or any(
        not isinstance(qid, str) or not qid.strip() for qid in query_ids
    ):
        raise RecordError("falta 'query_ids': una afirmacion declara que consultas la sostienen")
    for qid in query_ids:
        if qid not in queries:
            raise RecordError(f"la consulta '{qid}' no existe: registrala antes de citarla")

    if payload["kind"] == "entity":
        symbol_id = payload.get("symbol_id")
        if not isinstance(symbol_id, str) or not symbol_id.strip():
            raise RecordError("falta 'symbol_id': una entidad declara el simbolo que es")
        return

    source = payload.get("relation_source")
    if source == contract.GRAPH_EDGE:
        for field in ("relation_id", "from_symbol", "to_symbol"):
            if not isinstance(payload.get(field), str) or not payload[field].strip():
                raise RecordError(f"falta '{field}'")
    elif source == contract.REFERENCE_LINK:
        reference = payload.get("reference")
        if not isinstance(reference, dict):
            raise RecordError("falta 'reference' (query_id + index + path + line)")
        for field in ("query_id", "index", "path", "line"):
            if field not in reference:
                raise RecordError(f"'reference' no declara '{field}'")
        if reference["query_id"] not in queries:
            raise RecordError(
                f"la consulta '{reference['query_id']}' de la referencia no existe: "
                "registrala antes de citarla"
            )
    else:
        raise RecordError(
            "falta 'relation_source': una relacion declara de donde sale "
            "(graph_edge o reference_link)"
        )


# ---------------------------------------------------------------------------
# The ledger: read, renew, append.
# ---------------------------------------------------------------------------

def _next_id(items: list, field: str, prefix: str) -> str:
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
    numeros = []
    for item in items:
        if isinstance(item, dict):
            value = item.get(field)
            if isinstance(value, str):
                match = pattern.match(value)
                if match:
                    numeros.append(int(match.group(1)))
    return f"{prefix}-{max(numeros, default=0) + 1}"


def _renovar_entrada(item, field: str, aliases: dict) -> int:
    """Resolve the old spellings of one entry, in place. Returns what moved."""
    renombrados = 0
    for canonical, spellings in aliases.items():
        if canonical in item:
            continue
        for spelling in spellings:
            if spelling not in item:
                continue
            value = item.pop(spelling)
            if field == "claim_id" and canonical == "symbol_id":
                # El plural legado solo renueva si no ambigua.
                if not isinstance(value, list) or len(value) != 1:
                    continue
                value = value[0]
            item[canonical] = value
            renombrados += 1
            break
    return renombrados


def load_ledger(path: Path, collection: str, workspace_dir: Path) -> tuple[dict, int]:
    """Read one ledger file, renewing legacy material to the current version.

    Returns the document and how many spellings were renewed. Refuses when
    the material declares a version this tool cannot write, or when an
    entry cannot be renewed without loss: a renewal that dropped entries
    would be a ledger that lies about what it contains.
    """
    if not path.exists():
        return ({ "schema_version": contract.CONTRACT_VERSION, "skill": SKILL_NAME,
                  "workspace": str(workspace_dir), collection: [] }, 0)
    if path.is_symlink():
        raise RecordError(f"el ledger es un enlace simbolico: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RecordError(f"el ledger no se pudo leer: {path}: {exc}") from exc

    field = "claim_id" if collection == "claims" else "query_id"
    aliases = contract.CLAIM_ALIASES if collection == "claims" else contract.QUERY_ALIASES
    gaps_fn = contract.claim_gaps if collection == "claims" else contract.query_gaps

    if isinstance(raw, list):
        document = {collection: raw}
    elif isinstance(raw, dict):
        document = raw
    else:
        raise RecordError(f"el ledger no es un objeto ni una lista: {path}")

    version = document.get("schema_version")
    renombrados = 0
    if version == contract.CONTRACT_VERSION:
        document.setdefault(collection, [])
    elif version in contract.LEGACY_VERSIONS or version is None:
        items = document.get(collection)
        if not isinstance(items, list):
            raise RecordError(
                f"el ledger no trae la lista '{collection}': {path}"
            )
        for item in items:
            if isinstance(item, dict):
                renombrados += _renovar_entrada(item, field, aliases)
        document["schema_version"] = contract.CONTRACT_VERSION
        document["skill"] = SKILL_NAME
        document["workspace"] = str(workspace_dir)
    else:
        raise RecordError(
            f"el ledger declara la version {version}, que este registro no sabe escribir: {path}"
        )

    items = document.get(collection)
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise RecordError(f"el ledger no trae entradas validas en '{collection}': {path}")
    for item in items:
        identificador = item.get(field, item.get("id"))
        gaps = gaps_fn(item) if collection == "claims" else gaps_fn(str(identificador), item)
        if gaps:
            raise RecordError(
                f"el ledger tiene una entrada que no cumple la version "
                f"{contract.CONTRACT_VERSION} ('{identificador}'): {'; '.join(gaps)}"
            )
    return document, renombrados


def write_ledger(path: Path, document: dict) -> None:
    if path.is_symlink():
        raise RecordError(f"el destino es un enlace simbolico: {path}")
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.stem}-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
        os.chmod(temp, 0o644)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def record(what: str, repo: Path, home: Path | None, payload_path: str) -> dict:
    root = ws.supplied_repository_root(repo)
    workspace_dir = ws.workspace_path(root, home=home)
    if not workspace_dir.exists():
        ws.init(root, home=home)
    validator._no_symlinks(workspace_dir)
    evidence = workspace_dir / "evidence"
    if evidence.is_symlink():
        raise RecordError(f"el directorio de evidencia es un enlace simbolico: {evidence}")
    evidence.mkdir(exist_ok=True)

    payload = load_payload(payload_path)
    queries_path = evidence / QUERIES_FILE
    claims_path = evidence / CLAIMS_FILE
    queries_doc, queries_renovadas = load_ledger(queries_path, "queries", workspace_dir)

    if what == "query":
        validate_query(payload)
        payload["query_id"] = _next_id(queries_doc["queries"], "query_id", "Q")
        queries_doc["queries"].append(payload)
        write_ledger(queries_path, queries_doc)
        written, renovadas, stamped = queries_path, queries_renovadas, payload["query_id"]
    else:
        claims_doc, claims_renovadas = load_ledger(claims_path, "claims", workspace_dir)
        queries = contract.index_queries(queries_doc)
        validate_claim(payload, queries)
        payload["claim_id"] = _next_id(claims_doc["claims"], "claim_id", "C")
        claims_doc["claims"].append(payload)
        write_ledger(claims_path, claims_doc)
        written, renovadas, stamped = claims_path, claims_renovadas, payload["claim_id"]

    # El otro libro existe aunque este vacio: el veredicto se deriva de los
    # dos, y un ledger publicado a medias no se puede comprobar.
    for path, collection in ((queries_path, "queries"), (claims_path, "claims")):
        if not path.exists():
            document, _ = load_ledger(path, collection, workspace_dir)
            write_ledger(path, document)

    report, inputs = validator.examine(workspace_dir)
    target = evidence / validator.LEDGER_NAME
    validator._write_owned(
        target,
        json.dumps(validator.ledger(workspace_dir, report, inputs),
                   ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    return {
        "status": validator.estado_del_informe(report),
        "recorded": what,
        "id": stamped,
        "renovadas": renovadas,
        "workspace": str(workspace_dir),
        "counts": {
            "corroborated": report["corroborated"],
            "observed_not_corroborated": report["not_corroborated"],
            "not_checkable": report["not_checkable"],
            "not_implementation": report["not_implementation"],
        },
        "ledger": str(target),
        "written": str(written),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("what", choices=("query", "claim"),
                        help="que se registra: una consulta o una afirmacion")
    parser.add_argument("--repo", required=True, type=Path,
                        help="raiz explicita del repositorio investigado")
    parser.add_argument("--home", type=Path, default=None,
                        help="raiz del HOME derivado; por defecto el del usuario")
    parser.add_argument("--payload", required=True,
                        help="fichero con el payload JSON, o - para la entrada estandar")
    args = parser.parse_args(argv)

    try:
        result = record(args.what, args.repo, args.home, args.payload)
    except (ws.WorkspaceError, validator.EvidenceError, RecordError, OSError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
