#!/usr/bin/env python3
"""Router puro, por problemas observados y contexto, sin ejecutar ni modificar repositorios.

Los campos observados SON afirmaciones del llamante, no evidencia certificada.
Los enlaces href son rutas locales existentes, nunca endpoints ni comandos.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REFS = ROOT / "references"
INTENTS = frozenset({"catalog", "discovery", "design", "implementation", "refactor", "review"})
LANGUAGES = frozenset({"rust", "kotlin", "other", "unknown"})
BASIS = frozenset({"observed", "unknown", "stale"})
RISKS = frozenset({"routine", "high", "critical"})
PHASES = frozenset({"diagnose", "plan", "verify"})
SIGNALS = frozenset({
    "domain-ambiguity", "invalid-state", "side-effects", "large-service",
    "duplicate-logic", "complex-algorithm", "nested-data", "cross-context",
    "legacy-test-coupling", "unknown",
})
EFFORT = {"small": 0, "medium": 1, "large": 2}
RISK_COST = {"routine": 0, "high": 1, "critical": 2}
REVERSIBILITY = {"easy": 0, "medium": 1, "hard": 2}


def _catalog(filename: str, key: str) -> list[dict[str, Any]]:
    data = json.loads((REFS / filename).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get(key), list):
        raise ValueError(f"Invalid catalogue: {filename}")
    entries = data[key]
    if any(not isinstance(e, dict) or not isinstance(e.get("id"), str) for e in entries):
        raise ValueError(f"Malformed entries: {filename}")
    if len({e["id"] for e in entries}) != len(entries):
        raise ValueError(f"Duplicate identifiers: {filename}")
    return entries


def _read_catalog() -> list[dict[str, Any]]:
    return _catalog("lens-registry.json", "lenses")


def _local_path(filename: str) -> str:
    p = (ROOT / filename).resolve()
    if not p.is_relative_to(ROOT.resolve()) or not p.is_file():
        raise ValueError(f"Ruta local ausente o insegura: {filename}")
    return filename


def _strings(value: Any, name: str, permitted: set[str] | frozenset[str] | None = None) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value):
        raise ValueError(f"{name} debe ser lista de cadenas")
    if len(value) != len(set(value)):
        raise ValueError(f"{name} contiene duplicados")
    if permitted is not None and not set(value).issubset(permitted):
        raise ValueError(f"{name} contiene valores desconocidos")
    return value


def _evidence(items: Any) -> list[dict[str, str]]:
    if not isinstance(items, list):
        raise ValueError("evidence debe ser lista")
    for item in items:
        if not isinstance(item, dict) or not all(
            isinstance(item.get(k), str) and item[k].strip() for k in ("source", "observation")
        ):
            raise ValueError("La evidencia requiere source y observation no vacíos")
    return [{"source": x["source"], "observation": x["observation"]} for x in items]


def _diagnose(state: dict[str, Any], problems: list[dict[str, Any]], signals: set[str]) -> list[dict[str, Any]]:
    by_id = {x["id"]: x for x in problems}
    explicit = state.get("problems", [])
    if not isinstance(explicit, list):
        raise ValueError("problems debe ser lista")
    if explicit:
        ids = [x.get("id") if isinstance(x, dict) else None for x in explicit]
        if any(x not in by_id for x in ids) or len(ids) != len(set(ids)):
            raise ValueError("Problemas desconocidos o duplicados")
        return [{"id": x["id"], "status": "OBSERVED" if evidence else "INFERRED",
                 "evidence": evidence, "question": by_id[x["id"]]["question"],
                 "matched_signals": sorted(signals.intersection(by_id[x["id"]]["signals"]))}
                for x in explicit for evidence in [_evidence(x.get("evidence", []))]]
    candidates = [(p, signals.intersection(p["signals"])) for p in problems]
    candidates = [(p, matching) for p, matching in candidates if matching - {"unknown"}]
    candidates.sort(key=lambda pair: (-len(pair[1]), pair[0]["id"]))
    return [{"id": p["id"], "status": "INFERRED", "evidence": [],
             "question": p["question"], "matched_signals": sorted(matching)}
            for p, matching in candidates[:4]]


def _choices(diagnoses: list[dict[str, Any]], recipes: list[dict[str, Any]],
             facts: set[str], blockers: set[str], language: str) -> list[dict[str, Any]]:
    evidence = {x["id"]: x for x in diagnoses}
    candidates = []
    for recipe in recipes:
        if recipe["status"] != "ready" or language not in recipe["languages"]:
            continue
        matched = sorted(set(recipe["problems"]).intersection(evidence))
        if not matched:
            continue
        confirmed = any(evidence[id]["status"] == "OBSERVED" for id in matched)
        missing = sorted(set(recipe["requires"]) - facts)
        conflicts = sorted(set(recipe["blocks"]).intersection(blockers))
        if "already-cohesive-boundary" in blockers or "no-refactor-authorized" in blockers:
            decision, why = "KEEP_AS_IS", "La mejora no justifica un cambio o no está autorizado"
        elif conflicts:
            decision, why = "BLOCKED", "Contraindicaciones observadas: " + ", ".join(conflicts)
        elif not confirmed:
            decision, why = "INSPECT_MORE", "El problema es hipótesis, no diagnóstico acreditado"
        elif missing:
            decision, why = "INSPECT_MORE", "Faltan precondiciones observadas: " + ", ".join(missing)
        else:
            decision, why = "APPLY", "Receta aplicable como propuesta reversible, pendiente de ejecución y verificación"
        candidates.append({"id": recipe["id"], "decision": decision, "why": why,
                           "problems": matched, "missing": missing, "contraindications": conflicts,
                           "effort": recipe["effort"], "risk": recipe["risk"],
                           "reversibility": recipe["reversibility"],
                           "playbook": recipe["playbook"]})
    # Orden lexicográfico explicable: aplicabilidad > prerequisitos > esfuerzo > riesgo > reversibilidad.
    rank = {"APPLY": 0, "KEEP_AS_IS": 1, "INSPECT_MORE": 2, "BLOCKED": 3}
    candidates.sort(key=lambda x: (rank[x["decision"]], len(x["missing"]),
                                   EFFORT[x["effort"]], RISK_COST[x["risk"]],
                                   REVERSIBILITY[x["reversibility"]], x["id"]))
    return candidates


def _select_lenses(diagnoses: list[dict[str, Any]], lenses: list[dict[str, Any]],
                   signals: set[str], intent: str, language: str, phase: str) -> list[dict[str, Any]]:
    problem_ids = {x["id"] for x in diagnoses}
    inferred = any(x["status"] == "INFERRED" for x in diagnoses)
    methods = []
    for lens in lenses:
        if lens["kind"] != "method" or lens["status"] != "ready" or intent not in lens["intents"]:
            continue
        matches = set(lens.get("problems", [])).intersection(problem_ids)
        signs = set(lens["signals"]).intersection(signals)
        if not matches and not signs:
            continue
        # Specificity first; a diagnostic lens is always included while inference remains.
        if lens["id"] == "problem-diagnosis":
            significance = 100 if inferred else 10
        else:
            significance = len(matches) * 10 + len(signs)
        methods.append((significance, lens))
    methods.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    max_methods = 2 if phase == "diagnose" else (1 if phase == "verify" else 3)
    chosen = [x for _, x in methods[:max_methods]]
    if inferred and not any(x["id"] == "problem-diagnosis" for x in chosen):
        diagnosis = next((x for x in lenses if x["id"] == "problem-diagnosis"), None)
        if diagnosis is not None and intent in diagnosis["intents"]:
            chosen = [diagnosis] + chosen[:max_methods-1]
    adapter = next((x for x in lenses if x["kind"] == "language" and
                    x["status"] == "ready" and x.get("language") == language and
                    intent in x["intents"]), None)
    if adapter and phase != "diagnose":
        chosen.append(adapter)
    return chosen


def affordances(state: dict[str, Any]) -> dict[str, Any]:
    """Recomienda sin IO operativo. No certifica inspecciones ni PASS."""
    if not isinstance(state, dict):
        raise ValueError("session debe ser objeto")
    intent = state.get("intent", "catalog")
    language = state.get("language", "unknown")
    basis = state.get("basis", "unknown")
    risk = state.get("risk", "routine")
    phase = state.get("phase", "diagnose")
    if (intent not in INTENTS or language not in LANGUAGES or basis not in BASIS
            or risk not in RISKS or phase not in PHASES):
        raise ValueError("intent/language/basis/risk/phase no válido")
    signals = set(_strings(state.get("signals", []), "signals", SIGNALS))
    available = _strings(state.get("available_skills", []), "available_skills")
    facts = set(_strings(state.get("facts", []), "facts"))
    blockers = set(_strings(state.get("constraints", []), "constraints"))
    lenses = _read_catalog()
    problems = _catalog("problems.json", "problems")
    recipes = _catalog("recipe-registry.json", "recipes")
    legal_facts = set().union(*(set(x["requires"]) for x in recipes))
    legal_constraints = set().union(*(set(x["blocks"]) for x in recipes)) | {
        "already-cohesive-boundary", "no-refactor-authorized"}
    if not facts.issubset(legal_facts) or not blockers.issubset(legal_constraints):
        raise ValueError("facts/constraints incluyen términos no admitidos")
    result: dict[str, Any] = {"intent": intent, "phase": phase, "basis": basis,
        "risk": risk, "status": "NAVIGATION_ONLY", "diagnoses": [], "alternatives": [],
        "recommendation": None, "lenses": [], "_links": [], "warnings": []}
    if intent == "catalog":
        result["available"] = [{"id": x["id"], "kind": x["kind"], "status": x["status"]}
                                for x in lenses]
        result["recipes"] = [{"id": x["id"], "status": x["status"]} for x in recipes]
        return result
    if basis != "observed":
        result["_links"].append({"rel": "inspect-code" if basis == "unknown" else "refresh-basis",
                                 "why": "No hay evidencia vigente sobre código real"})
        return result
    if language == "unknown":
        result["_links"].append({"rel": "identify-language", "why": "Verificar lenguaje/versión"})
        return result
    if not signals and not state.get("problems"):
        result["_links"].append({"rel": "discover-signals", "why": "Observar un caso de uso y su riesgo"})
        return result
    if signals == {"unknown"} and not state.get("problems"):
        result["_links"].append({"rel": "discover-signals", "why": "Señales todavía indeterminadas"})
        return result
    diagnoses = _diagnose(state, problems, signals)
    result["diagnoses"] = diagnoses
    choices = _choices(diagnoses, recipes, facts, blockers, language)
    result["alternatives"] = [{k: v for k, v in entry.items() if k != "playbook"}
                              for entry in choices]
    result["alternatives"].append({"id": "keep-existing-code", "decision": "KEEP_AS_IS",
        "why": "Alternativa sin migración: preservar implementación y riesgo actual, "
               "salvo problema demostrado que justifique una receta", "problems": [x["id"] for x in diagnoses],
        "missing": [], "contraindications": [], "effort": "small",
        "risk": "routine", "reversibility": "easy"})
    if choices:
        result["recommendation"] = {"id": choices[0]["id"],
                                     "decision": choices[0]["decision"],
                                     "why": choices[0]["why"]}
    elif diagnoses:
        result["recommendation"] = {"id": "keep-existing-code", "decision": "KEEP_AS_IS",
                                     "why": "Ninguna receta disponible supera la opción de conservar el código"}
    for lens in _select_lenses(diagnoses, lenses, signals, intent, language, phase):
        result["lenses"].append({"id": lens["id"], "kind": lens["kind"],
                                  "question": lens["question"]})
        result["_links"].append({"rel": "read-lens", "href": _local_path(lens["playbook"]),
                                 "lens_id": lens["id"], "why": lens["question"]})
    if result["recommendation"] is not None:
        preferred = choices[0] if choices else None
        if preferred and preferred["decision"] == "APPLY":
            if phase == "diagnose":
                result["_links"].append({"rel": "compare-options", "why": "Contrastar alternativa local y KEEP_AS_IS"})
            elif phase == "plan":
                result["_links"].append({"rel": "read-recipe", "href": _local_path(preferred["playbook"]),
                                         "recipe_id": preferred["id"], "why": preferred["why"]})
                result["_links"].append({"rel": "propose-slice", "why": "Planificar un cambio reversible antes de ejecutarlo"})
            else:
                result["_links"].append({"rel": "verify-contracts",
                                         "why": "Comprobar comportamiento y coste del cambio ejecutado; no declarar PASS por plan"})
        elif preferred and preferred["decision"] in {"INSPECT_MORE", "BLOCKED"}:
            result["_links"].append({"rel": "inspect-problem", "why": preferred["why"]})
        elif preferred and preferred["decision"] == "KEEP_AS_IS":
            result["_links"].append({"rel": "preserve-existing", "why": preferred["why"]})
    if any(x["status"] == "INFERRED" for x in diagnoses):
        result["warnings"].append("Señales sin trazabilidad suficiente: hipótesis, no causa demostrada")
    if risk != "routine":
        result["warnings"].append("Revisar contratos, persistencia y concurrencia; el router nunca certifica PASS")
    if language == "other":
        result["warnings"].append("Sin adaptación idiomática: no copiar sintaxis Rust/Kotlin")
    # Descubrimiento de delegaciones condicionado a capacidades REALMENTE observadas.
    skills = _catalog("skill-registry.json", "related_skills")
    for skill in skills:
        if skill["id"] in available and intent in skill["intents"] and signals.intersection(skill["signals"]):
            result["_links"].append({"rel": "delegate-skill", "skill_id": skill["id"],
                                     "why": skill["purpose"]})
    return result


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Uso: affordances.py <session.json>")
    state = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(affordances(state), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
