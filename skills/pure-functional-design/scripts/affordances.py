#!/usr/bin/env python3
"""Calcula enlaces a playbooks observados, sin ejecutar ni modificar proyectos."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "references/lens-registry.json"
INTENTS = frozenset({"catalog", "discovery", "design", "implementation", "refactor", "review"})
LANGUAGES = frozenset({"rust", "kotlin", "other", "unknown"})
BASIS = frozenset({"observed", "unknown", "stale"})
RISKS = frozenset({"routine", "high", "critical"})
SIGNALS = frozenset({
    "domain-ambiguity", "invalid-state", "side-effects", "large-service",
    "duplicate-logic", "complex-algorithm", "nested-data", "cross-context",
    "legacy-test-coupling", "unknown",
})


def _read_catalog() -> list[dict[str, Any]]:
    result = json.loads(REGISTRY.read_text(encoding="utf-8"))["lenses"]
    assert len({lens["id"] for lens in result}) == len(result), "lentes duplicadas"
    return result


def _notice(rel: str, reason: str) -> dict[str, str]:
    return {"rel": rel, "why": reason}


def affordances(state: dict[str, Any]) -> dict[str, Any]:
    """Selecciona lentes con señales; no infiere que un efecto ya se ejecutó."""
    intent = state.get("intent", "catalog")
    language = state.get("language", "unknown")
    basis = state.get("basis", "unknown")
    risk = state.get("risk", "routine")
    signals = state.get("signals", [])
    if intent not in INTENTS or language not in LANGUAGES or basis not in BASIS or risk not in RISKS:
        raise ValueError("intent/language/basis/risk no válido")
    if not isinstance(signals, list) or not all(isinstance(s, str) and s in SIGNALS for s in signals):
        raise ValueError("signals debe ser una lista de señales conocidas")
    if len(signals) != len(set(signals)):
        raise ValueError("signals duplicadas")

    catalog = _read_catalog()
    result: dict[str, Any] = {"intent": intent, "basis": basis, "risk": risk,
                              "status": "NAVIGATION_ONLY", "lenses": [], "_links": [],
                              "warnings": []}
    if intent == "catalog":
        result["available"] = [{"id": x["id"], "kind": x["kind"], "status": x["status"]}
                                for x in catalog]
        return result
    if basis != "observed":
        result["_links"].append(_notice("inspect-code" if basis == "unknown" else "refresh-basis",
                                        "No se ha observado código actual; no afirmar hallazgos"))
        return result
    if language == "unknown":
        result["_links"].append(_notice("identify-language", "Verificar lenguaje/versión antes de dar sintaxis"))
        return result
    observed = set(signals)
    if not observed or observed == {"unknown"}:
        result["_links"].append(_notice("discover-signals", "Faltan señales verificadas por caso de uso"))
        return result

    methods = [x for x in catalog if x["kind"] == "method" and x["status"] == "ready"
               and intent in x["intents"] and observed.intersection(x["signals"])]
    methods.sort(key=lambda x: (-x["priority"], x["id"]))
    chosen = methods[:3]
    adapter = next((x for x in catalog if x["kind"] == "language" and x["status"] == "ready"
                    and x["language"] == language and intent in x["intents"]), None)
    if adapter:
        chosen.append(adapter)
    result["lenses"] = [{"id": x["id"], "kind": x["kind"], "question": x["question"]}
                        for x in chosen]
    for item in chosen:
        playbook = (ROOT / item["playbook"]).resolve()
        # Safety: referencias solo dentro de esta skill; links deben existir.
        if not playbook.is_relative_to(ROOT.resolve()) or not playbook.is_file():
            raise ValueError(f"Playbook inaccesible o inseguro: {item['id']}")
        result["_links"].append({"rel": "read-lens", "href": item["playbook"],
                                 "lens_id": item["id"], "why": item["question"]})
    if methods:
        result["_links"].append(_notice("propose-slice", "Elegir una mejora reversible y acotada"))
    if risk != "routine":
        result["warnings"].append("Revisar invariantes y compatibilidad antes de cualquier cambio; no certificar PASS")
    if language == "other":
        result["warnings"].append("Sin perfil idiomático para este lenguaje; no traducir sintaxis de Rust/Kotlin")
    if not methods:
        result["_links"].append(_notice("discover-signals", "Sin lente metodológica coincidente; ampliar contexto"))
    return result


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Uso: affordances.py <session.json>")
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("La sesión debe ser un objeto JSON")
    print(json.dumps(affordances(data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
