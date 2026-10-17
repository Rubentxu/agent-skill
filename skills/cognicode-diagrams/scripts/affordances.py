#!/usr/bin/env python3
"""Derive HATEOAS-like links from OBSERVED state + local lens catalog.

Pure example: NO subprocess, files changed, network, CogniCode calls, or install.
Usage: python3 scripts/affordances.py examples/session-c4.json
       python3 scripts/affordances.py - < /tmp/state.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from research_protocol import ResearchError, decide as decide_research

BASE = Path(__file__).resolve().parents[1]
CATALOG = BASE / "references" / "lens-registry.json"
INTENTS = {"catalog", "setup", "scan", "discover", "create", "interpret", "translate", "review", "update", "validate", "preview", "atlas", "editorial"}
ENVS = {"unknown", "missing", "cli_ready", "mcp_ready", "both_ready"}
WORKSPACES = {"unknown", "absent", "incomplete", "ready", "invalid"}
EVIDENCE = {"absent", "symbols_ready", "graph_ready", "partial", "stale"}
BASIS = {"unknown", "current", "stale"}
MODELS = {"absent", "draft", "reviewed"}
ARTIFACTS = {"absent", "draft", "valid", "invalid"}
VALIDATORS = {"missing", "available"}
SUPPORT = {"native", "adapted", "unsupported"}
READY = "ready"
STATUSES = {"ready", "planned"}
# Los formatos se obtienen del registro, no de una whitelist codificada en el router.
SLUG = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z")

LINKS = {
    "inspect-workspace": "references/workspace.md",
    "init-workspace": "references/workspace.md",
    "list-lenses": "references/extend-lenses.md",
    "inspect-environment": "references/bootstrap.md",
    "install-cognicode": "references/bootstrap.md",
    "scan-symbols": "references/scan.md",
    "build-graph": "references/scan.md",
    "query-cognicode": "references/scan.md",
    "formulate-question": "references/research-protocol.md",
    "discover-capabilities": "references/research-protocol.md",
    "preflight-language": "references/session-preflight.md",
    "inspect-session": "references/session-preflight.md",
    "plan-view": "references/lenses/c4.md",
    "split-view": "references/lenses/c4.md",
    "probe-capability": "references/research-protocol.md",
    "query-structured": "references/research-protocol.md",
    "justify-claims": "references/research-protocol.md",
    "assess-coverage": "references/research-protocol.md",
    "assess-omissions": "references/research-protocol.md",
    "interpret-input": "references/interpret.md",
    "review-model": "references/evidence.md",
    "reconcile": "references/interpret.md",
    "validate": "references/validate.md",
    "inspect-kroki": "references/kroki.md",
    "start-kroki": "references/kroki.md",
    "start-mermaid-companion": "references/kroki.md",
    "preview-mermaid": "references/kroki.md",
    "preview-structurizr": "references/kroki.md",
    "finish": "references/navigation.md",
    "inspect-projector": "references/projectors.md",
    "start-projector": "references/projectors.md",
    "open-projector": "references/projectors.md",
    "review-layout": "references/validate.md",
    "build-atlas": "references/projectors/markmap.md",
    "inspect-markmap": "references/projectors/markmap.md",
    "render-atlas": "references/projectors/markmap.md",
    "open-atlas": "references/projectors/markmap.md",
    "review-atlas": "references/projectors/markmap.md",
    "inspect-editorial-evidence": "references/editorial.md",
    "render-editorial": "references/editorial.md",
    "link-editorial-atlas": "references/editorial.md",
    "open-editorial": "references/editorial.md",
    "review-editorial": "references/editorial.md",
}


class InvalidState(ValueError):
    """State or catalog cannot safely be trusted."""


def read_catalog(path: Path = CATALOG) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema_version") != 1:
        raise InvalidState("catálogo: versión no soportada")
    items = raw.get("lenses")
    if not isinstance(items, list) or not items:
        raise InvalidState("catálogo: lenses debe ser una lista no vacía")
    result = {}
    for lens in items:
        if not isinstance(lens, dict) or not isinstance(lens.get("id"), str):
            raise InvalidState("catálogo: lente inválida")
        ident = lens["id"]
        if not SLUG.fullmatch(ident) or ident in result:
            raise InvalidState(f"catálogo: id duplicado/inválido {ident!r}")
        if lens.get("status") not in STATUSES or lens.get("evidence") not in {"architecture", "symbols", "requirements", "flow"}:
            raise InvalidState(f"catálogo: estado/evidencia inválido para {ident}")
        playbook = lens.get("playbook", "")
        if not isinstance(playbook, str) or not playbook.startswith("references/lenses/") or not (BASE / playbook).is_file():
            raise InvalidState(f"catálogo: falta playbook de {ident}")
        formats = lens.get("formats", {})
        if not isinstance(formats, dict) or not formats or any(not SLUG.fullmatch(fmt) for fmt in formats):
            raise InvalidState(f"catálogo: formatos inválidos {ident}")
        for fmt, desc in formats.items():
            if not isinstance(desc, dict) or desc.get("support") not in SUPPORT:
                raise InvalidState(f"catálogo: formato inválido {ident}/{fmt}")
            if lens["status"] == READY and desc.get("support") != "unsupported":
                ref = desc.get("playbook", "")
                if not isinstance(ref, str) or not ref.startswith("references/formats/") or not (BASE / ref).is_file():
                    raise InvalidState(f"catálogo: formato activo sin playbook {ident}/{fmt}")
        result[ident] = lens
    return result


def enum(state: dict, key: str, options: set[str]) -> str:
    value = state.get(key)
    if not isinstance(value, str) or value not in options:
        raise InvalidState(f"{key}: valor desconocido {value!r}")
    return value


def bool_field(state: dict, key: str, default: bool = False) -> bool:
    val = state.get(key, default)
    if not isinstance(val, bool):
        raise InvalidState(f"{key} debe ser booleano")
    return val


def editorial_affordances(state: dict, catalog: dict) -> dict:
    """Presentation-only HATEOAS route over a pre-existing CogniCode C4 view.

    Only observed input states; never reads the checkout or calls CogniCode.
    The --check projector command validates the actual derived ledger.
    """
    lens_id = state.get("lens", "c4")
    if lens_id != "c4" or catalog.get("c4", {}).get("status") != READY:
        return {"status": "UNSUPPORTED", "lens": lens_id, "recommended": None,
                "_links": [], "blockers": ["solo lente c4 disponible para presentación editorial"]}
    view = state.get("editorial", {})
    if not isinstance(view, dict):
        raise InvalidState("editorial debe ser un objeto")
    view_id = view.get("view")
    if not isinstance(view_id, str) or not SLUG.fullmatch(view_id):
        raise InvalidState("editorial.view debe ser el ID de un informe c4 existente")
    pattern = view.get("pattern", "auto")
    if pattern not in {"auto", "topology", "dependencies", "traceability"}:
        raise InvalidState("editorial.pattern inválido")
    question_kind = view.get("question_kind", "view_grouping")
    if not isinstance(question_kind, str) or question_kind not in {
        "view_grouping", "responsibilities", "understand_symbol", "collaborators",
        "interaction", "change_impact", "dependency_structure", "traceable_decomposition"
    }:
        raise InvalidState("editorial.question_kind desconocido")
    if pattern == "auto":
        pattern = ("dependencies" if question_kind in {"collaborators", "change_impact", "dependency_structure"}
                   else "traceability" if question_kind == "traceable_decomposition"
                   else "topology")
    profile = view.get("profile", "default")
    if not isinstance(profile, str) or not SLUG.fullmatch(profile):
        raise InvalidState("editorial.profile inválido")
    focus = view.get("focus")
    if focus is not None and (not isinstance(focus, str) or not focus.strip() or len(focus) > 400):
        raise InvalidState("editorial.focus debe ser un symbol_id existente")
    prepared = enum({"prepared": view.get("prepared", "unknown")}, "prepared",
                    {"unknown", "missing", "ready", "invalid"})
    # A ready status requires successful editorial.py --check, not a filename.
    rendered = enum({"render": view.get("render", "absent")}, "render",
                    {"absent", "stale", "ready", "invalid"})
    linked = bool_field(view, "linked")
    atlas = enum({"atlas_source": view.get("atlas_source", "absent")},
                 "atlas_source", {"absent", "stale", "ready"})
    review = enum({"visual_review": view.get("visual_review", "not_run")},
                  "visual_review", {"not_run", "passed", "failed"})
    basis = enum({"basis": state.get("basis", "unknown")}, "basis", BASIS)
    origin = enum({"evidence_origin": state.get("evidence_origin", "unknown")},
                  "evidence_origin", {"unknown", "cognicode", "other"})
    coverage = enum({"claim_coverage": state.get("claim_coverage", "unknown")},
                    "claim_coverage", {"unknown", "partial", "verified"})
    opts = {"view": view_id, "pattern": pattern, "profile": profile}
    if focus is not None:
        opts["focus"] = focus
    result = {"lens": lens_id, "presentation": opts, "certification": "presentation-only"}
    def offer(rel: str, why: str, *, status: str = "IN_PROGRESS", blockers=None) -> dict:
        link = {"rel": rel, "href": LINKS[rel], "requires_approval": False,
                "why": why, "inputs": opts}
        return {**result, "status": status, "recommended": rel,
                "_links": [link], "blockers": blockers or []}
    def stop(reason: str, status: str = "PARTIAL") -> dict:
        return {**result, "status": status, "recommended": None,
                "_links": [], "blockers": [reason]}
    if prepared == "ready" and origin != "cognicode":
        return stop("procedencia CogniCode no acreditada; proyección bloqueada", "BLOCKED")
    if prepared == "invalid":
        return stop("preflight editorial rechazó evidencia derivada; no suplir con lectura directa", "BLOCKED")
    if prepared == "missing":
        return stop("falta informe de vista C4: investigar SOLO con CogniCode antes de proyectar", "BLOCKED")
    if prepared == "unknown":
        return offer("inspect-editorial-evidence",
                     "ejecutar editorial.py --check sobre ledger/report externo; no investigar checkout")
    if rendered in {"absent", "stale", "invalid"}:
        return offer("render-editorial",
                     "renderizar representación derivada; no reconsultar código")
    if not linked:
        return offer("link-editorial-atlas", "enlazar los dos assets en informe externo de vista")
    if atlas in {"absent", "stale"}:
        return offer("build-atlas", "sincronizar atlas incremental con vistas ya generadas")
    if review == "failed":
        return offer("review-editorial", "corregir legibilidad o geometría, no modificar evidencia",
                     status="PARTIAL")
    if review != "passed":
        return offer("open-editorial", "inspeccionar realmente diagrama y enlaces en navegador")
    if coverage != "verified" or basis != "current":
        return offer("finish", "presentación disponible, pero vigencia/cobertura de código no certificada",
                     status="PARTIAL", blockers=["evidencia acotada o vigencia desconocida"])
    return offer("finish", "vista revisada; solo alcance declarado por CogniCode",
                 status="VERIFIED")


def affordances(state: dict, catalog: dict | None = None) -> dict:
    """Compute links from already-observed data, not invent observations."""
    if not isinstance(state, dict):
        raise InvalidState("state debe ser objeto")
    catalog = read_catalog() if catalog is None else catalog
    known_formats = {fmt for lens in catalog.values() for fmt in lens["formats"]}
    intent = enum(state, "intent", INTENTS)
    lens_id = state.get("lens")
    if intent == "catalog":
        return {
            "status": "READY", "lens": None, "recommended": "list-lenses",
            "_links": [{"rel": "list-lenses", "href": LINKS["list-lenses"], "requires_approval": False, "why": "enumerar lentes registradas y estados"}],
            "lenses": [{"id": x["id"], "status": x["status"], "formats": {k: v["support"] for k, v in x["formats"].items()}} for x in catalog.values()],
            "blockers": [],
        }
    # Artifact-producing requests always require an independently resolved HOME workspace.
    # This gate is before ANY CogniCode scan or projector operation: no Git contamination.
    if intent not in {"setup", "catalog"}:
        workspace = enum({"workspace": state.get("workspace", "unknown")}, "workspace", WORKSPACES)
        if workspace != "ready":
            blockers = []
            if workspace == "unknown":
                rel, why = "inspect-workspace", "resolver la ruta explícita sin ejecutar Git ni leer el repositorio"
            elif workspace in {"absent", "incomplete"}:
                rel, why = "init-workspace", "crear/completar directorios solo bajo ~/.cognicode-diagrams"
            else:
                rel, why = None, ""
                blockers.append("workspace inseguro/identidad no válida: no escribir ni modificar el repositorio")
            links = ([{"rel": rel, "href": LINKS[rel], "requires_approval": False, "why": why}]
                     if rel else [])
            return {"status": "IN_PROGRESS" if links else "BLOCKED", "lens": lens_id,
                    "recommended": rel, "_links": links, "blockers": blockers}

    # Editorial is only presentation of a previously researched C4 view.
    if intent == "editorial":
        return editorial_affordances(state, catalog)

    # Cross-lens navigation is deliberately independent of CogniCode readiness.
    # No model inference, no container auto-start, no implied visual verification.
    if intent == "atlas":
        source = enum({"atlas_source": state.get("atlas_source", "absent")},
                      "atlas_source", {"absent", "stale", "ready"})
        html = enum({"atlas_html": state.get("atlas_html", "absent")},
                    "atlas_html", {"absent", "stale", "rendered", "failed"})
        renderer = enum({"markmap": state.get("markmap", "unknown")},
                        "markmap", {"unknown", "missing", "ready"})
        review = enum({"visual_review": state.get("visual_review", "not_run")},
                      "visual_review", {"not_run", "passed", "failed"})
        assets = state.get("atlas_assets", "unknown")
        if assets not in {"unknown", "absent", "present"}:
            raise InvalidState("atlas_assets inválido")
        def atlas_link(rel: str, reason: str) -> dict:
            return {"rel": rel, "href": LINKS[rel], "requires_approval": False, "why": reason}
        if assets == "absent":
            return {"status": "BLOCKED", "lens": None, "recommended": None, "_links": [],
                    "blockers": ["no existen diagramas: generarlos mediante lente y agente antes del atlas"]}
        if source in {"absent", "stale"}:
            links = [atlas_link("build-atlas", "indexar fuentes/renders ya existentes en workspace externo")]
        elif html in {"absent", "stale", "failed"}:
            if renderer == "unknown":
                links = [atlas_link("inspect-markmap", "comprobar Markmap o imagen OCI local sin instalar")]
            elif renderer == "missing":
                return {"status": "PARTIAL", "lens": None, "recommended": None, "_links": [],
                        "blockers": ["atlas.md disponible; falta motor Markmap local, instalar solo con autorización"]}
            else:
                links = [atlas_link("render-atlas", "proyectar Markdown como HTML interactivo local")]
        elif review == "not_run":
            links = [atlas_link("open-atlas", "inspeccionar miniaturas y enlaces realmente en el navegador")]
        elif review == "failed":
            links = [atlas_link("review-atlas", "corregir el índice derivado o el render y revalidar")]
        else:
            links = [atlas_link("finish", "atlas visualmente revisado: no certifica arquitectura")]
        return {"status": "PARTIAL" if links[0]["rel"] == "review-atlas" else "VERIFIED" if links[0]["rel"] == "finish" else "IN_PROGRESS",
                "lens": None, "recommended": links[0]["rel"], "_links": links, "blockers": []}

    # Setup/scan are general CogniCode operations, independent of any diagram lens.
    generic = lens_id is None and intent in {"setup", "scan"}
    if generic:
        lens = {"id": None, "status": READY, "evidence": "symbols", "formats": {}}
    else:
        if not isinstance(lens_id, str):
            raise InvalidState("lens debe identificarse mediante string")
        if lens_id not in catalog:
            return {"status": "UNSUPPORTED", "lens": lens_id, "recommended": None, "_links": [], "blockers": ["lente no registrada; consultar references/extend-lenses.md"]}
        lens = catalog[lens_id]
        if lens["status"] != READY:
            return {"status": "UNSUPPORTED", "lens": lens_id, "recommended": None, "_links": [], "blockers": [f"lente {lens_id} es {lens['status']}; no hay implementación certificada en esta skill"]}

    env = enum(state, "environment", ENVS)
    evidence = enum(state, "evidence", EVIDENCE)
    basis = enum(state, "basis", BASIS)
    model = enum(state, "model", MODELS)
    has_input = bool_field(state, "has_input_diagram")
    reconciled = bool_field(state, "reconciled")
    scan_depth = enum({"scan_depth": state.get("scan_depth", "symbols")}, "scan_depth", {"symbols", "graph"})
    formats = state.get("formats", [])
    if not isinstance(formats, list) or any(not isinstance(x, str) for x in formats) or len(set(formats)) != len(formats) or set(formats) - known_formats:
        raise InvalidState("formats: conjunto inválido")
    if intent in {"create", "translate", "update", "validate"} and not formats:
        raise InvalidState(f"{intent} requiere al menos un formato")
    art = state.get("artifacts", {})
    validators = state.get("validators", {})
    approval = state.get("approval", {})
    if not isinstance(art, dict) or set(art.values()) - ARTIFACTS or not isinstance(validators, dict) or set(validators.values()) - VALIDATORS or not isinstance(approval, dict):
        raise InvalidState("artifacts, validators o approval inválidos")
    for key in ("install", "write_project"):
        if key in approval and not isinstance(approval[key], bool):
            raise InvalidState(f"approval.{key} debe ser booleano")
    unsupported = [fmt for fmt in formats if fmt not in lens["formats"] or lens["formats"][fmt]["support"] == "unsupported"]
    if unsupported:
        return {"status": "UNSUPPORTED", "lens": lens_id, "recommended": None, "_links": [], "blockers": [f"formato no compatible para {lens_id}: {', '.join(unsupported)}"]}

    # A browser projector is a viewer of already agent-authored text files.
    # No code scan, no source-model inference or implicit container start.
    # The existing Kroki route remains the default for image projections.
    if intent == "preview" and state.get("projector", "kroki-local") != "kroki-local":
        projector = enum(state, "projector", {"likec4-local", "structurizr-local"})
        expected = {"likec4-local": "likec4", "structurizr-local": "structurizr"}[projector]
        if formats != [expected]:
            return {"status": "UNSUPPORTED", "lens": lens_id, "recommended": None, "_links": [],
                    "blockers": [f"{projector} solo acepta el protocolo {expected}; el agente debe generarlo primero"]}
        observed = enum({"projector_status": state.get("projector_status", "unknown")},
                        "projector_status", {"unknown", "missing", "stopped", "running", "ready", "failed"})
        visual_review = enum({"visual_review": state.get("visual_review", "not_run")},
                             "visual_review", {"not_run", "passed", "failed"})
        if "start_projector" in approval and not isinstance(approval["start_projector"], bool):
            raise InvalidState("approval.start_projector debe ser booleano")
        blockers = []
        links = []
        def view_link(rel: str, why: str, approve: bool = False) -> None:
            links.append({"rel": rel, "href": LINKS[rel], "requires_approval": approve, "why": why})
        if art.get(expected, "absent") == "absent":
            return {"status": "BLOCKED", "lens": lens_id, "recommended": None, "_links": [],
                    "blockers": [f"no existe la fuente editable {expected} en el workspace externo"]}
        if observed in {"unknown", "running"}:
            view_link("inspect-projector", "comprobar estado y HTTP local del visor")
        elif observed in {"missing", "stopped"}:
            if approval.get("start_projector", False):
                view_link("start-projector", "arrancar contenedor solo mediante petición autorizada", True)
            else:
                blockers.append("visor ausente/parado; necesita autorización explícita para iniciar Podman/Docker")
        elif observed == "failed":
            blockers.append("visor fallido; revisar diagnóstico de runtime antes de reintentar")
        elif visual_review == "not_run":
            view_link("open-projector", "abrir vista local, inspeccionar legibilidad y registrar observación")
        elif visual_review == "failed":
            view_link("review-layout", "corregir fuente editable y revalidar antes de visualizar")
        else:
            view_link("finish", "vista inspeccionada; distinguir validez sintáctica y fidelidad semántica")
        status = ("VERIFIED" if links and links[0]["rel"] == "finish" and art.get(expected) == "valid"
                  else "PARTIAL" if visual_review == "failed" or (links and links[0]["rel"] == "finish")
                  else "IN_PROGRESS" if links else "BLOCKED")
        return {"status": status, "lens": lens_id,
                "recommended": links[0]["rel"] if links else None, "_links": links, "blockers": blockers}

    # Optional visualization is independent of CogniCode discovery and model review.
    # Only OBSERVED renderer/preview states are trusted; no auto-provisioning.
    if intent == "preview":
        if "likec4" in formats:
            return {"status": "UNSUPPORTED", "lens": lens_id, "recommended": None, "_links": [],
                    "blockers": ["Kroki no renderiza LikeC4; usar projector=likec4-local"]}
        kroki = enum({"kroki": state.get("kroki", "unknown")}, "kroki",
                     {"unknown", "missing", "gateway_ready", "full_ready"})
        previews = state.get("previews", {})
        if not isinstance(previews, dict) or set(previews) - known_formats or set(previews.values()) - {"absent", "rendered", "failed", "stale"}:
            raise InvalidState("previews inválidos")
        if "start_kroki" in approval and not isinstance(approval["start_kroki"], bool):
            raise InvalidState("approval.start_kroki debe ser booleano")
        # Partial renders are useful but must never masquerade as a completed render request.
        pending = [fmt for fmt in formats if previews.get(fmt, "absent") != "rendered"]
        links: list[dict] = []
        blockers: list[str] = []
        def add_preview_action(rel: str, why: str, approve: bool = False) -> None:
            links.append({"rel": rel, "href": LINKS[rel], "requires_approval": approve, "why": why})
        for fmt in pending:
            if art.get(fmt, "absent") == "absent":
                blockers.append(f"falta fuente de texto {fmt}; generar o proporcionar archivo antes de previsualizar")
        if pending and kroki == "unknown":
            add_preview_action("inspect-kroki", "comprobar render local real antes de usarlo")
        elif pending and kroki == "missing":
            if approval.get("start_kroki", False):
                add_preview_action("start-kroki", "instalar/arrancar contenedores solo con autorización", True)
            else:
                blockers.append("Kroki no disponible; arrancar contenedores requiere autorización")
        elif pending:
            for fmt in pending:
                if art.get(fmt, "absent") == "absent":
                    continue
                if fmt == "mermaid" and kroki != "full_ready":
                    if approval.get("start_kroki", False):
                        add_preview_action("start-mermaid-companion", "Mermaid necesita el contenedor complementario", True)
                    else:
                        blockers.append("Mermaid requiere el companion kroki-mermaid; arranque no autorizado")
                else:
                    add_preview_action("preview-" + fmt, "renderizar fuente mediante POST local y comprobar bytes SVG/PNG")
        if not pending:
            add_preview_action("finish", "previsualizaciones generadas; revisar visualmente y declarar alcance")
            status = "VERIFIED" if all(art.get(fmt) == "valid" for fmt in formats) else "PARTIAL"
        else:
            status = "IN_PROGRESS" if links else ("PARTIAL" if any(previews.get(fmt) == "rendered" for fmt in formats) else "BLOCKED")
        return {"status": status, "lens": lens_id,
                "recommended": links[0]["rel"] if links else None, "_links": links,
                "blockers": blockers}

    links: list[dict] = []
    blockers: list[str] = []

    def link(rel: str, why: str, href: str | None = None, requires_approval: bool = False) -> None:
        if not any(v["rel"] == rel for v in links):
            links.append({"rel": rel, "href": href or LINKS[rel], "requires_approval": requires_approval, "why": why})

    requires_code = intent in {"scan", "discover", "create", "review", "update"}
    detail_requested = bool_field(state, "detail_requested")
    evidence_insufficient = bool_field(state, "evidence_insufficient")
    evidence_origin = enum({"evidence_origin": state.get("evidence_origin", "unknown")},
                           "evidence_origin", {"unknown", "cognicode", "other"})
    claim_coverage = enum({"claim_coverage": state.get("claim_coverage", "unknown")},
                          "claim_coverage", {"unknown", "partial", "verified"})
    untrusted_evidence = (requires_code and evidence in {"symbols_ready", "graph_ready", "partial"}
                          and evidence_origin != "cognicode")
    usable = env in {"cli_ready", "mcp_ready", "both_ready"}
    # A graph-ready or verified flag cannot replace concrete proof of a question.
    architecture = intent in {"discover", "create", "review", "update"}
    if architecture and usable and not (detail_requested or evidence_insufficient or untrusted_evidence):
        try:
            verdict = decide_research(state.get("research"))
        except ResearchError as exc:
            raise InvalidState(f"research: {exc}") from exc
        if verdict["status"] != "EVIDENCE_READY":
            rel = verdict["action"]
            item = ([{"rel": rel, "href": LINKS[rel], "why": verdict["why"],
                      "requires_approval": False, "capability": verdict["capability"],
                      "question_id": verdict["question_id"]}] if rel else [])
            return {"status": verdict["status"], "lens": lens_id,
                    "recommended": rel, "_links": item,
                    "blockers": verdict["missing"] + ([] if rel else [verdict["why"]]),
                    "research": verdict}

    if (intent == "setup" or requires_code) and env == "unknown":
        link("inspect-environment", "no hay medición real de CLI/MCP")
    if (intent == "setup" or requires_code) and env == "missing":
        if approval.get("install") is True:
            link("install-cognicode", "instalación explícitamente autorizada")
        else:
            blockers.append("CogniCode ausente; instalación no autorizada")

    needs_input = intent in {"interpret", "translate", "validate"}
    if has_input and model == "absent" and intent in {"interpret", "translate", "review", "update", "validate"} and (not requires_code or usable):
        link("interpret-input", "existe diagrama; interpretar sin escaneo previo")
    if needs_input and not has_input and model == "absent" and all(art.get(fmt, "absent") == "absent" for fmt in formats):
        blockers.append("no existe diagrama de entrada")

    if untrusted_evidence:
        blockers.append("evidencia arquitectónica ajena a CogniCode: no se admite como prueba")
    if requires_code and not usable and env == "missing":
        blockers.append("CogniCode no disponible: investigación bloqueada; sin exploración sustitutiva")
    if requires_code and usable and (detail_requested or evidence_insufficient or untrusted_evidence):
        link("query-cognicode", "nueva consulta a CogniCode; prohibido leer el repositorio")
    if requires_code and usable and not (detail_requested or evidence_insufficient or untrusted_evidence) and (intent != "create" or model == "absent") and (intent not in {"review", "update"} or model != "absent"):
        if basis == "stale" or evidence in {"absent", "stale"}:
            link("scan-symbols", "escanear alcance vigente; evidencia ausente o caducada")
        elif evidence == "symbols_ready" and intent == "scan" and scan_depth == "graph":
            link("build-graph", "se requiere inspección de relaciones")
        elif intent == "scan":
            link("finish", "escaneo suficiente para el objetivo solicitado")
        elif model == "absent" and evidence in {"graph_ready", "partial", "symbols_ready"}:
            link("discover-model", "interpretar el grafo/código según la lente", href=lens["playbook"])
        elif intent in {"review", "update"} and model != "absent" and evidence == "graph_ready" and basis == "current" and not reconciled:
            link("reconcile", "contrastar diagrama existente con el código actual")

    if model == "draft" and not (detail_requested or evidence_insufficient or untrusted_evidence) and intent in {"discover", "create", "interpret", "translate", "review", "update"}:
        link("review-model", "revisar consistencia y límites de evidencia")

    can_render = intent in {"translate", "create", "update"} and model != "absent"
    if intent == "update" and (not reconciled or basis != "current"):
        can_render = False
    if intent == "create" and basis != "current":
        can_render = False
    if requires_code and (detail_requested or evidence_insufficient or untrusted_evidence or not usable):
        can_render = False
    if can_render:
        for fmt in formats:
            if art.get(fmt, "absent") in {"absent", "invalid"}:
                fmt_cfg = lens["formats"][fmt]
                link("render-" + fmt, "generar representación compatible" + (" con pérdidas declaradas" if fmt_cfg["support"] == "adapted" else ""), href=fmt_cfg["playbook"])

    if any(art.get(fmt, "absent") == "draft" for fmt in formats) and intent in {"create", "translate", "update", "validate"}:
        if all(validators.get(fmt) == "available" for fmt in formats if art.get(fmt, "absent") == "draft"):
            link("validate", "hay artefactos cuya sintaxis aún no está comprobada")
        else:
            blockers.append("faltan validadores locales: no declarar los diagramas como VALID")

    achieved = (intent == "setup" and usable) or (intent == "scan" and usable and evidence in {"symbols_ready", "graph_ready", "partial"} and basis == "current") or (intent in {"discover", "interpret"} and model != "absent") or (intent == "review" and reconciled) or (intent in {"create", "translate", "update", "validate"} and formats and all(art.get(fmt) in {"draft", "valid"} for fmt in formats))
    if requires_code and (detail_requested or evidence_insufficient or untrusted_evidence or not usable):
        achieved = False
    if achieved:
        link("finish", "el objetivo solicitado está disponible; declarar límites y validaciones")

    order = ["list-lenses", "interpret-input", "inspect-environment", "install-cognicode", "formulate-question", "discover-capabilities", "probe-capability", "query-structured", "justify-claims", "assess-coverage", "assess-omissions", "query-cognicode", "scan-symbols", "build-graph", "discover-model", "reconcile", "review-model", "render-mermaid", "render-structurizr", "validate", "finish"]
    # Los renderizadores de nuevas lentes/formatos se insertan sin modificar esta lista.
    links.sort(key=lambda l: (order.index(l["rel"]) if l["rel"] in order else order.index("validate") - 0.5))
    recommended = links[0]["rel"] if links else None
    if requires_code and env == "missing":
        links = [item for item in links if item["rel"] == "install-cognicode"]
    if not links:
        status = "BLOCKED" if blockers else "PARTIAL"
    elif any(l["rel"] != "finish" for l in links):
        status = "IN_PROGRESS"
    else:
        syntax_ok = all(art.get(fmt) == "valid" for fmt in formats)
        reviewed = (intent in {"setup", "scan"}) or model == "reviewed"
        evidence_ok = (intent in {"translate", "interpret", "setup", "scan"}) or (basis == "current" and evidence == "graph_ready")
        complete_evidence = evidence != "partial" if intent in {"scan", "discover", "create", "review", "update"} else True
        implementation_grounded = (not requires_code or
                                   (evidence_origin == "cognicode" and claim_coverage == "verified"))
        coverage_certified = (not architecture or
                              state.get("research", {}).get("scope", {}).get("coverage") == "complete")
        status = "VERIFIED" if (syntax_ok or intent in {"setup", "scan", "discover", "interpret", "review"}) and reviewed and evidence_ok and complete_evidence and implementation_grounded and coverage_certified and not blockers else "PARTIAL"

    return {"status": status, "lens": lens_id, "recommended": recommended, "_links": links, "blockers": blockers}


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: affordances.py <session.json | ->", file=sys.stderr)
        return 2
    try:
        content = sys.stdin.read() if sys.argv[1] == "-" else Path(sys.argv[1]).read_text(encoding="utf-8")
        result = affordances(json.loads(content))
    except (ValueError, OSError, json.JSONDecodeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
