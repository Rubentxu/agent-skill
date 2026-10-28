#!/usr/bin/env python3
"""Read-only Git index audit for PRIVATE project-management artefacts.

Never deletes files, edits .gitignore, changes the index, or rewrites Git history.
Use on a consumer application, not the agent-skill source distribution.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import PurePosixPath

DOC = re.compile(r"^(?:roadmap|backlog|project[-_]plan|sprint[-_]plan|milestones|decisions|specifications?)(?:[-_.][^.]+)?\.(?:md|mdx|rst|txt|pdf|docx|odt|json|ya?ml)$", re.I)
NUMBERED = re.compile(r"^(?:adr|spec|roadmap|milestone)[-_][a-z0-9][a-z0-9_.-]*\.(?:md|mdx|rst|txt|pdf|docx)$", re.I)
ARCHIVE = re.compile(r"(?:^|[-_.])(?:backlog|roadmap|adr|specs?|specifications?|milestones?|sprints?|project[-_]plans?)(?:[-_.]|$)", re.I)
BUNDLE_EXT = (".zip", ".tar.gz", ".tgz", ".7z", ".rar")
MANAGED_DIRS = {"backlog", ".backlog", "specs", "specifications", "roadmaps", "adrs", "adr", "milestones", "project-management", "planning"}
IGNORE = [
    "/backlog/", "/.backlog/", "/backlog.config.yml",
    "/ROADMAP.md", "/BACKLOG.md", "/docs/adr/", "/docs/specs/",
    "/docs/specifications/", "/docs/roadmaps/", "/specs/", "/planning/",
    "*roadmap*.zip", "*backlog*.zip", "*specs*.zip", "*adr*.zip",
]


def classify(path: str) -> str | None:
    if not isinstance(path, str) or not path or "\x00" in path or "\\" in path:
        return None
    p = PurePosixPath(path)
    parts = p.parts
    if p.is_absolute() or ".." in parts or not parts:
        return None
    lowered = tuple(x.lower() for x in parts)
    # Installed skill packages, test fixtures and source documentation are
    # distributable code assets, not the consumer's private planning corpus.
    if lowered[0] in {"skills", "node_modules", "vendor", ".git"}:
        return None
    name = lowered[-1]
    if name == "backlog.config.yml":
        return "backlog-config"
    if lowered[0] in {"backlog", ".backlog"}:
        return "backlog-managed"
    if lowered[0] in MANAGED_DIRS or (len(lowered) > 2 and lowered[0] == "docs" and lowered[1] in MANAGED_DIRS):
        return "planning-folder"
    if DOC.fullmatch(name) or NUMBERED.fullmatch(name):
        return "planning-document"
    if name.endswith(BUNDLE_EXT) and ARCHIVE.search(name):
        return "planning-archive"
    return None


def audit(tracked: list[str], staged: list[str] | None = None) -> dict:
    violations = [{"path": p, "kind": kind} for p in sorted(set(tracked))
                  if (kind := classify(p)) is not None]
    staged_set = set(staged or [])
    return {
        "schemaVersion": 1, "kind": "git-planning-artifact-audit",
        "status": "REVIEW_REQUIRED" if violations else "CLEAR",
        "tracked": [{**x, "staged": x["path"] in staged_set} for x in violations],
        "suggestedIgnorePatterns": IGNORE,
        "removalArgv": [["git", "rm", "--cached", "--", x["path"]] for x in violations],
        "effects": [
            "These are proposals only. Preserve working files and make a verified private backup before any untracking.",
            "git rm --cached removes an index entry, not local content; historical commits still contain the files.",
            "Adding .gitignore alone does not untrack existing files; verify config and all tracked paths.",
            "Backlog.md may rely on Git cross-branch history and auto-commit: inspect configuration and degraded features.",
            "Never rewrite Git history or delete planning documents automatically.",
        ],
    }


def _git_paths(root: str, *args: str) -> list[str]:
    result = subprocess.run(["git", "-C", root, *args], check=True, capture_output=True)
    return [x.decode("utf-8", "surrogateescape")
            for x in result.stdout.split(b"\0") if x]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="existing consumer Git checkout")
    parser.add_argument("--check", action="store_true", help="exit nonzero when tracked planning artefacts are found")
    args = parser.parse_args()
    try:
        tracked = _git_paths(args.repo, "ls-files", "-z", "--cached")
        staged = _git_paths(args.repo, "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR")
    except (OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": f"Git index unavailable: {exc}"}))
        return 2
    result = audit(tracked, staged)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if args.check and result["tracked"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
