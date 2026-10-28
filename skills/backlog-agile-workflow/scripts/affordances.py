#!/usr/bin/env python3
"""Pure, bounded Backlog.md workflow navigator. Never executes Backlog.md or edits a repo."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INTENTS = frozenset({"discover", "capture", "triage", "refine", "plan", "execute",
                     "verify", "close", "review", "maintain", "specify", "decompose", "sync-specs", "git-hygiene", "trace", "architecture", "curate-architecture", "map-task", "catalog"})
BASIS = frozenset({"observed", "unknown", "stale"})
CLI = frozenset({"available", "missing", "unknown"})
PROJECT = frozenset({"initialized", "absent", "unknown"})
MODES = frozenset({"read", "propose", "apply"})
GROMA = frozenset({"available", "missing", "unknown"})
GROMA_INTENTS = frozenset({"architecture", "curate-architecture", "map-task"})
CONFIG = ("autoCommit", "remoteOperations", "bypassGitHooks", "onStatusChange")
TASK_ID = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,63}")
NEEDS_TASK = frozenset({"plan", "execute", "verify", "close", "map-task"})
WRITE_INTENTS = frozenset({"capture", "refine", "plan", "execute", "verify", "close", "review", "maintain", "map-task"})


def _registry(file: str, key: str) -> list[dict[str, Any]]:
    data = json.loads((ROOT / "references" / file).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get(key), list):
        raise ValueError(f"Invalid registry: {file}")
    entries = data[key]
    if any(not isinstance(x, dict) or not isinstance(x.get("id"), str) for x in entries):
        raise ValueError(f"Malformed registry: {file}")
    if len({x["id"] for x in entries}) != len(entries):
        raise ValueError(f"Duplicate registry ids: {file}")
    return entries


def _local(href: str) -> str:
    path = (ROOT / href).resolve()
    if not path.is_relative_to(ROOT.resolve()) or not path.is_file():
        raise ValueError(f"Unsafe or missing playbook: {href}")
    return href


def _strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value):
        raise ValueError(f"{label} must be a string list")
    if len(value) != len(set(value)):
        raise ValueError(f"Duplicate {label}")
    return value


def _task(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("task must be object")
    allowed = {"id", "isReady", "archived", "status", "acceptanceCriteriaCount",
               "acceptanceCriteriaCompleted", "definitionOfDoneCount", "definitionOfDoneCompleted"}
    if set(value) - allowed:
        raise ValueError("Unknown task fields")
    tid = value.get("id")
    if tid is not None and (not isinstance(tid, str) or not TASK_ID.fullmatch(tid)):
        raise ValueError("Invalid task ID")
    if "status" in value and (not isinstance(value["status"], str) or not value["status"].strip()):
        raise ValueError("Invalid task status")
    for key in ("isReady", "archived"):
        if key in value and type(value[key]) is not bool:
            raise ValueError(f"Invalid {key}")
    for key in ("acceptanceCriteriaCount", "acceptanceCriteriaCompleted",
                "definitionOfDoneCount", "definitionOfDoneCompleted"):
        if key in value and (type(value[key]) is not int or value[key] < 0):
            raise ValueError(f"Invalid {key}")
    for prefix in ("acceptanceCriteria", "definitionOfDone"):
        count = value.get(prefix + "Count")
        completed = value.get(prefix + "Completed")
        if count is not None and completed is not None and completed > count:
            raise ValueError("Completed exceeds count")
    return value


def _config(value: Any) -> dict[str, bool | None]:
    if value is None:
        return {k: None for k in CONFIG}
    if not isinstance(value, dict) or set(value) - set(CONFIG):
        raise ValueError("Unknown configuration fields")
    if any(x is not None and type(x) is not bool for x in value.values()):
        raise ValueError("Configuration values must be boolean or null")
    return {k: value.get(k) for k in CONFIG}


def _notice(rel: str, why: str, **extra: Any) -> dict[str, Any]:
    return {"rel": rel, "why": why, **extra}


def affordances(state: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(state, dict):
        raise ValueError("Session must be object")
    allowed = {"intent", "basis", "cli", "project", "mode", "task", "config",
               "available_skills", "effects_acknowledged", "groma"}
    if set(state) - allowed:
        raise ValueError("Unknown session fields")
    intent, basis = state.get("intent", "catalog"), state.get("basis", "unknown")
    cli, project = state.get("cli", "unknown"), state.get("project", "unknown")
    mode = state.get("mode", "read")
    acknowledged = state.get("effects_acknowledged", False)
    groma = state.get("groma", "unknown")
    if (intent not in INTENTS or basis not in BASIS or cli not in CLI
            or project not in PROJECT or mode not in MODES or groma not in GROMA
            or type(acknowledged) is not bool):
        raise ValueError("Invalid session intent/basis/cli/project/mode/acknowledgement")
    task, config = _task(state.get("task")), _config(state.get("config"))
    available = _strings(state.get("available_skills", []), "available_skills")
    lenses = _registry("lens-registry.json", "lenses")
    skills = _registry("skill-registry.json", "related_skills")
    result: dict[str, Any] = {"intent": intent, "status": "NAVIGATION_ONLY", "decision": None,
                               "lenses": [], "_links": [], "suggested_reads": [], "warnings": []}
    if intent == "catalog":
        result["available"] = [{"id": x["id"], "status": x["status"]} for x in lenses]
        return result
    if basis == "stale":
        result["decision"] = "INSPECT_MORE"
        result["_links"].append(_notice("refresh-basis", "Reexaminar un proyecto que pudo cambiar"))
        return result
    if intent in GROMA_INTENTS and groma != "available":
        result["decision"] = "DISCOVER"
        result["_links"].append(_notice("inspect-groma", "Comprobar groma --version, groma plugin list y mapa local; no instalar ni escanear de oficio"))
        if groma == "missing":
            result["warnings"].append("Groma opcional y ausente; Backlog.md puede seguir funcionando sin mapa")
        return result
    offline_spec = intent in {"specify", "decompose", "git-hygiene", "trace", "architecture", "curate-architecture"}
    if cli != "available" and not offline_spec:
        result["decision"] = "DISCOVER"
        result["_links"].append(_notice("inspect-cli", "Verificar backlog --version y backlog --help, sin instalar automáticamente"))
        if cli == "missing":
            result["warnings"].append("backlog no instalado; npx backlog.md es distinto de npx backlog")
        return result
    if project != "initialized" and not offline_spec:
        result["decision"] = "DISCOVER"
        result["_links"].append(_notice("inspect-project", "Comprobar raíz y config; inicializar solo con permiso explícito"))
        return result
    if basis != "observed":
        result["decision"] = "INSPECT_MORE"
        result["_links"].append(_notice("inspect-backlog", "Leer estado real de CLI, tareas y configuración"))
        return result

    # Progressively load only 1-2 relevant guidance documents.
    selected = [x for x in lenses if x["status"] == "ready" and intent in x["intents"]][:2]
    for lens in selected:
        result["lenses"].append(lens["id"])
        result["_links"].append(_notice("read-lens", f"Guía {lens['id']}", href=_local(lens["playbook"])))
    result["suggested_reads"] = ([["backlog", "instructions", "overview"]]
                                  if cli == "available" and project == "initialized"
                                  and intent not in {"architecture", "curate-architecture"} else [])
    if intent in GROMA_INTENTS:
        result["suggested_reads"].extend([["groma", "plugin", "list"], ["groma", "agent-instructions"]])
        if intent == "map-task":
            result["suggested_reads"].append(["groma", "agent-instructions", "backlog"])
        else:
            result["suggested_reads"].append(["groma", "view", "--plain"])
    elif groma == "available" and intent in {"refine", "plan", "execute", "verify", "review", "decompose"}:
        result["_links"].append(_notice("inspect-architecture", "Groma es opcional: inspeccionar dueño de archivos por groma view <file> y referencias Backlog verificadas", href=_local("references/groma-integration.md")))
    if intent in {"specify", "decompose"}:
        result["_links"].append(_notice("inspect-specifications", "Inspeccionar ROADMAP, ADR, SPEC, gates y estado de la fuente canónica"))
    if intent == "git-hygiene":
        result["_links"].append(_notice("audit-git-index", "Comprobar índice con git_artifact_guard.py (solo lectura)"))
    if intent == "trace":
        result["_links"].append(_notice("inspect-commit-trailers", "Buscar IDs de tarea, bloque y ADR/SPEC en commits observados"))
    if intent in {"capture", "triage", "review", "maintain", "sync-specs"}:
        result["suggested_reads"].append(["backlog", "task", "list", "--json"])
    elif intent in NEEDS_TASK or intent == "refine":
        if task.get("id"):
            result["suggested_reads"].append(["backlog", "task", "view", task["id"], "--json"])
        elif intent in NEEDS_TASK:
            result["decision"] = "INSPECT_MORE"
            result["_links"].append(_notice("select-task", "Elegir el ID observado de una tarea"))
            return result

    if intent in NEEDS_TASK and task.get("archived") is True:
        result["decision"] = "BLOCKED"
        result["_links"].append(_notice("inspect-archived", "La tarea archivada es de solo lectura; restaurar requiere autorización"))
        return result
    if intent in {"execute", "plan"} and task.get("isReady") is not True:
        result["decision"] = "INSPECT_MORE"
        result["_links"].append(_notice("inspect-dependencies", "No se ha confirmado isReady=true para esta tarea"))
        return result
    if intent == "close":
        for prefix in ("acceptanceCriteria", "definitionOfDone"):
            count, done = task.get(prefix + "Count"), task.get(prefix + "Completed")
            if count is None or done is None:
                result["decision"] = "INSPECT_MORE"
                result["_links"].append(_notice("verify-checklist", f"Comprobar {prefix} en task view --json"))
                return result
            if done != count:
                result["decision"] = "BLOCKED"
                result["_links"].append(_notice("complete-checklist", f"Hay {count-done} pendientes en {prefix}; no cerrar"))
                return result

    if intent == "triage" and task and task.get("isReady") is not True:
        result["decision"] = "INSPECT_MORE"
        result["_links"].append(_notice("inspect-dependencies", "El candidato no está confirmado como listo"))
        return result

    if intent in {"specify", "decompose", "sync-specs"}:
        result["_links"].append(_notice("plan-spec-projection", "Derivar propuestas trazables; nunca escribir tareas sin reconciliar corpus"))
    if intent == "map-task":
        result["_links"].append(_notice("plan-groma-task-links", "Leer task view actual y proponer --modified-file completo y --add-ref/--remove-ref; no ejecuta CLI"))
    if intent == "curate-architecture":
        result["_links"].append(_notice("inspect-groma-writes", "Curación y scan escriben OKF; usar CLI Groma solo con aprobación específica"))
    if mode == "read":
        result["decision"] = "READY"
        result["_links"].append(_notice("inspect-current", "Leer backlog sin modificarlo"))
    elif mode == "propose":
        result["decision"] = "PROPOSE_ONLY"
        result["_links"].append(_notice("draft-change", "Proponer cambio, sin ejecutar CLI"))
    elif intent not in WRITE_INTENTS:
        result["decision"] = "KEEP_AS_IS"
    else:
        unknown = [x for x, v in config.items() if v is None]
        effects = [x for x, v in config.items() if v is True and x in
                   {"autoCommit", "remoteOperations", "bypassGitHooks", "onStatusChange"}]
        if unknown:
            result["decision"] = "INSPECT_MORE"
            result["_links"].append(_notice("inspect-configuration", "Configuración con efectos no observada: " + ", ".join(unknown)))
        elif effects and not acknowledged:
            result["decision"] = "BLOCKED"
            result["_links"].append(_notice("acknowledge-effects", "Revisar efectos de: " + ", ".join(effects)))
        else:
            result["decision"] = "AUTHORIZED_ACTION"
            result["_links"].append(_notice("propose-cli-write", "Hay permiso declarado para esta operación, pero el router no ejecuta CLI"))
        if effects:
            result["warnings"].append("Efectos de configuración observados: " + ", ".join(effects))
    for skill in skills:
        if skill["id"] in available and intent in skill["intents"]:
            result["_links"].append(_notice("delegate-skill", skill["reason"], skill_id=skill["id"]))
    return result


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Uso: affordances.py <session.json>")
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(affordances(data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
