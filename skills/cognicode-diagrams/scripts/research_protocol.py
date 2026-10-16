"""Pure question→capability→proof decision protocol for CogniCode diagrams.

No filesystem, shell, network, indexer, repository or CogniCode calls. The agent
supplies *observed* capability/probe/query facts; this module checks consistency,
selects the next admissible step, and refuses to certify ungrounded claims.
"""
from __future__ import annotations

from typing import Any

# Semantic roles, NOT names of commands. Names come only from runtime discovery.
QUESTION_ROLES: dict[str, tuple[str, ...]] = {
    "responsibilities": ("symbol_index", "intent_search", "symbol_context"),
    "understand_symbol": ("symbol_context", "members", "type_references"),
    "collaborators": ("references", "implementors", "call_hierarchy"),
    "interaction": ("subgraph", "trace_path"),
    "view_grouping": ("communities", "graph_query"),
}
STRUCTURED_MODES = {"structured", "symbol_context"}
DENIED_MODES = {"raw", "repository_read", "external_indexer"}
TEXT_ONLY_TOOLS = {"read_file", "search_content"}
PROBE_STATES = {"untried", "usable", "partial", "failed", "unsupported"}
QUERY_STATES = {"ok", "partial", "failed", "unsupported"}
COVERAGES = {"complete", "partial", "unknown"}
PLANES = {"static", "runtime", "deployment"}


class ResearchError(ValueError):
    """Invalid or misleading research state."""


