"""Incremental knowledge navigation from *derived* CogniCode ledgers and views.

No code inspection, no new facts, no DB, no projector execution. Rebuildable data.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from evidence_contract import (
    CORROBORATED,
    OBSERVED_NOT_CORROBORATED,
    corroborated,
    index_queries,
    verdict,
)

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
    for name in ("claims.json", "queries.json", "terms.json"):
        p = workspace / "evidence" / name
        _safe(p, workspace)
        if p.exists():
            if not p.is_file():
                raise KnowledgeError("knowledge input is not a file")
            result.append(p)
    # Moldable reports are owned projections, never evidence sources.
    reports = workspace / "reports"
    _safe(reports, workspace)
    if reports.exists():
        if not reports.is_dir():
            raise KnowledgeError("invalid reports directory")
        for p in sorted(reports.iterdir()):
            _safe(p, workspace)
            if p.name.endswith((".report.json", ".report.md")):
                if not p.is_file():
                    raise KnowledgeError("invalid moldable report")
                result.append(p)
    capsules = workspace / "handoffs"
    _safe(capsules, workspace)
    if capsules.exists():
        if not capsules.is_dir():
            raise KnowledgeError("invalid handoff directory")
        entries = sorted(capsules.iterdir())
        if len(entries) > 160:
            raise KnowledgeError("too many handoff artifacts")
        for p in entries:
            _safe(p, workspace)
            if p.name.endswith((".capsule.json", ".capsule.md")):
                if not p.is_file():
                    raise KnowledgeError("invalid handoff artifact")
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
    # Owned contextual navigation is derived, not a source of architectural facts.
    moldable = workspace / "navigation" / "moldable"
    _safe(moldable, workspace)
    if moldable.exists():
        if not moldable.is_dir():
            raise KnowledgeError("moldable navigation folder invalid")
        pages = sorted(moldable.iterdir())
        if len(pages) > 200:
            raise KnowledgeError("too many moldable navigation pages")
        for p in pages:
            _safe(p, workspace)
            if p.name.endswith((".moldable.json", ".moldable.html")):
                if not p.is_file():
                    raise KnowledgeError("invalid moldable navigation input")
                result.append(p)
    return result


def fingerprints(workspace: Path, *, known_inputs: list[Path] | None = None) -> dict[str, str]:
    """Hash existing artifacts without rediscovering the same workspace N times."""
    result = {}
    for p in (inputs(workspace) if known_inputs is None else known_inputs):
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
    discovered = inputs(workspace)
    digests = fingerprints(workspace, known_inputs=discovered)
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

    queries = {}
    if qfile.is_file():
        try:
            queries = index_queries(_load(qfile, workspace))
        except ValueError as exc:
            raise KnowledgeError("invalid queries: " + str(exc)) from exc
        if any(qid not in queries for c in claims.values() for qid in c.get("query_ids", [])):
            raise KnowledgeError("claim references nonexistent query")

    by_claim = {}
    bound = 0
    for p in discovered:
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
        allowed = {str(a.relative_to(workspace))
                   for k in ("sources", "renders", "views") for a in catalog[lens].get(k, [])}
        if any(not isinstance(cid, str) or cid not in claims for cid in ids):
            raise KnowledgeError("view references missing claim")
        plane = view.get("plane", "implementation")
        if plane not in {"implementation", "intent"}:
            raise KnowledgeError("view has unknown plane")
        if any((claims[cid].get("category", "symbol") == "intent") != (plane == "intent") for cid in ids):
            raise KnowledgeError("intent-only claim cannot justify an implementation diagram")
        if plane == "implementation" and any(not corroborated(claims[cid], queries) for cid in ids):
            raise KnowledgeError("implementation view needs corroborated CogniCode code claims")
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
                # What the writer said and what the queries prove are two
                # facts. An observation that no query corroborates was still
                # observed: saying "unknown" would deny it, and saying
                # nothing would overstate it. So both are published.
                derived, _ = verdict(c, queries)
                if derived == CORROBORATED:
                    effective = f"{provenance} (corroborada)"
                elif derived == OBSERVED_NOT_CORROBORATED:
                    effective = f"{provenance} (sin corroborar)"
                elif provenance == "CODE_DOC" and (not ids or not qfile.is_file()):
                    effective = "UNKNOWN (sin query)"
                else:
                    effective = provenance
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
    # Index *only* owned report projections and link back to their claims.
    # Never interpret natural language in reports as implementation evidence.
    report_files = [p for p in discovered if p.name.endswith(".report.json")]
    if report_files:
        if len(report_files) > 100:
            raise KnowledgeError("too many moldable reports; narrow the workspace")
        lines.extend(["### Informes moldables (proyecciones, no fuentes de código)", ""])
        for report_path in report_files:
            report = _load(report_path, workspace)
            if not isinstance(report, dict) or report.get("generator") != "cognicode-diagrams-report-v1" or report.get("schema_version") != 1:
                raise KnowledgeError("unowned or invalid report manifest")
            rel_md = report_path.with_suffix(".md")
            _safe(rel_md, workspace)
            if not rel_md.is_file() or not rel_md.read_text(encoding="utf-8").startswith(
                "<!-- Generated by cognicode-diagrams report_thinking.py v1. -->"
            ):
                raise KnowledgeError("missing or unowned report markdown")
            evidence = report.get("evidence", {})
            ids = evidence.get("claim_ids") if isinstance(evidence, dict) else None
            if not isinstance(ids, list) or any(not isinstance(cid, str) or cid not in claims for cid in ids):
                raise KnowledgeError("report references missing claims")
            language = report.get("language")
            if not isinstance(language, dict) or not isinstance(language.get("label"), str):
                raise KnowledgeError("report without language metadata")
            report_kind = report.get("kind")
            if report_kind not in {"term-card", "symbol-passport", "change-impact"}:
                raise KnowledgeError("unknown moldable report kind")
            if report_kind == "change-impact":
                # A changed ledger/vocabulary/intent must not leave a plausible but
                # obsolete "ready to change" brief in the shared knowledge atlas.
                from report_thinking import project as report_project, ReportError
                change = report.get("change")
                target = report.get("target_id")
                if not isinstance(change, dict) or not isinstance(target, str):
                    raise KnowledgeError("change-impact requires explicit intent and target")
                try:
                    current = report_project(workspace, "change-impact", symbol=target,
                                             context=report.get("requested_context"),
                                             goal=change.get("goal"))
                except ReportError as exc:
                    raise KnowledgeError("invalid or stale change-impact brief") from exc
                if current != report:
                    raise KnowledgeError("change-impact brief stale: regenerate from CogniCode ledger")
                if report.get("change", {}).get("edit_authorized") is not False:
                    raise KnowledgeError("change-impact is not an edit authorization")
            lines.append("- [" + label(language["label"]) + " (" + label(report_kind) + ")](" +
                         href(rel_md, workspace / "navigation") + ")")
            lines.append("  - Estado: " + label(report.get("status", "UNKNOWN")) +
                         " · lenguaje: " + label(language.get("status", "unmapped")) +
                         " · claims: " + label(", ".join(ids) if ids else "ninguno"))
            lines.append("  - [JSON para agentes](" + href(report_path, workspace / "navigation") + ")")
        lines.append("")
    # Capsules are task-specific handoffs; never a second factual knowledge base.
    handoffs = [p for p in discovered if p.name.endswith(".capsule.json")]
    if handoffs:
        if len(handoffs) > 80:
            raise KnowledgeError("too many agent handoffs")
        from context_capsule import (
            GENERATOR as CAPSULE_GENERATOR, model as capsule_model,
            markdown as capsule_markdown, CapsuleError,
        )
        lines.extend(["### Cápsulas de traspaso para agentes (no verifican el checkout)", ""])
        for jp in handoffs:
            data = _load(jp, workspace)
            if not isinstance(data, dict) or data.get("generator") != CAPSULE_GENERATOR or data.get("schema_version") != 1:
                raise KnowledgeError("invalid agent handoff capsule")
            target, task = data.get("target"), data.get("task")
            if not isinstance(target, dict) or not isinstance(task, dict):
                raise KnowledgeError("handoff missing target or goal")
            try:
                current = capsule_model(workspace, target.get("symbol_id"),
                                        task.get("goal"), target.get("context_id"))
            except (CapsuleError, ValueError) as exc:
                raise KnowledgeError("handoff evidence unavailable or invalid") from exc
            if current != data:
                raise KnowledgeError("handoff capsule stale: revalidate with CogniCode and regenerate")
            md = jp.with_suffix(".md")
            _safe(md, workspace)
            if not md.is_file() or md.read_text(encoding="utf-8") != capsule_markdown(current):
                raise KnowledgeError("handoff Markdown missing, stale or unowned")
            ids = current["evidence"]["claim_ids"]
            if any(cid not in claims for cid in ids):
                raise KnowledgeError("handoff references missing claims")
            lines.append("- [" + label(target["symbol_id"]) + ": " +
                         label(task["goal"]) + "](" + href(md, workspace / "navigation") + ")")
            lines.append("  - PARTIAL_HANDOFF · código no revalidado · " +
                         label(current["language"]["status"]))
            lines.append("  - [Cápsula JSON para agentes](" + href(jp, workspace / "navigation") + ")")
        lines.append("")
    # Moldable pages are links to existing, reconcilable projections. Never
    # treat their labels or explanations as new architectural evidence.
    moldable_pages = [p for p in discovered if p.name.endswith(".moldable.json")]
    if moldable_pages:
        from moldable_views import GENERATOR as MOLDABLE_GENERATOR, MARKER as MOLDABLE_MARKER, project as moldable_project
        lines.extend(["### Navegación moldable por símbolo", ""])
        for p in moldable_pages:
            page = _load(p, workspace)
            if not isinstance(page, dict) or page.get("generator") != MOLDABLE_GENERATOR or page.get("schema_version") != 1:
                raise KnowledgeError("moldable page not owned by projector")
            target = page.get("target")
            if not isinstance(target, dict) or target.get("kind") != "symbol" or not isinstance(target.get("symbol_id"), str):
                raise KnowledgeError("moldable target invalid")
            if page != moldable_project(workspace, target["symbol_id"], target.get("context_id")):
                raise KnowledgeError("moldable page stale: regenerate from CogniCode ledger")
            hp = p.with_suffix(".html")
            _safe(hp, workspace)
            if not hp.is_file():
                raise KnowledgeError("moldable HTML is missing")
            html = hp.read_text(encoding="utf-8")
            if not html.startswith(MOLDABLE_MARKER) or 'http-equiv="Content-Security-Policy"' not in html:
                raise KnowledgeError("unowned or unsafe moldable HTML")
            lang = page.get("language", {})
            if not isinstance(lang, dict) or not isinstance(lang.get("label"), str):
                raise KnowledgeError("moldable label missing")
            lines.append("- [" + label(lang["label"]) + "](" + href(hp, workspace / "navigation") + ")" +
                         " · " + label(target["symbol_id"]) + " · " +
                         label(lang.get("status", "unmapped")))
            lines.append("  - [JSON de navegación para agentes](" + href(p, workspace / "navigation") + ")")
        lines.append("")
    return lines, digests, len(claims), bound
