#!/usr/bin/env python3
"""Read-only planner of Backlog.md Kanban operations. No CLI or Git access."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

IDENTITY = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,63}\Z")
CONFIG = ("autoCommit", "remoteOperations", "bypassGitHooks", "onStatusChange")


def outcome(op, decision, reason, argv=None):
    return {"schemaVersion": 1, "kind": "board-operation-proposal",
            "operation": op, "decision": decision, "status": "NAVIGATION_ONLY",
            "reason": reason, "suggestedArgv": argv,
            "next": "Reread current task/configuration before executing, then verify CLI result"}


def text(value, name, max_length=900):
    if not isinstance(value, str) or not value.strip() or len(value) > max_length or "\0" in value:
        raise ValueError("Invalid " + name)
    return value.strip()


def strings(value, name):
    if not isinstance(value, list) or len(value) > 30:
        raise ValueError("Invalid " + name)
    result = [text(s, name) for s in value]
    if len(set(result)) != len(result):
        raise ValueError("Duplicate " + name)
    return result


def task_observed(task):
    if not isinstance(task, dict):
        raise ValueError("Observed task object required")
    identity = text(task.get("id"), "task ID", 64)
    if not IDENTITY.fullmatch(identity):
        raise ValueError("Unsafe task ID")
    text(task.get("status"), "observed status")
    if type(task.get("archived")) is not bool:
        raise ValueError("Observed archived must be boolean")
    for name in ("isReady", "finalSummaryRecorded"):
        if name in task and type(task[name]) is not bool:
            raise ValueError("Invalid " + name)
    for name in ("acceptanceCriteriaCount", "acceptanceCriteriaCompleted",
                 "definitionOfDoneCount", "definitionOfDoneCompleted"):
        if name in task and (type(task[name]) is not int or task[name] < 0):
            raise ValueError("Invalid " + name)
    return task


def verified(task, gate):
    if gate not in ("PASS", "NOT_REQUIRED") or task.get("finalSummaryRecorded") is not True:
        return False
    return all(task.get(k + "Count") is not None
               and task.get(k + "Completed") == task.get(k + "Count")
               for k in ("acceptanceCriteria", "definitionOfDone"))


def plan(data):
    if not isinstance(data, dict) or data.get("kind") != "board-operation" or data.get("schemaVersion") != 1:
        raise ValueError("Expected board-operation schemaVersion 1")
    op = data.get("operation")
    if op not in ("create", "transition", "archive", "restore", "delete"):
        raise ValueError("Unknown board operation")
    statuses = data.get("statuses")
    if (not isinstance(statuses, list) or not 2 <= len(statuses) <= 30
            or any(not isinstance(s, str) or not s.strip() or len(s) > 80 for s in statuses)
            or len(set(statuses)) != len(statuses)):
        raise ValueError("Configured statuses required")
    terminal = data.get("terminalStatus")
    if not isinstance(terminal, str) or terminal not in statuses:
        raise ValueError("Observed terminal status required")
    if op == "delete":
        return outcome(op, "BLOCKED", "Permanent deletion can release IDs and remove dependency links; separate human maintenance action required")
    if op == "create":
        if data.get("duplicateReview") != "clear":
            return outcome(op, "INSPECT_MORE", "Review existing tasks, drafts, archived records and historical identities")
        creation = data.get("newTask")
        if not isinstance(creation, dict):
            raise ValueError("newTask required")
        title = text(creation.get("title"), "title", 200)
        description = text(creation.get("description"), "description")
        ac = strings(creation.get("acceptanceCriteria"), "acceptance criteria")
        if not ac:
            return outcome(op, "BLOCKED", "At least one verifiable acceptance criterion required")
        selected = creation.get("status", statuses[0])
        if selected not in statuses or selected == terminal:
            return outcome(op, "BLOCKED", "New task requires configured, nonterminal status")
        refs = strings(creation.get("references", []), "references")
        argv = ["backlog", "task", "create", title, "-d", description]
        if selected != statuses[0]:
            argv.extend(["-s", selected])
        for criterion in ac:
            argv.extend(["--ac", criterion])
        for ref in refs:
            argv.extend(["--ref", ref])
    else:
        task = task_observed(data.get("task"))
        tid, current = task["id"], task["status"]
        if current not in statuses:
            return outcome(op, "INSPECT_MORE", "Observed status differs from configured columns")
        if op == "transition":
            if task["archived"]:
                return outcome(op, "BLOCKED", "Archived tasks are read-only; restore first")
            target = data.get("targetStatus")
            if target not in statuses:
                return outcome(op, "BLOCKED", "Target must match configured column exactly")
            if target == current:
                return outcome(op, "NO_CHANGE", "Already in target column")
            if target == terminal and not verified(task, data.get("gateResult")):
                return outcome(op, "BLOCKED", "Final status requires verified AC/DoD, gate and recorded summary")
            if current == terminal and target != terminal and not data.get("reopenReason"):
                return outcome(op, "INSPECT_MORE", "Reopening needs an explicit reason")
            if current == statuses[0] and target != terminal and task.get("isReady") is not True:
                return outcome(op, "INSPECT_MORE", "Check readiness and dependencies before starting")
            argv = ["backlog", "task", "edit", tid, "-s", target]
        elif op == "archive":
            if task["archived"]:
                return outcome(op, "NO_CHANGE", "Task already archived")
            reason = data.get("archiveReason")
            if reason not in ("completed", "cancelled", "duplicate", "invalid", "obsolete"):
                return outcome(op, "INSPECT_MORE", "Explicit archive reason required")
            if reason == "completed":
                if current != terminal or not verified(task, data.get("gateResult")):
                    return outcome(op, "BLOCKED", "Completed archive requires terminal status and verified AC/DoD/gate/summary")
            elif data.get("dependencyImpact") != "reviewed" or task.get("finalSummaryRecorded") is not True:
                return outcome(op, "INSPECT_MORE", "Record reason and inspect dependents; archived unfinished task still blocks")
            argv = ["backlog", "task", "archive", tid]
        else:
            if not task["archived"]:
                return outcome(op, "NO_CHANGE", "Task already on the board")
            argv = ["backlog", "task", "restore", tid]
    config = data.get("config")
    if (not isinstance(config, dict) or set(config) != set(CONFIG)
            or any(type(config[k]) is not bool for k in CONFIG)):
        return outcome(op, "INSPECT_MORE", "Observe all Git/callback configuration before any write")
    active = [k for k in CONFIG if config[k]]
    if active and data.get("effectsAcknowledged") is not True:
        return outcome(op, "BLOCKED", "Review configuration side effects: " + ", ".join(active))
    if data.get("authorized") is not True:
        return outcome(op, "PROPOSE_ONLY", "Explicit write permission required", argv)
    return outcome(op, "AUTHORIZED_ACTION", "Authorized proposal; this helper never executes CLI", argv)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: board_crud.py <board-operation.json>")
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(plan(data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
