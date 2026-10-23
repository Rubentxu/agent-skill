"""The shape of the derived evidence, and what each claim actually earns.

Two things live here, and they are the same thing seen from both sides:

- **The shape.** What a query and a claim look like when they follow the
  published contract. The field names are declared once, in this module, so
  that the documents and the code cannot drift apart: the documents name
  these fields, and a test executes the example the documents publish.

- **The verdict.** What a claim is worth, *derived* from the queries that
  support it. A writer may say a claim was observed; only the queries can
  say it is corroborated. When the two disagree, the disagreement is
  reported, not smoothed over.

No access to Git, checkout, runtime or services. IDs alone are not evidence.
"""
from __future__ import annotations

# --------------------------------------------------------------------------
# The shape.
#
# These are the names the published contract uses. They are data, not prose,
# so that a document and this module can be compared mechanically.
# --------------------------------------------------------------------------

QUERY_REQUIRED = ("query_id", "mode", "status", "observation_plane", "source")
QUERY_CORROBORATING = ("symbol_ids",)
CLAIM_REQUIRED = ("claim_id", "kind", "provenance", "plane", "coverage", "query_ids")

# The vocabularies a claim declares with. A value outside them is a claim
# nobody will be able to read later, so the recorder refuses it at the
# door instead of filing it unreadable.
CLAIM_KINDS = ("entity", "relation")
CLAIM_COVERAGES = ("complete", "partial", "unknown")

# Los campos sin los cuales la afirmacion no se puede mirar. Los demas
# son forma: se avisa de ellos, pero la afirmacion se sigue leyendo.
CLAIM_BLOCKING = ("claim_id", "kind", "provenance")

# Spellings seen in ledgers written before the shape was fixed. They are
# read — under the legacy version 1 — so the ledger is not lost, and
# reported, so the drift is visible. Under version 2 they are a broken
# promise: the shape has one authority, and it is not whoever writes by
# hand.
CLAIM_ALIASES = {
    "claim_id": ("id",),
    "provenance": ("status",),
    "symbol_id": ("symbol_ids",),
}
QUERY_ALIASES = {
    "query_id": ("id",),
}

# A query only corroborates when the engine answered in a mode where symbols
# are resolved, not merely named.
QUERY_MODES = ("structured", "symbol_context")
QUERY_STATUSES = ("ok", "partial")
QUERY_SOURCES = ("cognicode",)
QUERY_PLANES = ("static",)

# The revision of the repository a query was looking at when it ran. It is
# optional: a query that does not declare it is still a valid query, and
# what it omits stays unknown instead of being assumed.
REPOSITORY_REVISION = "repository_revision"

# Optional fields a query may declare. They are read, never required: a
# query without them is still a valid query, and every projection that
# cites it has to carry what it omits instead of filling it in.
QUERY_OPTIONAL = ("limitations", "symbol_locations", "impact",
                  REPOSITORY_REVISION)

# Provenance: what the observation *was*. The writer says this.
IMPLEMENTATION_PROVENANCE = ("OBSERVED_CODE", "observed")
INTENT_PROVENANCE = ("CODE_DOC", "CURATED_INTENT")
UNCERTAIN_PROVENANCE = ("INFERRED", "inferred", "UNKNOWN", "unknown")
CLAIM_PROVENANCE = IMPLEMENTATION_PROVENANCE + INTENT_PROVENANCE + UNCERTAIN_PROVENANCE

# Provenance of a relation: where the relation comes from.
GRAPH_EDGE = "graph_edge"
REFERENCE_LINK = "reference_link"

# Keys in a query summary that count how many results came back. A count of
# zero here means the query answered with nothing.
RESULT_COUNT_KEYS = ("total", "entries", "results", "hits", "matches")

# --------------------------------------------------------------------------
# The verdict: what the evidence supports. Derived, never asserted.
# --------------------------------------------------------------------------

CORROBORATED = "corroborated"
OBSERVED_NOT_CORROBORATED = "observed_not_corroborated"
NOT_IMPLEMENTATION = "not_implementation"

