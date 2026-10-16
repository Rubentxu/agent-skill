#!/usr/bin/env python3
"""Pure, read-only affordance router for distribution-first-release."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "lens-registry.json"
RELATED = ROOT / "references" / "skill-registry.json"

INTENTS = {"catalog", "audit", "prepare", "release", "cleanup"}
PRODUCTS = {"unknown", "application", "cli", "library", "sdk", "plugin", "container"}
SIGNALS = {"release", "git", "archive", "package", "consumer", "integrity", "evidence", "history", "unknown"}
CHECKS = {"not_run", "passed", "failed", "blocked"}
ACTIONS = {
    "list-lenses": "references/navigation.md",
    "inspect-product": "references/lenses/asset-selection.md",
    "refresh-basis": "references/lenses/integrity-provenance.md",
    "plan-git-hygiene": "references/lenses/git-hygiene.md",
    "clarify-source-archives": "references/lenses/source-archive-boundary.md",
    "fix-asset-set": "references/lenses/asset-selection.md",
    "inventory-assets": "references/lenses/asset-selection.md",
    "investigate-failure": "references/lenses/release-publication.md",
    "inspect-package": "references/lenses/package-composition.md",
    "verify-consumer": "references/lenses/consumer-verification.md",
    "verify-integrity": "references/lenses/integrity-provenance.md",
    "publish-or-check-release": "references/lenses/release-publication.md",
    "finish-release": "references/lenses/release-publication.md",
    "audit-portfolio": "references/lenses/evidence-separation.md",
    "assess-history": "references/lenses/history-remediation.md",
}


class InvalidState(ValueError):
    pass


def _one(value: object, field: str, allowed: set[str]) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise InvalidState(f"{field} must be one of {sorted(allowed)}")
    return value


def _names(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(x, str) or not x or "/" in x or ".." in x for x in value
    ):
        raise InvalidState(f"{field} must contain simple non-blank names")
    if len(value) != len(set(value)):
        raise InvalidState(f"{field} contains duplicates")
    return value


def read_catalog(path: Path = CATALOG) -> dict[str, dict]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("schema_version") != 1 or not isinstance(doc.get("lenses"), list):
        raise InvalidState("invalid lens registry")
    out: dict[str, dict] = {}
    for lens in doc["lenses"]:
        ident = lens.get("id")
        if not isinstance(ident, str) or ident in out:
            raise InvalidState("duplicate/invalid lens id")
        if lens.get("status") not in {"ready", "planned"}:
            raise InvalidState("unknown lens status")
        ref = (ROOT / lens["playbook"]).resolve()
        if not ref.is_relative_to(ROOT) or not ref.is_file():
            raise InvalidState(f"unsafe/broken playbook: {ident}")
        out[ident] = lens
    return out


def affordances(state: dict) -> dict:
    if not isinstance(state, dict):
        raise InvalidState("state must be an object")
    intent = _one(state.get("intent"), "intent", INTENTS)
    lenses = read_catalog()
    signals = _names(state.get("signals", []), "signals")
    if any(signal not in SIGNALS for signal in signals):
        raise InvalidState("unknown signal")
    available = _names(state.get("available_skills", []), "available_skills")
    product = _one(state.get("product", "unknown"), "product", PRODUCTS)
    inventory = _one(state.get("inventory", "unknown"), "inventory", {"ready", "unknown"})
    basis = _one(state.get("basis", "unknown"), "basis", {"current", "unknown", "stale"})
    git = _one(state.get("git_artifacts", "unknown"), "git_artifacts", {"unknown", "clean", "bloated"})
    assets = _one(state.get("asset_set", "unknown"), "asset_set", {"unknown", "complete", "incomplete", "unexpected"})
    for key in ("package", "consumer", "integrity", "publication"):
        _one(state.get(key, "not_run"), key, CHECKS)
    _one(state.get("risk", "routine"), "risk", {"routine", "high", "critical"})
    if type(state.get("archive_confusion", False)) is not bool or type(state.get("lens_gap", False)) is not bool:
        raise InvalidState("archive_confusion/lens_gap must be boolean")

    if intent == "catalog":
        action, status = "list-lenses", "READY"
    elif inventory == "unknown" or product == "unknown":
        action, status = "inspect-product", "READY"
    elif basis != "current":
        action, status = "refresh-basis", "BLOCKED"
    elif intent == "cleanup":
        action, status = ("plan-git-hygiene" if git == "bloated" else "assess-history"), "READY"
    elif intent == "audit":
        action, status = "audit-portfolio", "READY"
    elif git == "bloated":
        action, status = "plan-git-hygiene", "READY"
    elif state.get("archive_confusion", False):
        action, status = "clarify-source-archives", "READY"
    elif assets in {"incomplete", "unexpected"}:
        action, status = "fix-asset-set", "FAILED"
    elif assets == "unknown":
        action, status = "inventory-assets", "READY"
    elif any(state.get(k) == "failed" for k in ("package", "consumer", "integrity", "publication")):
        action, status = "investigate-failure", "FAILED"
    elif any(state.get(k) == "blocked" for k in ("package", "consumer", "integrity", "publication")):
        action, status = "investigate-failure", "BLOCKED"
    elif state.get("package") != "passed":
        action, status = "inspect-package", "READY"
    elif state.get("consumer") != "passed":
        action, status = "verify-consumer", "READY"
    elif state.get("integrity") != "passed":
        action, status = "verify-integrity", "READY"
    elif state.get("publication") != "passed":
        action, status = "publish-or-check-release", "READY"
    else:
        action, status = "finish-release", "DONE"

    matching = []
    for lens in lenses.values():
        if lens["status"] != "ready" or intent not in lens["intents"]:
            continue
        if lens["signals"] and not set(lens["signals"]).intersection(signals):
            continue
        matching.append({
            "id": lens["id"], "question": lens["question"],
            "rel": "inspect-" + lens["id"], "href": lens["playbook"],
        })

    related = json.loads(RELATED.read_text(encoding="utf-8")).get("related_skills", [])
    peers = [
        {"id": x["id"], "purpose": x["purpose"]}
        for x in related
        if x["id"] in available and intent in x["intents"] and
        (not x["signals"] or set(x["signals"]).intersection(signals))
    ]
    for ref in ACTIONS.values():
        dest = (ROOT / ref).resolve()
        if not dest.is_relative_to(ROOT) or not dest.is_file():
            raise InvalidState(f"missing/unsafe action playbook {ref}")
    return {
        "status": status,
        "recommended": action,
        "_links": [{"rel": action, "href": ACTIONS[action], "why": "observed state"}],
        "lenses": matching,
        "related_skills": peers,
        "discovery": ([{"rel": "propose-lens", "href": "references/extend-lenses.md"}]
                      if state.get("lens_gap", False) or "unknown" in signals else []),
        "notice": "read-only decision aid; no tests executed, no assets published or certified",
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: affordances.py STATE.json|-", file=sys.stderr)
        return 2
    try:
        raw = sys.stdin.read() if sys.argv[1] == "-" else Path(sys.argv[1]).read_text(encoding="utf-8")
        result = affordances(json.loads(raw))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"INVALID_STATE: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
