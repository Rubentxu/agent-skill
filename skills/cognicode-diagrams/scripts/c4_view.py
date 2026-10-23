#!/usr/bin/env python3
"""The C4 derived view: the view as data, traced to the ledger.

The selection is curated — which claims make a view, which C4 question it
answers, which class each element has. The view is derived: this tool
reads the ledger and publishes elements, relations and holes, with the
digests of the material it came from and the basis its queries declare.
Nothing in the view is written by hand, and nothing in it is drawn: the
canvas is another product's concern, and any renderer that wants to draw
this data can map it to its own shapes.

    python3 scripts/c4_view.py --repo <raiz> --view containers
    python3 scripts/c4_view.py --repo <raiz> --view containers --emit

An element is a corroborated entity claim, identified by its symbol and
classified by the selection. A relation is a corroborated graph edge,
with the identifier the engine returned: a localised reference is never
an edge, exactly as in the evidence contract. A claim that does not make
it into the view is not dropped: it is published as a hole with its
reason, because a hole with its reason is information and a silent
omission is not.

Never reads the checkout: it only reads the derived workspace under HOME.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import evidence_contract as contract
import evidence as validator
import selection
import workspace as ws
from report_thinking import basis_of

GENERATOR = selection.VIEW_GENERATOR
VIEW_SCHEMA = 1

# El vocabulario C4 que la version 1 de la vista admite. Ampliarlo es un
# cambio de contrato, no un campo libre: una clase que nadie dibuja igual
# en dos sitios es una clase que no significa nada.
C4_KINDS = ("system", "external_system", "container", "component", "store")

# Las preguntas que la lente declara, para que la vista diga cual responde.
C4_QUESTIONS = ("C1", "C2", "C3")

# El presupuesto de legibilidad de la lente: una vista que se pasa se
# divide, no se aprieta.
MAX_ELEMENTS = 15
MAX_CLAIMS = selection.MAX_CLAIMS
MAX_LABEL = selection.MAX_LABEL

CLAIMS_PATH = "evidence/claims.json"
QUERIES_PATH = "evidence/queries.json"


def _plane_of(planes: set[str]) -> str | None:
    """The view's plane: the one plane its whole content shares.

    A mixed set is not one plane, and an empty set is no plane at all:
    both leave the field out instead of inventing an answer (SPEC-ST-002
    says every view declares its plane; declaring nothing is still more
    honest than guessing one).
    """
    if len(planes) == 1:
        return next(iter(planes))
    return None


class ViewError(ValueError):
    """The selection or the ledger cannot produce a view as it stands."""


# ---------------------------------------------------------------------------
# The selection: curated, validated.
# ---------------------------------------------------------------------------

def load_selection(workspace_dir: Path, view: str) -> dict:
    path = workspace_dir / "lenses" / "c4" / "reports" / f"{view}.atlas.json"
    if not path.is_file():
        raise ViewError(f"no hay seleccion de vista '{view}': falta {path.name}")
    # La forma compartida la decide su dueño: el proyector no vuelve a
    # inventar unas reglas que el atlas y la editorial ya aplican.
    try:
        seleccion = selection.load(path)
    except selection.SelectionError as exc:
        raise ViewError(f"la seleccion de vista '{view}' no es valida: {exc}") from exc

    if seleccion.get("lens") != "c4":
        raise ViewError("la seleccion no declara la lente c4")
    pregunta = seleccion.get("question")
    if pregunta not in C4_QUESTIONS:
        raise ViewError(
            f"la pregunta es '{pregunta}', y la lente solo declara {', '.join(C4_QUESTIONS)}"
        )
    kinds = seleccion.get("kinds")
    if not isinstance(kinds, dict):
        raise ViewError("la seleccion no declara las clases de sus elementos")
    for cid, kind in kinds.items():
        if cid not in set(seleccion["claim_ids"]):
            raise ViewError(f"la clase de '{cid}' apunta a una afirmacion que no esta seleccionada")
        if kind not in C4_KINDS:
            raise ViewError(
                f"la clase de '{cid}' es '{kind}', que no es del vocabulario: "
                f"{', '.join(C4_KINDS)}"
            )
    return seleccion


# ---------------------------------------------------------------------------
# The derivation: computed, never written by hand.
# ---------------------------------------------------------------------------

def _texto(value) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _coverage_of(coverages: list[str]) -> str:
    if coverages and all(c == "complete" for c in coverages):
        return "complete"
    if any(c == "partial" for c in coverages):
        return "partial"
    return "unknown"


def _location_of(claim: dict, queries: dict[str, dict], symbol: str) -> dict | None:
    """Where the corroborating queries resolved this symbol, when they say."""
    for qid in claim.get("query_ids", []) if isinstance(claim.get("query_ids"), list) else []:
        query = queries.get(qid) if isinstance(qid, str) else None
        if not isinstance(query, dict):
            continue
        locations = query.get("symbol_locations")
        if not isinstance(locations, dict):
            continue
        site = locations.get(symbol)
        if isinstance(site, dict) and _texto(site.get("path")):
            line = site.get("line")
            return {"path": site["path"],
                    **({"line": line} if isinstance(line, int) else {})}
    return None


def derive(workspace_dir: Path, view: str) -> dict:
    """Derive the view of one selection from the ledger of the workspace."""
    validator._no_symlinks(workspace_dir)
    seleccion = load_selection(workspace_dir, view)

    evidence = workspace_dir / "evidence"
    try:
        claims_bytes = validator._load_bytes(evidence / "claims.json")
        queries_bytes = validator._load_bytes(evidence / "queries.json")
        claims_raw = json.loads(claims_bytes.decode("utf-8"))
        queries_raw = json.loads(queries_bytes.decode("utf-8"))
    except (validator.EvidenceError, ValueError, UnicodeError) as exc:
        raise ViewError(f"el ledger no se pudo leer: {exc}") from exc

    status, gaps = contract.material_status(claims_raw, queries_raw)
    if status != "current":
        raise ViewError("el ledger no se puede leer con este contrato: " + "; ".join(gaps))
    queries = contract.index_queries(queries_raw)
    claims = contract.index_claims(claims_raw)

    # Primera pasada: las entidades. Un elemento es un simbolo; las
    # afirmaciones que lo corroboran se agrupan en el.
    elementos: dict[str, dict] = {}
    huecos: list[dict] = []
    for cid in seleccion["claim_ids"]:
        claim = claims.get(cid)
        if claim is None:
            huecos.append({"claim_id": cid, "reason": "la afirmacion no esta en el ledger"})
            continue
        if contract.provenance_of(claim) not in contract.IMPLEMENTATION_PROVENANCE:
            huecos.append({
                "claim_id": cid,
                "reason": "no es una afirmacion de implementacion: se declara, no se dibuja",
            })
            continue
        if claim.get("kind") != "entity":
            continue
        kind = seleccion["kinds"].get(cid)
        if kind is None:
            huecos.append({"claim_id": cid,
                           "reason": "la seleccion no declara su clase C4"})
            continue
        if not contract.corroborated(claim, queries):
            _, missing = contract.verdict(claim, queries)
            huecos.append({
                "claim_id": cid,
                "reason": "; ".join(missing) or "no corroborada por ninguna consulta estructurada",
            })
            continue
        symbol = claim["symbol_id"]
        elemento = elementos.get(symbol)
        if elemento is None:
            elemento = {"id": symbol, "kind": kind, "label": symbol,
                        "claim_ids": [], "coverage": claim.get("coverage", "unknown")}
            elementos[symbol] = elemento
        else:
            elemento["coverage"] = _coverage_of(
                [elemento["coverage"], claim.get("coverage", "unknown")])
        elemento["claim_ids"].append(cid)
        sitio = _location_of(claim, queries, symbol)
        if sitio is not None and "location" not in elemento:
            elemento["location"] = sitio

    # Segunda pasada: las relaciones. Solo aristas corroboradas del grafo;
    # una referencia localizada nunca lo es.
    relations: list[dict] = []
    for cid in seleccion["claim_ids"]:
        claim = claims.get(cid)
        if claim is None or contract.provenance_of(claim) not in contract.IMPLEMENTATION_PROVENANCE:
            continue
        if claim.get("kind") != "relation":
            continue
        if claim.get("relation_source") == contract.REFERENCE_LINK:
            huecos.append({
                "claim_id": cid,
                "reason": "una referencia localizada no es una arista del grafo",
            })
            continue
        if not contract.corroborated(claim, queries):
            _, missing = contract.verdict(claim, queries)
            huecos.append({
                "claim_id": cid,
                "reason": "; ".join(missing) or "no corroborada por ninguna consulta estructurada",
            })
            continue
        src, dst = claim.get("from_symbol"), claim.get("to_symbol")
        if src == dst:
            huecos.append({"claim_id": cid,
                           "reason": "un bucle sobre el mismo elemento no es una relacion de la vista"})
            continue
        ausentes = [extremo for extremo in (src, dst) if extremo not in elementos]
        if ausentes:
            huecos.append({
                "claim_id": cid,
                "reason": "un extremo no esta en la vista: " + ", ".join(map(str, ausentes)),
            })
            continue
        attrs = claim.get("attributes")
        kind = _texto(attrs.get("kind")) if isinstance(attrs, dict) else None
        relations.append({
            "source": src, "target": dst,
            "kind": kind or "relation",
            "claim_id": cid, "relation_id": claim.get("relation_id"),
            "coverage": claim.get("coverage", "unknown"),
        })

    elements = sorted(elementos.values(), key=lambda e: e["id"])
    if len(elements) > MAX_ELEMENTS:
        raise ViewError(
            f"la vista excede el presupuesto de legibilidad ({MAX_ELEMENTS} elementos): "
            "dividirla en vistas por contenedor o por rol"
        )
    relations.sort(key=lambda r: (r["source"], r["target"], r["claim_id"]))
    huecos.sort(key=lambda h: h["claim_id"])

    # La base la declaran las consultas que sostienen lo publicado: las de
    # los elementos y las de las relaciones que llegaron.
    sostienen: set[str] = set()
    for elemento in elements:
        for cid in elemento["claim_ids"]:
            ids = claims[cid].get("query_ids")
            if isinstance(ids, list):
                sostienen.update(qid for qid in ids if isinstance(qid, str))
    for relation in relations:
        ids = claims[relation["claim_id"]].get("query_ids")
        if isinstance(ids, list):
            sostienen.update(qid for qid in ids if isinstance(qid, str))

    todo_completo = (not huecos
                     and all(e["coverage"] == "complete" for e in elements)
                     and all(r["coverage"] == "complete" for r in relations))

    # El plano de la vista es el de su contenido: las afirmaciones que
    # llegaron. Una sola respuesta viaja en el campo; una mezcla o un
    # vacio salen sin el, que es declarar que no se dijo.
    llegaron: set[str] = set()
    for elemento in elements:
        for cid in elemento["claim_ids"]:
            plano = claims[cid].get("plane")
            if isinstance(plano, str) and plano:
                llegaron.add(plano)
    for relation in relations:
        plano = claims[relation["claim_id"]].get("plane")
        if isinstance(plano, str) and plano:
            llegaron.add(plano)

    vista = {
        "schema_version": VIEW_SCHEMA,
        "generator": GENERATOR,
        "lens": "c4",
        "view": view,
        "question": seleccion["question"],
        "label": seleccion["label"],
        "workspace": str(workspace_dir),
        "inputs": {
            CLAIMS_PATH: hashlib.sha256(claims_bytes).hexdigest(),
            QUERIES_PATH: hashlib.sha256(queries_bytes).hexdigest(),
        },
        "basis": basis_of(queries, sostienen),
        "elements": elements,
        "relations": relations,
        "holes": huecos,
        "counts": {"elements": len(elements), "relations": len(relations),
                   "holes": len(huecos)},
        "status": "complete" if todo_completo else "partial",
    }
    plano = _plane_of(llegaron)
    if plano is not None:
        vista["plane"] = plano
    return vista


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path,
                        help="raiz explicita del repositorio investigado")
    parser.add_argument("--home", type=Path, default=None,
                        help="raiz del HOME derivado; por defecto el del usuario")
    parser.add_argument("--view", required=True,
                        help="nombre de la seleccion de vista (reports/<vista>.atlas.json)")
    parser.add_argument("--emit", action="store_true",
                        help="escribe la vista derivada junto a las selecciones")
    args = parser.parse_args(argv)

    try:
        root = ws.supplied_repository_root(args.repo)
        workspace_dir = ws.workspace_path(root, home=args.home)
        if not workspace_dir.exists():
            raise ViewError(f"no hay material derivado para {root}")
        vista = derive(workspace_dir, args.view)
        if args.emit:
            views = workspace_dir / "lenses" / "c4" / "views"
            if views.is_symlink():
                raise ViewError(f"el directorio de vistas es un enlace simbolico: {views}")
            views.mkdir(parents=True, exist_ok=True)
            target = views / f"{args.view}.json"
            validator._write_owned(
                target, json.dumps(vista, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    except (ws.WorkspaceError, validator.EvidenceError, ViewError, OSError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        return 2
    print(json.dumps(vista, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