# Una afirmacion que el material no deja comprobar.
#
# No es lo mismo que una afirmacion observada y sin corroborar: aquella se
# miro y no la sostiene ninguna consulta, y el reproche es justo; esta no se
# pudo mirar. Decirle a un material que sus afirmaciones no estan
# corroboradas cuando lo que pasas es que no se le puede mirar es una
# acusacion falsa, y por eso tiene su propio veredicto.
NOT_CHECKABLE = "not_checkable"

# La version del contrato que este modulo comprueba.
#
# El material declara la suya, y declararla es una promesa: la forma que se
# comprueba es la de la version declarada. Bajo la version 2 la forma es
# una sola y se cumple entera: cualquiera de las grafias antiguas, o un
# campo requerido ausente, es un material que miente sobre lo que declara,
# y se lee como ilegible. La version 1 es legado: se lee con sus grafias
# antiguas y el desvio se informa. Un material que declara otra version es
# un material de otro contrato: este no lo puede leer.
CONTRACT_VERSION = 2

# Las versiones que este modulo sigue leyendo con las grafias antiguas.
LEGACY_VERSIONS = (1,)

# Labels for humans, in the language of the people who read the atlas.
VERDICT_LABELS = {
    CORROBORATED: "corroborada por una consulta estructurada",
    OBSERVED_NOT_CORROBORATED: "observada, pero sin corroborar",
    NOT_IMPLEMENTATION: "no es una afirmacion de implementacion",
    NOT_CHECKABLE: "no se pudo comprobar: el material no lo permite",
}


def _text(value) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def index_queries(raw: list | dict) -> dict[str, dict]:
    """Index queries by their identifier.

    The identifier may be spelled `query_id` or `id`; both are accepted so
    that a ledger written before the contract was fixed is still readable.
    What it *means* to be missing is reported elsewhere.
    """
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


def index_claims(raw: list | dict) -> dict[str, dict]:
    """Index claims by their identifier, tolerating the older spelling."""
    if isinstance(raw, dict):
        raw = raw.get("claims")
    if not isinstance(raw, list):
        raise ValueError("claims must be a list")
    result = {}
    for c in raw:
        if not isinstance(c, dict):
            raise ValueError("invalid claim")
        key = c.get("claim_id", c.get("id"))
        if not isinstance(key, str) or not key or key in result:
            raise ValueError("missing or duplicate claim ID")
        result[key] = c
    return result


def provenance_of(claim: dict) -> str:
    """The provenance a claim asserts, or UNKNOWN when it asserts nothing."""
    value = claim.get("provenance", claim.get("status"))
    return value if isinstance(value, str) and value else "UNKNOWN"


def revision_of(query: dict) -> str | None:
    """The repository revision a query declares, or None when it declares none.

    The revision travels with the query that observed it: it is declared by
    whoever collected the evidence, and only that declaration counts. It is
    never guessed, never resolved from the checkout and never asked to Git,
    so an absent declaration means the revision is unknown, not that it is
    the revision the code has now.
    """
    if not isinstance(query, dict):
        return None
    value = query.get(REPOSITORY_REVISION)
    return value if isinstance(value, str) and value.strip() else None


def corroborated(claim: dict, queries: dict[str, dict]) -> bool:
    """True iff a successful structured query identifies this exact edge.

    This is the gate for *implementation* evidence: a relation counts only
    when the graph operation itself returned its identifier. A usage or a
    reference is not an edge and is never promoted to one, however exactly
    its endpoints are named.
    """
    if not isinstance(claim, dict) or provenance_of(claim) not in IMPLEMENTATION_PROVENANCE:
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
    if kind == "relation" and claim.get("relation_source") != GRAPH_EDGE:
        return False
    for qid in ids:
        q = queries[qid]
        if not _query_is_structured(q):
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


