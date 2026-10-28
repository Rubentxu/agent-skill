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
                     "verify", "close", "review", "maintain", "catalog"})
BASIS = frozenset({"observed", "unknown", "stale"})
CLI = frozenset({"available", "missing", "unknown"})
PROJECT = frozenset({"initialized", "absent", "unknown"})
MODES = frozenset({"read", "propose", "apply"})
CONFIG = ("autoCommit", "remoteOperations", "bypassGitHooks", "onStatusChange")
TASK_ID = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,63}")
NEEDS_TASK = frozenset({"plan", "execute", "verify", "close"})
WRITE_INTENTS = frozenset({"capture", "refine", "plan", "execute", "verify", "close", "review", "maintain"})


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
               "available_skills", "effects_acknowledged"}
    if set(state) - allowed:
        raise ValueError("Unknown session fields")
    intent, basis = state.get("intent", "catalog"), state.get("basis", "unknown")
    cli, project = state.get("cli", "unknown"), state.get("project", "unknown")
    mode = state.get("mode", "read")
    acknowledged = state.get("effects_acknowledged", False)
    if (intent not in INTENTS or basis not in BASIS or cli not in CLI
            or project not in PROJECT or mode not in MODES or type(acknowledged) is not bool):
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
    if cli != "available":
        result["decision"] = "DISCOVER"
        result["_links"].append(_notice("inspect-cli", "Verificar backlog --version y backlog --help, sin instalar automáticamente"))
        if cli == "missing":
            result["warnings"].append("backlog no instalado; npx backlog.md es distinto de npx backlog")
        return result
    if project != "initialized":
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
    result["suggested_reads"] = [["backlog", "instructions", "overview"]]
    if intent in {"capture", "triage", "review", "maintain"}:
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
