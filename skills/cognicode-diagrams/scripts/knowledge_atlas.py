"""Incremental knowledge navigation from *derived* CogniCode ledgers and views.

No code inspection, no new facts, no DB, no projector execution. Rebuildable data.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

MAX_INPUT = 8 * 1024 * 1024
MAX_CLAIMS = 250
# These are presentation lenses, NEVER inferred by parsing a filename/DSL/image.
CATEGORY_LABELS = {
    "system": "Sistema", "module": "Modulos", "surface": "Superficies",
    "external": "Sistemas externos", "store": "Almacenes",
    "signal": "Senales observadas", "coverage": "Cobertura",
    "glossary": "Glosario", "symbol": "Simbolos",
    "intent": "Intencion (NO implementacion)",
}
IMPLEMENTATION = {"OBSERVED_CODE", "observed"}
INTENT = {"CODE_DOC", "CURATED_INTENT"}
UNCERTAIN = {"INFERRED", "inferred", "UNKNOWN", "unknown"}



class KnowledgeError(ValueError):
    pass


def _safe(path: Path, workspace: Path) -> None:
    if not path.is_relative_to(workspace):
        raise KnowledgeError("knowledge path outside external workspace")
    for p in (path, *path.parents):
        if p == workspace.parent:
            break
        if p.is_symlink():
            raise KnowledgeError("knowledge input symlink refused")


def inputs(workspace: Path) -> list[Path]:
    """Only our evidence ledger and per-view link reports; never the checkout."""
    result = []
    for name in ("claims.json", "queries.json"):
        p = workspace / "evidence" / name
        _safe(p, workspace)
        if p.exists():
            if not p.is_file():
                raise KnowledgeError("knowledge input is not a file")
            result.append(p)
    root = workspace / "lenses"
    _safe(root, workspace)
    for lens in sorted(root.iterdir()):
        _safe(lens, workspace)
        if not lens.is_dir():
            continue
        reports = lens / "reports"
        _safe(reports, workspace)
        if not reports.exists():
            continue
        for p in sorted(reports.iterdir()):
            _safe(p, workspace)
            if p.name.endswith(".atlas.json"):
                if not p.is_file():
                    raise KnowledgeError("view report is not a file")
                result.append(p)
    return result


def fingerprints(workspace: Path) -> dict[str, str]:
    result = {}
    for p in inputs(workspace):
        if p.stat().st_size > MAX_INPUT:
            raise KnowledgeError("knowledge input too large")
        result[str(p.relative_to(workspace))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def _load(path: Path, workspace: Path):
    _safe(path, workspace)
    if path.stat().st_size > MAX_INPUT:
        raise KnowledgeError("knowledge input too large")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise KnowledgeError("invalid derived knowledge JSON") from exc


def project(workspace: Path, catalog: dict, href, label) -> tuple[list[str], dict, int, int]:
    """Produce Markmap branches linking claims to *existing* source/render assets."""
    digests = fingerprints(workspace)
    ledger = workspace / "evidence" / "claims.json"
    qfile = workspace / "evidence" / "queries.json"
    claims_raw = _load(ledger, workspace) if ledger.is_file() else []
    if isinstance(claims_raw, dict):
        claims_raw = claims_raw.get("claims")
    if not isinstance(claims_raw, list) or len(claims_raw) > MAX_CLAIMS:
        raise KnowledgeError("claims must be a bounded array")
    claims = {}
    for c in claims_raw:
        if not isinstance(c, dict):
            raise KnowledgeError("invalid claim")
        cid = c.get("claim_id", c.get("id"))
        if not isinstance(cid, str) or not cid or cid in claims:
            raise KnowledgeError("duplicate or absent claim ID")
        if c.get("kind", "entity") not in {"entity", "relation"}:
            raise KnowledgeError("unknown claim kind")
        provenance = c.get("provenance", c.get("status", "UNKNOWN"))
        if provenance not in IMPLEMENTATION | INTENT | UNCERTAIN:
            raise KnowledgeError("unsupported claim provenance (DOC_INTENT requires separate authorized mode)")
        category = c.get("category", "symbol")
        if category not in CATEGORY_LABELS:
            raise KnowledgeError("unknown concept category; classify only from CogniCode evidence")
        if (category == "intent") != (provenance in INTENT):
            raise KnowledgeError("intent and implemented architectural concepts cannot share a category")
        ids = c.get("query_ids", [])
        if not isinstance(ids, list) or any(not isinstance(q, str) or not q for q in ids):
            raise KnowledgeError("invalid claim query references")
        if provenance == "CURATED_INTENT" and (ids or not isinstance(c.get("curator"), str) or not c["curator"]):
            raise KnowledgeError("curated intent needs curator, never fabricated CogniCode queries")
        if provenance == "CODE_DOC" and not ids:
            raise KnowledgeError("CODE_DOC intent requires CogniCode query IDs")
        if c.get("plane", "static") not in {"static", "runtime", "deployment", "intent"}:
            raise KnowledgeError("unknown claim evidence plane")
        if category == "intent" and c.get("plane", "intent") != "intent":
            raise KnowledgeError("intent cannot claim implementation plane")
        if c.get("coverage", "unknown") not in {"complete", "partial", "unknown"}:
            raise KnowledgeError("unsupported evidence coverage")
        claims[cid] = c

    if qfile.is_file():
        qraw = _load(qfile, workspace)
        if isinstance(qraw, dict):
            qraw = qraw.get("queries")
        if not isinstance(qraw, list):
            raise KnowledgeError("queries must be an array")
        qids = {q.get("query_id", q.get("id")) for q in qraw if isinstance(q, dict)}
        if any(qid not in qids for c in claims.values() for qid in c.get("query_ids", [])):
            raise KnowledgeError("claim references nonexistent query")

    by_claim = {}
    bound = 0
    for p in inputs(workspace):
        if not p.name.endswith(".atlas.json"):
            continue
        view = _load(p, workspace)
        if not isinstance(view, dict) or view.get("schema_version") != 1:
            raise KnowledgeError("invalid view link schema")
        lens = p.parent.parent.name
        if lens not in catalog:
            raise KnowledgeError("view link lens not found among assets")
        name, ids, assets = view.get("label"), view.get("claim_ids"), view.get("assets")
        if not isinstance(name, str) or not name.strip() or not isinstance(ids, list) or not ids or not isinstance(assets, list) or not assets:
            raise KnowledgeError("view must link concrete claims and assets")
        allowed = {str(a.relative_to(workspace)) for k in ("sources", "renders") for a in catalog[lens][k]}
        if any(not isinstance(cid, str) or cid not in claims for cid in ids):
            raise KnowledgeError("view references missing claim")
        plane = view.get("plane", "implementation")
        if plane not in {"implementation", "intent"}:
            raise KnowledgeError("view has unknown plane")
        if any((claims[cid].get("category", "symbol") == "intent") != (plane == "intent") for cid in ids):
            raise KnowledgeError("intent-only claim cannot justify an implementation diagram")
        if any(not isinstance(a, str) or a not in allowed for a in assets):
            raise KnowledgeError("view references ungenerated/external asset")
        for cid in ids:
            by_claim.setdefault(cid, []).append((name, [workspace / a for a in assets]))
        bound += 1

    lines = []
    if claims:
        lines.extend(["## Conocimiento derivado de CogniCode", "",
                      "Claims, consultas y proyecciones vinculadas; el atlas no crea evidencia.", ""])
    groups = {}
    for cid, c in sorted(claims.items()):
        symbol = c.get("symbol_id") or c.get("from_symbol") or "Sin simbolo"
        if not isinstance(symbol, str):
            raise KnowledgeError("invalid symbol")
        groups.setdefault(c.get("category", "symbol"), {}).setdefault(symbol, []).append((cid, c))
    for category, by_symbol in sorted(groups.items(), key=lambda item: list(CATEGORY_LABELS).index(item[0])):
        lines.extend(["### " + CATEGORY_LABELS[category], ""])
        for symbol, members in sorted(by_symbol.items()):
            lines.extend(["#### " + label(symbol), ""])
            for cid, c in members:
                relation = c.get("to_symbol") if c.get("kind") == "relation" else None
                source = "referencia" if c.get("relation_source") == "reference_link" else c.get("kind", "entity")
                name = f"{cid} · {source}" + (f" → {relation}" if isinstance(relation, str) else "")
                provenance = c.get("provenance", c.get("status", "UNKNOWN"))
                ids = c.get("query_ids", [])
                # A legacy "observed" without resolvable queries is a *candidate*, never verified evidence.
                effective = ("UNKNOWN (sin query)" if provenance in IMPLEMENTATION and (not ids or not qfile.is_file())
                             else provenance)
                plane = "intent" if category == "intent" else c.get("plane", "static")
                coverage = c.get("coverage", "unknown")
                lines.append(f"- {label(name)} [{label(effective)} · {label(plane)} · cobertura:{label(coverage)}]")
                lines.append(f"  - [Claim]({href(ledger, workspace / 'navigation')})")
                if qfile.is_file() and ids:
                    lines.append(f"  - [Consultas: {label(', '.join(ids))}]({href(qfile, workspace / 'navigation')})")
                if category == "intent":
                    lines.append("  - NO demuestra implementacion")
                if c.get("kind") == "relation" and category != "intent":
                    # Detail is explicitly supplied by CogniCode observations; never infer HTTP or runtime.
                    attributes = c.get("attributes", {})
                    if not isinstance(attributes, dict):
                        raise KnowledgeError("relation.attributes invalid")
                    for key in ("kind", "technology", "endpoint", "order"):
                        value = attributes.get(key)
                        if value is not None:
                            if not isinstance(value, str):
                                raise KnowledgeError("relation attribute must be text")
                            lines.append(f"  - {key}: {label(value)} (declarado en codigo, no runtime)")
                for view_name, artifacts in by_claim.get(cid, []):
                    lines.append("  - " + label(view_name))
                    for p in artifacts:
                        lines.append(f"    - [{label(p.name)}]({href(p, workspace / 'navigation')})")
            lines.append("")
    return lines, digests, len(claims), bound