def reference_corroborated(claim: dict, queries: dict[str, dict]) -> bool:
    """True iff a structured usage result backs this reference, with its row.

    The second provenance the contract declares: a localised use, proved by
    the query that found it, by the row inside that answer and by the place
    on disk where it was found. It proves *a use*, never a call, a dependency
    or a runtime relation.
    """
    if not isinstance(claim, dict) or provenance_of(claim) not in IMPLEMENTATION_PROVENANCE:
        return False
    if claim.get("kind") != "relation":
        return False
    if claim.get("relation_source") != REFERENCE_LINK:
        return False
    if claim.get("plane", "static") != "static":
        return False
    reference = claim.get("reference")
    if not isinstance(reference, dict):
        return False
    qid = reference.get("query_id")
    index = reference.get("index")
    path = reference.get("path")
    line = reference.get("line")
    if not isinstance(qid, str) or not qid or qid not in queries:
        return False
    if not isinstance(index, int):
        return False
    if not isinstance(path, str) or not path:
        return False
    if not isinstance(line, int):
        return False
    query = queries[qid]
    if not _query_is_structured(query):
        return False
    hits = query.get("reference_hits")
    if not isinstance(hits, list):
        return False
    for hit in hits:
        if not isinstance(hit, dict):
            continue
        if hit.get("index") != index:
            continue
        if hit.get("path") != path:
            continue
        if hit.get("line") != line:
            continue
        # The row exists in the answer. The endpoints still have to be
        # resolved symbols seen by a structured query of the same question.
        endpoints = [claim.get("from_symbol"), claim.get("to_symbol")]
        if not all(isinstance(symbol, str) and symbol for symbol in endpoints):
            return False
        for other in claim.get("query_ids", []):
            if not isinstance(other, str) or other not in queries:
                continue
            symbols = queries[other].get("symbol_ids")
            if not isinstance(symbols, list):
                continue
            if all(symbol in symbols for symbol in endpoints):
                return True
    return False


def _query_is_structured(query: dict) -> bool:
    """True iff the engine answered in a mode where symbols are resolved."""
    if not isinstance(query, dict):
        return False
    if query.get("source", "cognicode") not in QUERY_SOURCES:
        return False
    if query.get("mode") not in QUERY_MODES:
        return False
    if query.get("status") not in QUERY_STATUSES:
        return False
    if query.get("observation_plane", "static") not in QUERY_PLANES:
        return False
    return True


def claim_gaps(claim: dict) -> list[str]:
    """What the claim itself does not say in the canonical shape.

    Reported per claim, because a claim that does not follow the shape
    cannot be corroborated by anything: there is no way to know what was
    actually observed.
    """
    gaps: list[str] = []
    if not isinstance(claim, dict):
        return ["la afirmacion no es un objeto"]

    for field in CLAIM_REQUIRED:
        if field in claim:
            continue
        aliases = CLAIM_ALIASES.get(field, ())
        used = next((alias for alias in aliases if alias in claim), None)
        if used is not None:
            gaps.append(f"usa '{used}' en vez de '{field}'")
        else:
            gaps.append(f"falta '{field}'")
    if claim.get("kind") == "entity" and "symbol_id" not in claim:
        if "symbol_ids" in claim:
            gaps.append("usa 'symbol_ids' en vez de 'symbol_id'")
        else:
            gaps.append("falta 'symbol_id'")
    if claim.get("kind") == "relation":
        source = claim.get("relation_source")
        if source == GRAPH_EDGE:
            for field in ("relation_id", "from_symbol", "to_symbol"):
                if not _text(claim.get(field)):
                    gaps.append(f"falta '{field}'")
        elif source == REFERENCE_LINK:
            if not isinstance(claim.get("reference"), dict):
                gaps.append("falta 'reference' (query_id + index + path + linea)")
            else:
                reference = claim["reference"]
                for field in ("query_id", "index", "path", "line"):
                    if field not in reference:
                        gaps.append(f"'reference' no declara '{field}'")
        else:
            gaps.append(
                f"declara 'relation_source' '{source}', que no es una procedencia del contrato: "
                "solo se admiten 'graph_edge' y 'reference_link'"
            )
    return gaps


