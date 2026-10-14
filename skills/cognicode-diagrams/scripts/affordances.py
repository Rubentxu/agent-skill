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

BASE = Path(__file__).resolve().parents[1]
CATALOG = BASE / "references" / "lens-registry.json"
INTENTS = {"catalog", "setup", "scan", "discover", "create", "interpret", "translate", "review", "update", "validate"}
ENVS = {"unknown", "missing", "cli_ready", "mcp_ready", "both_ready"}
EVIDENCE = {"absent", "symbols_ready", "graph_ready", "partial", "stale"}
BASIS = {"unknown", "current", "stale"}
MODELS = {"absent", "draft", "reviewed"}
ARTIFACTS = {"absent", "draft", "valid", "invalid"}
VALIDATORS = {"missing", "available"}
SUPPORT = {"native", "adapted", "unsupported"}
READY = "ready"
STATUSES = {"ready", "planned"}
FORMATS = {"mermaid", "structurizr"}
SLUG = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z")

LINKS = {
    "list-lenses": "references/extend-lenses.md",
    "inspect-environment": "references/bootstrap.md",
    "install-cognicode": "references/bootstrap.md",
    "scan-symbols": "references/scan.md",
    "build-graph": "references/scan.md",
    "interpret-input": "references/interpret.md",
    "review-model": "references/evidence.md",
    "reconcile": "references/interpret.md",
    "validate": "references/validate.md",
    "finish": "references/navigation.md",
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
        if not isinstance(formats, dict) or not formats or set(formats) - FORMATS:
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


def affordances(state: dict, catalog: dict | None = None) -> dict:
    """Compute links from already-observed data, not invent observations."""
    if not isinstance(state, dict):
        raise InvalidState("state debe ser objeto")
    catalog = read_catalog() if catalog is None else catalog
    intent = enum(state, "intent", INTENTS)
    lens_id = state.get("lens")
    if intent == "catalog":
        return {
            "status": "READY", "lens": None, "recommended": "list-lenses",
            "_links": [{"rel": "list-lenses", "href": LINKS["list-lenses"], "requires_approval": False, "why": "enumerar lentes registradas y estados"}],
            "lenses": [{"id": x["id"], "status": x["status"], "formats": {k: v["support"] for k, v in x["formats"].items()}} for x in catalog.values()],
            "blockers": [],
        }
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
    if not isinstance(formats, list) or any(not isinstance(x, str) for x in formats) or len(set(formats)) != len(formats) or set(formats) - FORMATS:
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

    links: list[dict] = []
    blockers: list[str] = []

    def link(rel: str, why: str, href: str | None = None, requires_approval: bool = False) -> None:
        if not any(v["rel"] == rel for v in links):
            links.append({"rel": rel, "href": href or LINKS[rel], "requires_approval": requires_approval, "why": why})

    requires_code = intent in {"scan", "discover", "create", "review", "update"}
    usable = env in {"cli_ready", "mcp_ready", "both_ready"}
    if (intent == "setup" or requires_code) and env == "unknown":
        link("inspect-environment", "no hay medición real de CLI/MCP")
    if (intent == "setup" or requires_code) and env == "missing":
        if approval.get("install") is True:
            link("install-cognicode", "instalación explícitamente autorizada")
        else:
            blockers.append("CogniCode ausente; instalación no autorizada")

    needs_input = intent in {"interpret", "translate", "validate"}
    if has_input and model == "absent" and intent in {"interpret", "translate", "review", "update", "validate"}:
        link("interpret-input", "existe diagrama; interpretar sin escaneo previo")
    if needs_input and not has_input and model == "absent" and all(art.get(fmt, "absent") == "absent" for fmt in formats):
        blockers.append("no existe diagrama de entrada")

    if requires_code and usable and (intent != "create" or model == "absent") and (intent not in {"review", "update"} or model != "absent"):
        if basis == "stale" or evidence in {"absent", "stale"}:
            link("scan-symbols", "escanear alcance vigente; evidencia ausente o caducada")
        elif evidence == "symbols_ready" and (lens["evidence"] in {"architecture", "flow"} or (intent == "scan" and scan_depth == "graph")):
            link("build-graph", "se requiere inspección de relaciones")
        elif intent == "scan":
            link("finish", "escaneo suficiente para el objetivo solicitado")
        elif model == "absent" and evidence in {"graph_ready", "partial", "symbols_ready"}:
            link("discover-model", "interpretar el grafo/código según la lente", href=lens["playbook"])
        elif intent in {"review", "update"} and model != "absent" and evidence == "graph_ready" and basis == "current" and not reconciled:
            link("reconcile", "contrastar diagrama existente con el código actual")

    if model == "draft" and intent in {"discover", "create", "interpret", "translate", "review", "update"}:
        link("review-model", "revisar consistencia y límites de evidencia")

    can_render = intent in {"translate", "create", "update"} and model != "absent"
    if intent == "update" and (not reconciled or basis != "current"):
        can_render = False
    if intent == "create" and basis == "stale":
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
    if achieved:
        link("finish", "el objetivo solicitado está disponible; declarar límites y validaciones")

    order = ["list-lenses", "interpret-input", "inspect-environment", "install-cognicode", "scan-symbols", "build-graph", "discover-model", "reconcile", "review-model", "render-mermaid", "render-structurizr", "validate", "finish"]
    links.sort(key=lambda l: order.index(l["rel"]))
    recommended = links[0]["rel"] if links else None
    if not links:
        status = "BLOCKED" if blockers else "PARTIAL"
    elif any(l["rel"] != "finish" for l in links):
        status = "IN_PROGRESS"
    else:
        syntax_ok = all(art.get(fmt) == "valid" for fmt in formats)
        reviewed = (intent in {"setup", "scan"}) or model == "reviewed"
        evidence_ok = (intent in {"translate", "interpret", "setup", "scan"}) or (basis == "current" and evidence == "graph_ready")
        complete_evidence = evidence != "partial" if intent in {"scan", "discover", "create", "review", "update"} else True
        status = "VERIFIED" if (syntax_ok or intent in {"setup", "scan", "discover", "interpret", "review"}) and reviewed and evidence_ok and complete_evidence and not blockers else "PARTIAL"

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
