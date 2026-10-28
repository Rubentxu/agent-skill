#!/usr/bin/env python3
"""Validate one-shot Backlog.md task-list JSON, presenting eligible tasks in CLI order.

Reads ONLY an explicit JSON snapshot. Never queries Backlog.md, edits, reprioritizes,
or mistakes a page of results for the full board.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

MAX_TASKS = 20000
MAX_BYTES = 8 * 1024 * 1024


def candidates(payload: dict[str, Any], limit: int = 5) -> dict[str, Any]:
    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError("limit must be 1..20")
    if not isinstance(payload, dict) or type(payload.get("schemaVersion")) is not int or payload["schemaVersion"] != 1 or payload.get("kind") != "task-list":
        raise ValueError("Unsupported Backlog.md task-list JSON envelope")
    items = payload.get("tasks")
    if not isinstance(items, list) or len(items) > MAX_TASKS:
        raise ValueError("Task list missing or too large")
    seen = set()
    result: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Malformed task")
        tid, title = item.get("id"), item.get("title")
        if not isinstance(tid, str) or not tid.strip() or not isinstance(title, str) or not title.strip() or tid in seen:
            raise ValueError("Missing, invalid, or duplicate task identity")
        seen.add(tid)
        archived, ready = item.get("archived"), item.get("isReady")
        if type(archived) is not bool or type(ready) is not bool:
            raise ValueError("Missing authoritative archived/isReady boolean")
        if ready and archived:
            raise ValueError("Contradictory archived/ready task")
        if ready:
            result.append({"id": tid, "title": title,
                           "status": item.get("status") if isinstance(item.get("status"), str) else None,
                           "priority": item.get("priority") if isinstance(item.get("priority"), str) else None})
    return {"status": "NAVIGATION_ONLY", "source_kind": "task-list", "total_in_snapshot": len(items),
            "ready_in_snapshot": len(result), "candidates": result[:limit],
            "truncated_candidates": len(result) > limit,
            "notice": "Mantiene el orden del CLI. La instantánea puede estar filtrada/paginada; priorización de valor y selección final requieren revisión."}


def main() -> None:
    if len(sys.argv) not in (2, 3):
        raise SystemExit("Uso: ready_candidates.py <task-list.json> [max_candidates]")
    p = Path(sys.argv[1])
    if not p.is_file() or p.is_symlink() or p.stat().st_size > MAX_BYTES:
        raise ValueError("Missing, unsafe or oversized task snapshot")
    limit = int(sys.argv[2]) if len(sys.argv) == 3 else 5
    data = json.loads(p.read_text(encoding="utf-8"))
    print(json.dumps(candidates(data, limit), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