def query_gaps(qid: str, query) -> list[str]:
    """What a query does not say in the canonical shape.

    A query that does not say how it ran cannot corroborate anything: the
    platform would be counting as support something it cannot tell apart
    from a query that returned nothing.
    """
    gaps: list[str] = []
    if not isinstance(query, dict):
        return [f"la consulta '{qid}' no es un objeto"]
    for field in QUERY_REQUIRED:
        if field in query:
            continue
        aliases = QUERY_ALIASES.get(field, ())
        used = next((alias for alias in aliases if alias in query), None)
        if used is not None:
            gaps.append(f"la consulta '{qid}' usa '{used}' en vez de '{field}'")
        else:
            gaps.append(f"la consulta '{qid}' no declara '{field}'")
    if not isinstance(query.get("symbol_ids"), list):
        gaps.append(f"la consulta '{qid}' no declara 'symbol_ids': no identifica ningun simbolo")
    return gaps


def impedimentos(claim: dict, queries: dict[str, dict]) -> list[str]:
    """What stops this claim from being looked at, if anything does.

    A claim can be looked at when the platform can tell what it claims
    and when the queries that should support it say how they ran. When
    it cannot, there is no verdict to give: there is a hole, and the hole
    says what is missing.

    What is *not* an impediment is a claim that offers no support at all:
    that one was seen and nothing backs it, which is a finding about the
    claim. An old spelling is not an impediment either: the claim is
    read, and the drift is reported.
    """
    impedimentos_: list[str] = []
    if not isinstance(claim, dict):
        return ["la afirmacion no es un objeto"]

    for field in CLAIM_BLOCKING:
        if field in claim:
            continue
        if any(alias in claim for alias in CLAIM_ALIASES.get(field, ())):
            # Se lee igual. La diferencia de escritura se cuenta aparte.
            continue
        impedimentos_.append(f"falta '{field}'")
    if claim.get("kind") == "entity" and "symbol_id" not in claim and "symbol_ids" not in claim:
        impedimentos_.append("falta 'symbol_id'")

    citados = [qid for qid in claim.get("query_ids", []) if isinstance(qid, str)] \
        if isinstance(claim.get("query_ids"), list) else []
    if not citados:
        return impedimentos_
    for qid in citados:
        if qid not in queries:
            impedimentos_.append(f"la consulta '{qid}' no existe")
    utilizables = [qid for qid in citados
                   if qid in queries and not query_gaps(qid, queries[qid])]
    if not utilizables:
        for qid in citados:
            if qid in queries:
                impedimentos_.extend(query_gaps(qid, queries[qid]))
        impedimentos_.append("ninguna de sus consultas declara como se ejecuto")
    return impedimentos_


def shape_gaps(claim: dict, queries: dict[str, dict]) -> list[str]:
    """What the claim and its queries do not say in the canonical shape.

    Reported per claim, because a claim that does not follow the shape
    cannot be corroborated by anything: there is no way to know what was
    actually observed.
    """
    gaps = claim_gaps(claim)
    for qid in claim.get("query_ids", []) if isinstance(claim.get("query_ids"), list) else []:
        query = queries.get(qid) if isinstance(qid, str) else None
        if query is None:
            gaps.append(f"la consulta '{qid}' no existe")
            continue
        gaps.extend(query_gaps(qid, query))
    return gaps


