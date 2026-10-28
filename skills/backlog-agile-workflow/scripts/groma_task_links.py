#!/usr/bin/env python3
"""Pure Backlog.md/Groma.md task-link planner. No subprocess or filesystem writes.

Consumes a curated task view, observed changed file paths, and confirmed Groma
element IDs. Produces *argv proposals* only, never ownership claims or commands.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

TASK = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,63}\Z")
ELEMENT = re.compile(r"[a-z0-9][a-z0-9_-]{0,127}\Z")
MAX = 250


def _path(value: Any) -> str:
    if (not isinstance(value, str) or not value or len(value) > 400
            or value.startswith("/") or "\\" in value
            or any(part in {"", ".", ".."} for part in value.split("/"))
            or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        raise ValueError("Invalid repository-relative file path")
    return value


def _unique(values: Any, field: str, validate) -> list[str]:
    if not isinstance(values, list) or len(values) > MAX:
        raise ValueError("Invalid or oversized " + field)
    result = [validate(v) for v in values]
    if len(result) != len(set(result)):
        raise ValueError("Duplicate " + field)
    return result


def _reference(value: Any) -> str:
    if (not isinstance(value, str) or not value.strip() or len(value) > 400
            or "\n" in value or "\r" in value or "\0" in value):
        raise ValueError("Invalid task reference")
    return value


def plan(data: dict) -> dict:
    if (not isinstance(data, dict) or data.get("schemaVersion") != 1
            or data.get("kind") != "groma-task-link-input"):
        raise ValueError("Expected groma-task-link-input schemaVersion 1")
    allowed = {"schemaVersion", "kind", "task", "changedFiles", "confirmedElementIds", "replacements"}
    if set(data) - allowed:
        raise ValueError("Unknown input fields")
    task = data.get("task")
    if not isinstance(task, dict) or set(task) != {"id", "modifiedFiles", "references"}:
        raise ValueError("Task view must supply id, modifiedFiles and references")
    tid = task["id"]
    if not isinstance(tid, str) or not TASK.fullmatch(tid):
        raise ValueError("Invalid task ID")
    previous = _unique(task["modifiedFiles"], "modifiedFiles", _path)
    references = _unique(task["references"], "references", _reference)
    changed = _unique(data.get("changedFiles", []), "changedFiles", _path)
    targets = _unique(data.get("confirmedElementIds", []), "confirmedElementIds",
                      lambda v: v if isinstance(v, str) and ELEMENT.fullmatch(v)
                      else (_ for _ in ()).throw(ValueError("Invalid Groma element ID")))
    replacements = data.get("replacements", [])
    if not isinstance(replacements, list) or len(replacements) > MAX:
        raise ValueError("Malformed Groma replacements")
    removed: list[str] = []
    added: list[str] = []
    for value in replacements:
        if (not isinstance(value, dict) or set(value) != {"old", "new"}
                or not all(isinstance(value[k], str) and ELEMENT.fullmatch(value[k])
                           for k in ("old", "new")) or value["old"] == value["new"]):
            raise ValueError("Invalid structural replacement")
        if value["old"] not in references:
            raise ValueError("Replacement source not present in task references; inspect task")
        removed.append(value["old"])
        added.append(value["new"])
    if len(set(removed)) != len(removed) or len(set(added)) != len(added):
        raise ValueError("Conflicting Groma replacements")
    # Only remove explicit prior IDs that Groma reports as replaced; preserve
    # opaque roadmap/ADR/spec refs and avoid assuming changedFiles prove owners.
    final_files = previous + [p for p in changed if p not in previous]
    final_refs = [r for r in references if r not in removed]
    for target in added + targets:
        if target not in final_refs:
            final_refs.append(target)
    files_added = final_files[len(previous):]
    refs_added = [r for r in final_refs if r not in references]
    refs_removed = [r for r in references if r not in final_refs]
    argv: list[list[str]] = []
    if files_added:
        cmd = ["backlog", "task", "edit", tid]
        for value in final_files:
            cmd += ["--modified-file", value]
        argv.append(cmd)
    if refs_added or refs_removed:
        cmd = ["backlog", "task", "edit", tid]
        for value in refs_removed:
            cmd += ["--remove-ref", value]
        for value in refs_added:
            cmd += ["--add-ref", value]
        argv.append(cmd)
    return {
        "schemaVersion": 1, "kind": "groma-task-link-proposal",
        "status": "PROPOSAL_ONLY" if argv else "NO_CHANGE",
        "taskId": tid, "fullModifiedFiles": final_files,
        "fullReferences": final_refs, "addedFiles": files_added,
        "addedRefs": refs_added, "removedRefs": refs_removed,
        "suggestedArgv": argv,
        "warnings": [
            "Verify the exact current task view and project/worktree immediately before applying.",
            "--modified-file replaces the entire list: pass every previously modified path.",
            "Only confirmed Groma element IDs are added; a task reference does not establish code ownership.",
            "Groma's ID replacements are not persisted as aliases; apply before the next structural change.",
            "Do not commit private groma/ or Backlog.md documents, even when tracking their changed paths in the task.",
        ],
    }


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: groma_task_links.py <groma-task-link-input.json>")
    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(plan(payload), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