def _str(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ResearchError(f"{name} debe ser string no vacío")
    return value


def _list(value: Any, name: str) -> list:
    if not isinstance(value, list):
        raise ResearchError(f"{name} debe ser lista")
    return value


def _unique(records: list, key: str, name: str) -> None:
    ids = [_str(item.get(key), f"{name}.{key}") for item in records]
    if len(ids) != len(set(ids)):
        raise ResearchError(f"{name}: {key} duplicado")


def _result(status: str, action: str | None, why: str, question_id: str | None = None,
            capability: str | None = None, missing: list[str] | None = None) -> dict:
    return {"status": status, "action": action, "why": why, "question_id": question_id,
            "capability": capability, "missing": missing or []}



def _assess_scope(scope: Any, qid: str, language: str, by_query: dict,
                  budget: int, attempts: int) -> dict:
    """Fail closed on omitted files; never confuse a complete graph with complete evidence."""
    if scope is None:
        return _result("IN_PROGRESS", "assess-coverage",
                       "falta informe de cobertura y ficheros omitidos obtenido mediante CogniCode", qid)
    if not isinstance(scope, dict):
        raise ResearchError("scope debe ser objeto")
    if scope.get("source") != "cognicode":
        return _result("BLOCKED", None, "cobertura no atribuida a CogniCode", qid)
    _str(scope.get("report_id"), "scope.report_id")
    languages = _list(scope.get("languages"), "scope.languages")
    if language not in languages:
        return _result("PARTIAL", None,
                       "lenguaje de la pregunta no confirmado en el alcance analizado", qid,
                       missing=[language])
    coverage = scope.get("coverage")
    if coverage not in COVERAGES:
        raise ResearchError("scope.coverage inválida")
    omissions_complete = scope.get("omissions_complete")
    if type(omissions_complete) is not bool:
        raise ResearchError("scope.omissions_complete debe ser booleano observado")
    omitted = _list(scope.get("omitted_files"), "scope.omitted_files")
    if any(not isinstance(item, dict) for item in omitted):
        raise ResearchError("scope.omitted_files debe contener objetos")
    _unique(omitted, "path", "scope.omitted_files")
    if coverage == "complete" and omitted:
        raise ResearchError("cobertura completa contradice ficheros omitidos")
    if not omissions_complete or coverage == "unknown":
        audit = _list(scope.get("review_query_ids", []), "scope.review_query_ids")
        return _result("IN_PROGRESS" if not audit and attempts < budget else "PARTIAL",
                       "assess-coverage" if not audit and attempts < budget else None,
                       "CogniCode no ha permitido verificar exhaustivamente las omisiones", qid)
    if coverage == "partial" and not omitted:
        return _result("PARTIAL", None,
                       "cobertura parcial sin inventario verificable de archivos omitidos", qid)

    unresolved = []
    to_review = []
    for item in omitted:
        path = _str(item.get("path"), "omission.path")
        relevance = item.get("relevance")
        if relevance not in {"relevant", "irrelevant", "unknown"}:
            raise ResearchError("omission.relevance inválida")
        audits = _list(item.get("review_query_ids", []), "omission.review_query_ids")
        if relevance == "relevant":
            unresolved.append(path)
            continue
        if not audits:
            to_review.append(path)
            continue
        grounded_audit = any(
            query_id in by_query and
            by_query[query_id].get("mode") in STRUCTURED_MODES and
            by_query[query_id].get("status") == "ok" and
            path in by_query[query_id].get("coverage_paths", [])
            for query_id in audits
        )
        if relevance == "unknown" or not grounded_audit:
            unresolved.append(path)
    if unresolved:
        return _result("PARTIAL", None,
                       "archivos omitidos relevantes/no verificables: no cerrar la vista como implementada",
                       qid, missing=unresolved)
    if to_review:
        can_review = attempts < budget
        return _result("IN_PROGRESS" if can_review else "PARTIAL",
                       "assess-omissions" if can_review else None,
                       "comprobar relevancia de archivos omitidos mediante consultas estructuradas de CogniCode",
                       qid, missing=to_review)
    return _result("EVIDENCE_READY", None,
                   "claims respaldados; cobertura " + coverage +
                   (" (omisiones justificadas, no cobertura global)" if omitted else ""),
                   qid)

def decide(research: dict | None) -> dict:
    """Select one justified next action; no guessed tools or unverifiable success."""
    if research is None:
        return _result("IN_PROGRESS", "formulate-question",
                       "debe existir una pregunta concreta antes de modelar")
    if not isinstance(research, dict):
        raise ResearchError("research debe ser objeto")

    question = research.get("question")
    if not isinstance(question, dict):
        return _result("IN_PROGRESS", "formulate-question",
                       "faltan pregunta, lenguaje y objetivo")
    qid = _str(question.get("id"), "question.id")
    _str(question.get("text"), "question.text")
    language = _str(question.get("language"), "question.language")
    kind = _str(question.get("kind"), "question.kind")
    target = _str(question.get("target"), "question.target")
    if kind not in QUESTION_ROLES:
        raise ResearchError(f"question.kind no soportado: {kind}")

    catalog = research.get("catalog", "unknown")
    if catalog not in {"unknown", "observed"}:
        raise ResearchError("research.catalog inválido")
    if catalog != "observed":
        return _result("IN_PROGRESS", "discover-capabilities",
                       "descubrir herramientas y esquemas del runtime real", qid)

    caps = _list(research.get("capabilities", []), "capabilities")
    queries = _list(research.get("queries", []), "queries")
    claims = _list(research.get("claims", []), "claims")
    diagram_ids = _list(research.get("diagram_claim_ids", []), "diagram_claim_ids")
    budget = research.get("max_queries", 4)
    if type(budget) is not int or not 1 <= budget <= 12:
        raise ResearchError("max_queries debe estar entre 1 y 12")
    for name, items in (("capabilities", caps), ("queries", queries), ("claims", claims)):
        if any(not isinstance(x, dict) for x in items):
            raise ResearchError(f"{name}: entradas deben ser objetos")
    _unique(caps, "name", "capabilities")
    _unique(queries, "id", "queries")
    _unique(claims, "id", "claims")
    if len(diagram_ids) != len(set(diagram_ids)) or any(not isinstance(x, str) for x in diagram_ids):
        raise ResearchError("diagram_claim_ids inválidos o duplicados")

    # Each advertised tool has independent probes for the actual project languages.
    # One successful Rust probe can never authorize Kotlin queries.
    cap_names = {c["name"] for c in caps}
    cap_by_name = {c["name"]: c for c in caps}
    for c in caps:
        _str(c.get("role"), "capability.role")
        languages = _list(c.get("languages"), "capability.languages")
        if any(not isinstance(v, str) or not v for v in languages):
            raise ResearchError("capability.languages inválido")
        if type(c.get("advertised")) is not bool or type(c.get("schema_observed")) is not bool:
            raise ResearchError("capability requiere advertised y schema_observed observados")
        probes = c.get("probes")
        if not isinstance(probes, dict) or set(probes) - set(languages):
            raise ResearchError("capability.probes debe asociar sondeos solo a lenguajes anunciados")
        for probe_language, probe in probes.items():
            if not isinstance(probe, dict) or probe.get("status") not in PROBE_STATES:
                raise ResearchError("probe.status inválido")
            if probe["status"] != "untried":
                _str(probe.get("query_id"), "probe.query_id")
            if probe["status"] in {"usable", "partial"}:
                _str(probe.get("symbol_id"), "probe.symbol_id")
                _str(probe.get("location"), "probe.location")
                if probe.get("coverage") not in COVERAGES:
                    raise ResearchError("probe.coverage inválida")
                if probe.get("context") not in {"present", "missing", "unknown"} or probe.get("relations") not in {"present", "missing", "unknown"}:
                    raise ResearchError("probe.context/relations deben estar observados")

    for query in queries:
        if _str(query.get("question_id"), "query.question_id") != qid:
            raise ResearchError("no mezclar consultas de otra pregunta")
        tool = _str(query.get("capability"), "query.capability")
        if tool not in cap_names:
            raise ResearchError("consulta a capacidad no descubierta: " + tool)
        if (query.get("mode") in DENIED_MODES or tool == "read_file" or
                (tool == "search_content" and query.get("mode") != "text_candidate")):
            return _result("BLOCKED", None,
                           "se utilizó lectura raw/directa u otro indexador: no puede acreditarse exclusividad",
                           qid, tool)
        if query.get("mode") not in STRUCTURED_MODES | {"text_candidate"}:
            raise ResearchError("query.mode desconocido")
        if query.get("mode") in STRUCTURED_MODES:
            witness = cap_by_name[tool]
            if (not witness["advertised"] or not witness["schema_observed"] or
                    language not in witness["languages"] or
                    witness["probes"].get(language, {}).get("status") not in {"usable", "partial"}):
                return _result("BLOCKED", None,
                               "consulta sin esquema/prueba funcional para este lenguaje; no certificable",
                               qid, tool)
        if query.get("status") not in QUERY_STATES or query.get("coverage") not in COVERAGES:
            raise ResearchError("query.status/coverage inválidos")
        if _str(query.get("target"), "query.target") != target:
            raise ResearchError("consulta fuera del símbolo/alcance de la pregunta")
        if not isinstance(query.get("symbol_ids", []), list) or not isinstance(query.get("relation_ids", []), list):
            raise ResearchError("query.symbol_ids/relation_ids deben ser listas")

    by_query = {q["id"]: q for q in queries}
    by_claim = {c["id"]: c for c in claims}
    if any(cid not in by_claim for cid in diagram_ids):
        raise ResearchError("el diagrama menciona claims inexistentes")
    grounded = []
    ungrounded = []
    for claim_id in diagram_ids:
        claim = by_claim[claim_id]
        claim_kind = claim.get("kind")
        if claim.get("question_id") != qid or claim_kind not in {"entity", "relation"} or claim.get("status") != "observed":
            ungrounded.append(claim_id)
            continue
        plane = claim.get("plane")
        if plane not in PLANES:
            ungrounded.append(claim_id)
            continue
        refs = claim.get("query_ids", [])
        if not isinstance(refs, list) or not refs:
            ungrounded.append(claim_id)
            continue
        def supports(query: dict) -> bool:
            if query.get("mode") not in STRUCTURED_MODES or query.get("status") not in {"ok", "partial"}:
                return False
            if query.get("observation_plane", "static") != plane:
                return False
            if claim_kind == "entity":
                return bool(claim.get("symbol_id")) and claim["symbol_id"] in query.get("symbol_ids", [])
            return (bool(claim.get("relation_id")) and
                    claim["relation_id"] in query.get("relation_ids", []) and
                    bool(claim.get("from_symbol")) and bool(claim.get("to_symbol")) and
                    claim["from_symbol"] in query.get("symbol_ids", []) and
                    claim["to_symbol"] in query.get("symbol_ids", []))
        if any(qid_ref in by_query and supports(by_query[qid_ref]) for qid_ref in refs):
            grounded.append(claim_id)
        else:
            ungrounded.append(claim_id)
    if diagram_ids and not ungrounded:
        return _assess_scope(research.get("scope"), qid, language, by_query, budget,
                             sum(q["mode"] in STRUCTURED_MODES for q in queries))

    # Claims without references are not evidence; text search only locates candidates.
    if ungrounded:
        return _result("PARTIAL", "justify-claims",
                       "no se puede dibujar como implementado: faltan vínculos estructurados",
                       qid, missing=ungrounded)
    if any(q.get("mode") == "text_candidate" for q in queries) and not any(q.get("mode") in STRUCTURED_MODES for q in queries):
        # Do not certify a candidate from text; try eligible structured probes below.
        pass

    attempts = [q for q in queries if q.get("mode") in STRUCTURED_MODES]
    if len(attempts) >= budget:
        return _result("PARTIAL", None,
                       "límite de consultas alcanzado sin evidencia suficiente; marcar UNKNOWN", qid)
    roles = QUESTION_ROLES[kind]
    candidates = sorted(
        (c for c in caps if c["role"] in roles and language in c["languages"] and
         c["advertised"] and c["schema_observed"] and c["name"] not in TEXT_ONLY_TOOLS),
        key=lambda c: (roles.index(c["role"]), c["name"]),
    )
    if not candidates:
        return _result("PARTIAL", None,
                       "sin capacidad estructurada comprobable para esta pregunta y lenguaje; no declarar lenguaje incompatible",
                       qid)
    for cap in candidates:
        probe = cap["probes"].get(language, {"status": "untried"})
        if probe["status"] == "untried":
            return _result("IN_PROGRESS", "probe-capability",
                           "probar sobre símbolo real identidad, ubicación, contexto, relaciones y cobertura",
                           qid, cap["name"])
        if probe["status"] not in {"usable", "partial"}:
            continue
        if not any(q["capability"] == cap["name"] and q.get("mode") in STRUCTURED_MODES for q in attempts):
            return _result("IN_PROGRESS", "query-structured",
                           "consultar operación estructurada pertinente, no read_file(raw)/search_content",
                           qid, cap["name"])
    return _result("PARTIAL", None,
                   "capacidades pertinentes ya probadas sin progreso; documentar UNKNOWN o formular otra pregunta",
                   qid)
