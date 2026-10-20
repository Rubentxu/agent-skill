"""Pure corroboration of an implementation fact by observed CogniCode queries.

No access to Git, checkout, runtime or services. IDs alone are not evidence.
"""
from __future__ import annotations


def index_queries(raw: list | dict) -> dict[str, dict]:
    if isinstance(raw, dict):
        raw = raw.get("queries")
    if not isinstance(raw, list):
        raise ValueError("queries must be a list")
    result = {}
    for q in raw:
        if not isinstance(q, dict):
            raise ValueError("invalid query")
        key = q.get("query_id", q.get("id"))
        if not isinstance(key, str) or not key or key in result:
            raise ValueError("missing or duplicate query ID")
        result[key] = q
    return result


def corroborated(claim: dict, queries: dict[str, dict]) -> bool:
    """True iff a successful structured query identifies this exact symbol/edge."""
    if not isinstance(claim, dict) or claim.get("provenance", claim.get("status")) not in {"OBSERVED_CODE", "observed"}:
        return False
    if claim.get("category") == "intent" or claim.get("plane", "static") != "static":
        return False
    ids = claim.get("query_ids")
    if not isinstance(ids, list) or not ids or any(
        not isinstance(qid, str) or not qid or qid not in queries for qid in ids
    ) or len(ids) != len(set(ids)):
        return False
    kind = claim.get("kind", "entity")
    if kind not in {"entity", "relation"}:
        return False
    # Usage/reference is NOT a graph edge. Never promote it by naming endpoints.
    if kind == "relation" and claim.get("relation_source") != "graph_edge":
        return False
    for qid in ids:
        q = queries[qid]
        if (q.get("source", "cognicode") != "cognicode"
                or q.get("mode") not in {"structured", "symbol_context"}
                or q.get("status") not in {"ok", "partial"}
                or q.get("observation_plane", "static") != "static"):
            continue
        symbols = q.get("symbol_ids")
        if not isinstance(symbols, list):
            continue
        if kind == "entity" and isinstance(claim.get("symbol_id"), str):
            if claim["symbol_id"] in symbols:
                return True
        if kind == "relation" and q.get("mode") == "structured":
            rels = q.get("relation_ids")
            if (isinstance(rels, list) and
                    isinstance(claim.get("relation_id"), str) and claim["relation_id"] and
                    isinstance(claim.get("from_symbol"), str) and
                    isinstance(claim.get("to_symbol"), str) and
                    claim["relation_id"] in rels and
                    claim["from_symbol"] in symbols and claim["to_symbol"] in symbols):
                return True
    return False
