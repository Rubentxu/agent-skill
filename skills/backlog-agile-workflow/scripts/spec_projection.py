#!/usr/bin/env python3
"""Pure, fail-closed projection from a curated spec packet to Backlog.md proposals.

Does NOT read any repository, invoke CLI, write files or certify implementation.
The caller must verify that sourceRefs were extracted from authoritative documents,
and that task-list is a complete UNFILTERED visible corpus. No fuzzy ID guessing.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

KEY = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,79}\Z")
REF = re.compile(r"[A-Za-z0-9_./-]+#[A-Za-z0-9_.:-]+\Z")
PRIORITY = {"high": 3, "medium": 2, "low": 1}
EFFORT = {"small": 1, "medium": 2, "large": 3}
LIFECYCLE = {"planned", "active", "implemented", "verified", "closed", "unknown"}


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 1200:
        raise ValueError(f"Invalid {label}")
    return value.strip()


def _key(value: Any) -> str:
    value = _string(value, "key")
    if not KEY.fullmatch(value):
        raise ValueError(f"Invalid key: {value}")
    return value


def _ref(value: Any) -> str:
    value = _string(value, "sourceRef")
    if not REF.fullmatch(value) or value.startswith("/") or ".." in value.split("#", 1)[0].split("/"):
        raise ValueError(f"Unsafe or noncanonical sourceRef: {value}")
    return value


def _strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
        raise ValueError(f"Invalid {label}")
    if len(set(value)) != len(value):
        raise ValueError(f"Duplicate {label}")
    return value


def _packet(packet: dict) -> tuple[list[dict], list[dict]]:
    if not isinstance(packet, dict) or packet.get("kind") != "spec-packet" or packet.get("schemaVersion") != 1:
        raise ValueError("Invalid spec-packet envelope")
    milestones, tasks = packet.get("milestones"), packet.get("tasks")
    if not isinstance(milestones, list) or not isinstance(tasks, list) or len(tasks) > 200:
        raise ValueError("Milestones/tasks missing or over budget")
    if not tasks:
        raise ValueError("No goals selected: do not invent tasks")
    mkeys = set()
    for m in milestones:
        if not isinstance(m, dict):
            raise ValueError("Malformed milestone")
        key = _key(m.get("key"))
        if key in mkeys:
            raise ValueError("Duplicate milestone key")
        mkeys.add(key)
        _string(m.get("title"), "milestone title")
        _ref(m.get("sourceRef"))
        if m.get("state") not in LIFECYCLE:
            raise ValueError("Invalid milestone state")
    keys, refs = set(), set()
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("Malformed task")
        key, ref = _key(task.get("key")), _ref(task.get("sourceRef"))
        if key in keys or ref in refs:
            raise ValueError("Duplicate task identity/sourceRef")
        keys.add(key);refs.add(ref)
        _string(task.get("title"), "title")
        _string(task.get("outcome"), "outcome")
        _strings(task.get("acceptanceCriteria"), "acceptanceCriteria")
        if not task["acceptanceCriteria"]:
            raise ValueError("Acceptance criteria required")
        _strings(task.get("definitionOfDone"), "definitionOfDone")
        _strings(task.get("dependsOn"), "dependsOn")
        _strings(task.get("documentRefs"), "documentRefs")
        for r in task["documentRefs"]:
            _ref(r)
        if task.get("milestone") not in mkeys:
            raise ValueError("Unknown milestone")
        if task.get("state") not in LIFECYCLE:
            raise ValueError("Unknown task state")
        if not isinstance(task.get("priorityFactors"), dict):
            raise ValueError("Priority factors required")
        p = task["priorityFactors"]
        if set(p) != {"impact", "urgency", "risk", "effort"} or (
            any(p[k] not in PRIORITY for k in ("impact", "urgency", "risk"))
            or p["effort"] not in EFFORT
        ):
            raise ValueError("Missing/invalid priority factors")
        if not isinstance(task.get("evidenceRefs"), list) or not all(isinstance(e, str) and e.strip() for e in task["evidenceRefs"]):
            raise ValueError("Invalid evidenceRefs")
    for task in tasks:
        if any(_key(dep) not in keys or dep == task["key"] for dep in task["dependsOn"]):
            raise ValueError("Unresolved/self dependency; do not infer links")
    # Cycle detection: dependencies must be a DAG.
    lookup = {task["key"]: task for task in tasks}
    colors = {}
    def visit(k):
        if colors.get(k) == 1:
            raise ValueError("Dependency cycle detected")
        if colors.get(k) == 2:
            return
        colors[k] = 1
        for dep in lookup[k]["dependsOn"]:
            visit(dep)
        colors[k] = 2
    for key in keys:
        visit(key)
    return milestones, tasks


def _existing(snapshot: dict | None) -> tuple[dict[str, dict], list[dict], list[str]]:
    if snapshot is None:
        return {}, [], ["Backlog snapshot absent: no create operations can be proposed as safe"]
    if not isinstance(snapshot, dict) or snapshot.get("kind") != "task-list" or snapshot.get("schemaVersion") != 1:
        raise ValueError("Backlog task-list schemaVersion 1 required")
    if not isinstance(snapshot.get("tasks"), list):
        raise ValueError("Malformed backlog task list")
    records = snapshot["tasks"]
    ids = []
    refs: dict[str, dict] = {}
    for task in records:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str) or not isinstance(task.get("title"), str):
            raise ValueError("Malformed task-list record")
        if task["id"] in ids:
            raise ValueError("Ambiguous task ID in visible corpus")
        ids.append(task["id"])
        incoming = task.get("references", [])
        if not isinstance(incoming, list):
            raise ValueError("Unsupported reference format")
        for item in incoming:
            # The CLI's compact references are strings. Do not silently
            # claim an unrecognized shape means there is no source reference.
            if not isinstance(item, str):
                raise ValueError("Unknown references shape; inspect task view")
            if REF.fullmatch(item):
                if item in refs:
                    raise ValueError("Multiple tasks own the same sourceRef")
                refs[item] = task
    return refs, records, []


def _implementation_index(evidence: dict | None, keys: set[str]) -> tuple[dict[str, list[dict]], list[str]]:
    if evidence is None:
        return {}, []
    if (not isinstance(evidence, dict) or evidence.get("schemaVersion") != 1
            or evidence.get("kind") != "implementation-references"
            or not isinstance(evidence.get("matches"), dict)
            or not isinstance(evidence.get("warnings", []), list)):
        raise ValueError("Invalid implementation-references snapshot")
    if not set(evidence["matches"]).issubset(keys):
        raise ValueError("Implementation references contain unknown task keys")
    matches = {}
    for key, entries in evidence["matches"].items():
        if not isinstance(entries, list):
            raise ValueError("Implementation evidence must be list")
        verified = []
        for entry in entries:
            if (not isinstance(entry, dict) or not isinstance(entry.get("sha"), str)
                    or not re.fullmatch(r"[0-9a-f]{40}(?:[0-9a-f]{24})?", entry["sha"])
                    or entry.get("status") != "REVIEW_ONLY"
                    or not isinstance(entry.get("backlogTaskIds"), list)
                    or not all(isinstance(t, str) and t for t in entry["backlogTaskIds"])):
                raise ValueError("Malformed implementation evidence")
            verified.append(entry)
        matches[key] = verified
    return matches, list(evidence.get("warnings", []))


def _rank(factors: dict[str, str]) -> dict[str, Any]:
    # Ordinal tie-breaking, NOT a calibrated estimate or a CLI priority.
    score = 3 * PRIORITY[factors["impact"]] + 2 * PRIORITY[factors["urgency"]] + PRIORITY[factors["risk"]] - EFFORT[factors["effort"]]
    tier = "P0" if score >= 15 else "P1" if score >= 11 else "P2" if score >= 7 else "P3"
    return {"tier": tier, "score": score, "why": "impact*3 + urgency*2 + risk - effort; ordinal proposal, requires human review"}


def project(packet: dict, snapshot: dict | None, commit_evidence: dict | None = None) -> dict:
    milestones, tasks = _packet(packet)
    refs, records, warnings = _existing(snapshot)
    commit_matches, commit_warnings = _implementation_index(commit_evidence, {t["key"] for t in tasks})
    warnings.extend(commit_warnings)
    result = {"schemaVersion": 1, "kind": "backlog-projection", "status": "PROPOSAL_ONLY",
              "sourceOfTruth": "specification documents", "taskAuthority": "Backlog.md CLI",
              "milestones": [], "actions": [], "warnings": list(warnings), "summary": {}}
    incomplete = snapshot is None or packet.get("snapshotScope") != "unfiltered-visible-corpus"
    if incomplete:
        result["warnings"].append("Unfiltered, complete visible task-list not confirmed; do not create missing tasks")
    if snapshot is not None:
        result["warnings"].append("Other branches/worktrees may contain tasks: cross-branch reconciliation is required before writes")
    for m in milestones:
        result["milestones"].append({"key": m["key"], "title": m["title"], "sourceRef": m["sourceRef"],
                  "state": m["state"], "action": "REVIEW_MILESTONE" if m["state"] != "closed" else "PRESERVE_HISTORICAL"})
    by_key={t["key"]: t for t in tasks}
    for task in tasks:
        ref = task["sourceRef"]
        pri = _rank(task["priorityFactors"])
        match = refs.get(ref)
        same_title = [t for t in records if t["title"].strip().casefold() == task["title"].strip().casefold()]
        if match:
            disposition = ("PRESERVE_ARCHIVED" if match.get("archived") is True else
                           "REVIEW_EXISTING" if task["state"] not in {"closed", "verified"}
                           else "PRESERVE_HISTORICAL")
        elif task["state"] in {"closed", "verified"}:
            disposition = "PRESERVE_HISTORICAL"
        elif incomplete:
            disposition = "NEEDS_CORPUS"
        elif same_title:
            disposition = "REVIEW_POSSIBLE_DUPLICATE"
        elif task["state"] == "unknown":
            disposition = "INSPECT_STATUS"
        else:
            disposition = "PROPOSE_CREATE"
        prior_commits = commit_matches.get(task["key"], [])
        referenced_task_ids = {task_id for item in prior_commits for task_id in item["backlogTaskIds"]}
        recorded_ids = {item["id"] for item in records}
        if match and referenced_task_ids and match["id"] not in referenced_task_ids:
            disposition = "REVIEW_IDENTITY_CONFLICT"
        elif not match and referenced_task_ids.intersection(recorded_ids):
            disposition = "REVIEW_POSSIBLE_DUPLICATE"
        elif prior_commits and not match and disposition in {"PROPOSE_CREATE", "WAIT_FOR_DEPENDENCY_IDS", "INSPECT_STATUS"}:
            disposition = "REVIEW_IMPLEMENTATION"
        pending_deps = [dep for dep in task["dependsOn"] if by_key[dep]["sourceRef"] not in refs]
        if disposition == "PROPOSE_CREATE" and pending_deps:
            disposition = "WAIT_FOR_DEPENDENCY_IDS"
        action = {"key": task["key"], "sourceRef": ref, "title": task["title"],
                  "milestoneKey": task["milestone"], "disposition": disposition,
                  "existingTaskId": match["id"] if match else None,
                  "linkedCommitSHAs": [item["sha"] for item in prior_commits],
                  "priorityProposal": pri, "dependsOnKeys": task["dependsOn"],
                  "pendingDependencyKeys": pending_deps, "acceptanceCriteria": task["acceptanceCriteria"],
                  "definitionOfDone": task["definitionOfDone"], "outcome": task["outcome"],
                  "documentRefs": task["documentRefs"], "evidenceRefs": task["evidenceRefs"],
                  "stateDeclared": task["state"], "gate": task.get("gate"),
                  "next": "Inspect full task view and current source before edit" if match else "Review proposed CLI create parameters, then resolve milestones/dependencies"}
        if same_title and not match:
            action["possibleDuplicateIds"] = [t["id"] for t in same_title]
        if task["state"] in {"closed", "verified"} and not task["evidenceRefs"]:
            result["warnings"].append(f"{task['key']}: documentary completion without receipt reference; no certification inferred")
        if prior_commits:
            result["warnings"].append(f"{task['key']}: matching commits require current-code and acceptance review; no completion inferred")
        if match and match.get("archived") is True:
            result["warnings"].append(f"{task['key']}: archived task {match['id']} is read-only; restoration requires explicit approval")
        result["actions"].append(action)
    # Dependencies block consumers; advertise topo rank, not arbitrary priorities.
    rank = {}
    def depth(key):
        if key not in rank:
            rank[key] = 1 + max((depth(d) for d in by_key[key]["dependsOn"]), default=-1)
        return rank[key]
    for t in tasks:depth(t["key"])
    result["actions"].sort(key=lambda a: (rank[a["key"]], -a["priorityProposal"]["score"], a["key"]))
    types = sorted({a["disposition"] for a in result["actions"]})
    result["summary"] = {status:sum(a["disposition"] == status for a in result["actions"]) for status in types}
    result["warnings"].append("Never auto-close gates: documented CLOSED/verified is not runtime evidence; keep upstream receipts as authority")
    return result


def main() -> int:
    if len(sys.argv) not in {2, 3, 4}:
        raise SystemExit("Usage: spec_projection.py <spec-packet.json> [unfiltered-task-list.json] [implementation-references.json]")
    packet=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    snapshot=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")) if len(sys.argv)==3 else None
    evidence=json.loads(Path(sys.argv[3]).read_text(encoding="utf-8")) if len(sys.argv)==4 else None
    print(json.dumps(project(packet,snapshot,evidence),ensure_ascii=False,indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