def evidence_gaps(claim: dict, queries: dict[str, dict]) -> list[str]:
    """What the queries do not prove, in the words of what they did return.

    The shape can be perfect and the evidence still be thin: the query
    answered, but with nothing, or without resolving the symbols the claim
    is about. Those are different facts and both have to be said.
    """
    gaps: list[str] = []
    kind = claim.get("kind", "entity")
    ids = [qid for qid in claim.get("query_ids", []) if isinstance(qid, str)] \
        if isinstance(claim.get("query_ids"), list) else []

    if kind == "entity":
        symbol = claim.get("symbol_id")
        if isinstance(symbol, str) and symbol:
            resolved = any(
                isinstance(q.get("symbol_ids"), list) and symbol in q["symbol_ids"]
                for qid, q in queries.items()
                if isinstance(q, dict) and _query_is_structured(q)
            )
            if not resolved:
                gaps.append(f"ninguna consulta estructurada identifica '{symbol}' como simbolo resuelto")

    if kind == "relation":
        source = claim.get("relation_source")
        if source not in (GRAPH_EDGE, REFERENCE_LINK):
            gaps.append(
                f"'relation_source' es '{source}', que no es una procedencia del contrato: "
                "una relacion se apoya en 'graph_edge' o en 'reference_link'"
            )
        endpoints = [claim.get("from_symbol"), claim.get("to_symbol")]
        if all(isinstance(endpoint, str) and endpoint for endpoint in endpoints):
            resolved = any(
                isinstance(q.get("symbol_ids"), list)
                and all(endpoint in q["symbol_ids"] for endpoint in endpoints)
                for qid, q in queries.items()
                if isinstance(q, dict) and _query_is_structured(q)
            )
            if not resolved:
                gaps.append(
                    f"ninguna consulta estructurada identifica '{endpoints[0]}' y '{endpoints[1]}' "
                    "como simbolos resueltos"
                )

    empty = [qid for qid in ids if _query_returned_nothing(queries.get(qid))]
    if empty and len(empty) == len(ids):
        gaps.append("ninguna de sus consultas devolvio 0 resultados: no puede sostener la afirmacion")
    elif empty:
        gaps.append(f"la consulta '{empty[0]}' devolvio 0 resultados: no puede sostener la afirmacion")
    return gaps


def _query_returned_nothing(query) -> bool:
    """True iff the query's own summary says it returned no results.

    Only the keys that count results are read. A count of zero for
    something else (how many tools a server lists) is a finding in itself
    and must not be read as "the query returned nothing".
    """
    if not isinstance(query, dict):
        return False
    summary = query.get("result_summary")
    if not isinstance(summary, dict):
        return False
    counts = [summary[key] for key in RESULT_COUNT_KEYS
              if isinstance(summary.get(key), int) and not isinstance(summary.get(key), bool)]
    return bool(counts) and all(count == 0 for count in counts)


def verdict(claim: dict, queries: dict[str, dict]) -> tuple[str, list[str]]:
    """What the claim actually earns, and what is missing to earn more.

    The verdict is derived from the queries. A claim that says it was
    observed but cannot be corroborated is reported as such: it was seen,
    but nothing structured proves it.

    When the material does not let the platform look at the claim, there
    is no verdict at all. There is a hole, and the hole says what is
    missing: that is a different fact, and it is not a reproach.
    """
    if not isinstance(claim, dict):
        return NOT_IMPLEMENTATION, ["la afirmacion no es un objeto"]

    provenance = provenance_of(claim)
    if provenance not in IMPLEMENTATION_PROVENANCE:
        return NOT_IMPLEMENTATION, []

    if corroborated(claim, queries):
        return CORROBORATED, []
    if reference_corroborated(claim, queries):
        return CORROBORATED, []

    # The shape comes before the evidence. When the material does not say
    # enough to look at the claim, the absence of corroboration is an
    # effect of the material, not a fact about the claim.
    impedimentos_ = impedimentos(claim, queries)
    if impedimentos_:
        return NOT_CHECKABLE, impedimentos_

    gaps = evidence_gaps(claim, queries)
    if not gaps:
        gaps = ["ninguna consulta estructurada identifica lo que la afirmacion sostiene"]
    return OBSERVED_NOT_CORROBORATED, gaps


