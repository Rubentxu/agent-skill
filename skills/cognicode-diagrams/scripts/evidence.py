#!/usr/bin/env python3
"""Say, for every derived claim, what it earns and what is missing.

The ledger of a workspace is written by whoever investigated. This tool
does not rewrite it: it reads it, compares it against the published shape,
and reports what each claim is actually worth.

    python3 scripts/evidence.py --repo <raiz> --check
    python3 scripts/evidence.py --repo <raiz> --emit

`--check` writes a report and fails when a claim claims to be observed but
no structured query backs it. `--emit` writes the same verdict as a derived
artifact next to the ledger, so that whoever publishes the evidence can
publish the verdict with it and not only the claim.

Never reads the checkout: it only reads the derived workspace under HOME.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import evidence_contract as contract
import workspace as ws

SCHEMA_VERSION = 1
GENERATOR = "cognicode-diagrams-evidence"
LEDGER_NAME = "corroboration.json"
MAX_INPUT = 8 * 1024 * 1024


class EvidenceError(ValueError):
    """The workspace or its ledger cannot be read."""


def _no_symlinks(path: Path) -> None:
    for component in (path, *path.parents):
        if component.is_symlink():
            raise EvidenceError(f"ruta con enlace simbolico: {component}")


def _load(path: Path) -> object:
    if not path.is_file():
        raise EvidenceError(f"no existe el fichero de evidencia: {path}")
    if path.stat().st_size > MAX_INPUT:
        raise EvidenceError(f"el fichero de evidencia es demasiado grande: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise EvidenceError(f"no se pudo leer {path}: {exc}") from exc


def _write_owned(path: Path, content: str) -> None:
    """Write a derived artifact, refusing to touch anything we did not make."""
    if path.is_symlink():
        raise EvidenceError("el destino es un enlace simbolico")
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise EvidenceError(f"el destino no es un artefacto derivado: {path}") from exc
        if existing.get("generator") != GENERATOR:
            raise EvidenceError(f"el destino no lo genero esta skill: {path}")
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=".corroboration-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.chmod(temp, 0o644)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def examine(workspace_dir: Path) -> dict:
    """Read the ledger and report what every claim earns."""
    _no_symlinks(workspace_dir)
    evidence = workspace_dir / "evidence"
    claims_raw = _load(evidence / "claims.json")
    queries_raw = _load(evidence / "queries.json")
    try:
        return contract.report(claims_raw, queries_raw)
    except ValueError as exc:
        raise EvidenceError(f"el ledger no se pudo interpretar: {exc}") from exc


def ledger(workspace_dir: Path, report: dict) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "generator": GENERATOR,
        "workspace": str(workspace_dir),
        "claims": report["claims"],
        "counts": {
            "corroborated": report["corroborated"],
            "observed_not_corroborated": report["not_corroborated"],
            "not_implementation": report["not_implementation"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path,
                        help="raiz explicita del repositorio investigado")
    parser.add_argument("--home", type=Path, default=None,
                        help="raiz del HOME derivado; por defecto el del usuario")
    parser.add_argument("--check", action="store_true",
                        help="informa y falla si alguna afirmacion no esta corroborada")
    parser.add_argument("--emit", action="store_true",
                        help="escribe el veredicto derivado junto al ledger")
    args = parser.parse_args(argv)

    try:
        root = ws.supplied_repository_root(args.repo)
        workspace_dir = ws.workspace_path(root, home=args.home)
        if not workspace_dir.exists():
            raise EvidenceError(f"no hay material derivado para {root}")
        report = examine(workspace_dir)
    except (ws.WorkspaceError, EvidenceError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2

    result = {
        "status": "OK" if report["not_corroborated"] == 0 else "NOT_CORROBORATED",
        "workspace": str(workspace_dir),
        "counts": {
            "corroborated": report["corroborated"],
            "observed_not_corroborated": report["not_corroborated"],
            "not_implementation": report["not_implementation"],
        },
        "claims": report["claims"],
    }

    if args.emit:
        target = workspace_dir / "evidence" / LEDGER_NAME
        try:
            _write_owned(target, json.dumps(ledger(workspace_dir, report), ensure_ascii=False,
                                            sort_keys=True, indent=2) + "\n")
        except (EvidenceError, OSError) as exc:
            print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
            return 2
        result["ledger"] = str(target)

    print(json.dumps(result, ensure_ascii=False, indent=2))

    # A claim that says it was observed but that nothing corroborates is a
    # defect, not a warning: the command fails so a caller cannot read a
    # clean exit as "everything is proven".
    if args.check and report["not_corroborated"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
