#!/usr/bin/env python3
"""Pure commit-trailer index for reconciliation; no Git access or writes.

An implementation commit is a review hint, NOT proof of completion.
Consumes curated commit-message snapshots, never guesses identities by title.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SHA = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
KEYS = {"Backlog-Task", "Roadmap-Block", "ADR-Ref", "Spec-Ref",
        "Implementation", "Verification"}
TRAILER = re.compile(r"^(Backlog-Task|Roadmap-Block|ADR-Ref|Spec-Ref|Implementation|Verification):\s*(\S.*?)\s*$")
ID = re.compile(r"[A-Za-z][A-Za-z0-9_./:#-]{0,255}\Z")


def trailers(message: str) -> dict[str, list[str]]:
    if not isinstance(message, str):
        raise ValueError("Commit message must be a string")
    # Only the last paragraph is a trailer block. Do not parse quoted
    # examples of 'Roadmap-Block:' within the body as observed references.
    blocks = re.split(r"\n\s*\n", message.strip())
    block = blocks[-1] if blocks else ""
    result: dict[str, list[str]] = {}
    for line in block.splitlines():
        match = TRAILER.fullmatch(line)
        if match is None:
            return {}
        name, value = match.groups()
        if name not in {"Implementation", "Verification"} and not ID.fullmatch(value):
            raise ValueError("Unsafe trace identifier")
        if len(value) > 600:
            raise ValueError("Oversized trailer")
        result.setdefault(name, []).append(value)
    return result


def index(snapshot: dict, packet: dict) -> dict:
    if (not isinstance(snapshot, dict) or snapshot.get("schemaVersion") != 1
            or snapshot.get("kind") != "commit-messages"
            or not isinstance(snapshot.get("commits"), list)):
        raise ValueError("Expected commit-messages schemaVersion 1")
    if (not isinstance(packet, dict) or packet.get("schemaVersion") != 1
            or packet.get("kind") != "spec-packet" or not isinstance(packet.get("tasks"), list)):
        raise ValueError("Expected spec-packet schemaVersion 1")
    tasks = packet["tasks"]
    if not all(isinstance(t, dict) and isinstance(t.get("key"), str)
               and isinstance(t.get("sourceRef"), str) for t in tasks):
        raise ValueError("Malformed spec tasks")
    # A short unqualified ID is never enough if different specifications
    # expose the same fragment identifier.
    fragments = {}
    for t in tasks:
        fragment = t["sourceRef"].rsplit("#", 1)[-1]
        fragments.setdefault(fragment, set()).add(t["sourceRef"])
    matches = {t["key"]: [] for t in tasks}
    warnings = []
    seen = set()
    for row in snapshot["commits"]:
        if (not isinstance(row, dict) or not isinstance(row.get("sha"), str)
                or not SHA.fullmatch(row["sha"]) or not isinstance(row.get("message"), str)):
            raise ValueError("Malformed commit record")
        sha = row["sha"]
        if sha in seen:
            raise ValueError("Duplicate commit SHA")
        seen.add(sha)
        fields = trailers(row["message"])
        if not fields:
            continue
        identifiers = fields.get("Roadmap-Block", []) + fields.get("Spec-Ref", []) + fields.get("ADR-Ref", [])
        if not fields.get("Implementation") or not fields.get("Verification"):
            warnings.append(f"{sha[:12]}: incomplete implementation/verification trailers; review manually")
            continue
        for t in tasks:
            ref = t["sourceRef"]
            frag = ref.rsplit("#", 1)[-1]
            linked = (ref in identifiers or
                      (frag in identifiers and len(fragments[frag]) == 1) or
                      any(d in identifiers for d in t.get("documentRefs", [])))
            if linked:
                matches[t["key"]].append({
                    "sha": sha,
                    "backlogTaskIds": fields.get("Backlog-Task", []),
                    "implementation": fields["Implementation"],
                    "verification": fields["Verification"],
                    "status": "REVIEW_ONLY",
                })
    return {"schemaVersion": 1, "kind": "implementation-references",
            "matches": matches, "warnings": warnings,
            "notice": "Commits are historical leads, not runtime or acceptance evidence."}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("commit_messages_json")
    p.add_argument("spec_packet_json")
    args = p.parse_args()
    records = json.loads(Path(args.commit_messages_json).read_text(encoding="utf-8"))
    packet = json.loads(Path(args.spec_packet_json).read_text(encoding="utf-8"))
    print(json.dumps(index(records, packet), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