def _strict_violations(nombre: str, raw: dict, gaps: list[str]) -> bool:
    """Item by item, what does not follow the shape the material declares.

    Only called for material that declares the current version: that
    declaration says the drift is gone, so every old spelling and every
    missing required field is named here, and the caller reads the
    material as what it is — a ledger that lied about itself. Returns
    whether anything was found.
    """
    es_afirmaciones = nombre == "las afirmaciones"
    collection = "claims" if es_afirmaciones else "queries"
    items = raw.get(collection)
    if not isinstance(items, list):
        gaps.append(f"{nombre} declaran la version {CONTRACT_VERSION} "
                    f"y no traen la lista '{collection}'")
        return True
    donde = f"{nombre} declaran la version {CONTRACT_VERSION} y"
    habia = len(gaps)
    for item in items:
        if not isinstance(item, dict):
            gaps.append(f"{donde} traen una entrada que no es un objeto")
            continue
        identificador = item.get("claim_id", item.get("query_id", item.get("id")))
        if es_afirmaciones:
            gaps.extend(f"{donde} la afirmacion '{identificador}' {gap}"
                        for gap in claim_gaps(item))
        else:
            gaps.extend(f"{donde} {gap}"
                        for gap in query_gaps(str(identificador), item))
    return len(gaps) > habia


def material_status(claims_raw: list | dict, queries_raw: list | dict) -> tuple[str, list[str]]:
    """Whether this contract can read the material, and what it misses.

    The version is a promise. A material that declares the current version
    says the drift is gone, and the platform checks it item by item: an
    old spelling or a missing required field makes the material unreadable,
    because its verdicts would be about a shape it did not promise. A
    material of a legacy version is read with its old spellings and the
    drift is reported, so ledgers written before the shape was fixed are
    not lost. A material that declares another version is a material of
    another contract: this contract cannot read it, and saying so is
    better than returning verdicts that would be about a shape nobody
    promised.
    """
    gaps: list[str] = []
    ilegible = False
    for nombre, raw in (("las afirmaciones", claims_raw), ("las consultas", queries_raw)):
        if not isinstance(raw, dict):
            continue
        version = raw.get("schema_version")
        if version is None:
            gaps.append(f"{nombre} no declaran la version del contrato")
        elif version == CONTRACT_VERSION:
            if _strict_violations(nombre, raw, gaps):
                ilegible = True
        elif version in LEGACY_VERSIONS:
            gaps.append(
                f"{nombre} declaran la version {version} del contrato, que es legado: "
                "se leen las grafias antiguas y el desvio se informa"
            )
        else:
            ilegible = True
            gaps.append(
                f"{nombre} declaran la version {version} del contrato "
                f"y este comprueba la {CONTRACT_VERSION}"
            )
    return ("unreadable" if ilegible else "current"), gaps


def report(claims_raw: list | dict, queries_raw: list | dict) -> dict:
    """A per-claim report of what each claim earns and what is missing.

    This is the whole point of the module: the operator sees, for every
    claim, whether the evidence supports it and, when it does not, exactly
    what is absent.
    """
    status, gaps = material_status(claims_raw, queries_raw)
    queries = index_queries(queries_raw)
    claims = index_claims(claims_raw)
    entries = []
    for cid, claim in claims.items():
        derived, missing = verdict(claim, queries)
        entries.append({
            "claim_id": cid,
            "kind": claim.get("kind", "entity"),
            "provenance": provenance_of(claim),
            "verdict": derived,
            "verdict_label": VERDICT_LABELS[derived],
            "missing": missing,
        })
    if status != "current":
        # El material es de otro contrato: no hay nada que decir de sus
        # afirmaciones, y decirlo seria inventar un veredicto.
        entries = []
    return {
        "status": status,
        "gaps": gaps,
        "claims": entries,
        "corroborated": sum(1 for e in entries if e["verdict"] == CORROBORATED),
        "not_corroborated": sum(1 for e in entries if e["verdict"] == OBSERVED_NOT_CORROBORATED),
        "not_checkable": sum(1 for e in entries if e["verdict"] == NOT_CHECKABLE),
        "not_implementation": sum(1 for e in entries if e["verdict"] == NOT_IMPLEMENTATION),
    }
