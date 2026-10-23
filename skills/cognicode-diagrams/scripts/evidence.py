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
publish the verdict with it and not only the claim. The derived verdict
carries the digests of the files it read, so whoever reads it can tell
whether it speaks about the material in front of them.

Never reads the checkout: it only reads the derived workspace under HOME.
"""
from __future__ import annotations

import argparse
import hashlib
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
CLAIMS_PATH = "evidence/claims.json"
QUERIES_PATH = "evidence/queries.json"


class EvidenceError(ValueError):
    """The workspace or its ledger cannot be read."""


def _no_symlinks(path: Path) -> None:
    for component in (path, *path.parents):
        if component.is_symlink():
            raise EvidenceError(f"ruta con enlace simbolico: {component}")


def _load_bytes(path: Path) -> bytes:
    """Read a ledger file as bytes, so its digest can travel with it."""
    if not path.is_file():
        raise EvidenceError(f"no existe el fichero de evidencia: {path}")
    if path.stat().st_size > MAX_INPUT:
        raise EvidenceError(f"el fichero de evidencia es demasiado grande: {path}")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise EvidenceError(f"no se pudo leer {path}: {exc}") from exc


def _load(path: Path) -> object:
    raw = _load_bytes(path)
    try:
        return json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
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


def examine(workspace_dir: Path) -> tuple[dict, dict[str, str]]:
    """Read the ledger and report what every claim earns.

    The digests of the files that were read travel with the report: a
    verdict that does not say which material it came from cannot be
    matched against the material in front of the reader.
    """
    _no_symlinks(workspace_dir)
    evidence = workspace_dir / "evidence"
    claims_path = evidence / "claims.json"
    queries_path = evidence / "queries.json"
    claims_raw = _load_bytes(claims_path)
    queries_raw = _load_bytes(queries_path)
    try:
        report = contract.report(json.loads(claims_raw.decode("utf-8")),
                                  json.loads(queries_raw.decode("utf-8")))
    except (ValueError, UnicodeError) as exc:
        raise EvidenceError(f"el ledger no se pudo interpretar: {exc}") from exc
    inputs = {
        CLAIMS_PATH: hashlib.sha256(claims_raw).hexdigest(),
        QUERIES_PATH: hashlib.sha256(queries_raw).hexdigest(),
    }
    return report, inputs


def ledger(workspace_dir: Path, report: dict, inputs: dict[str, str]) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "generator": GENERATOR,
        "workspace": str(workspace_dir),
        "status": report["status"],
        "gaps": report["gaps"],
        "inputs": inputs,
        "claims": report["claims"],
        "counts": {
            "corroborated": report["corroborated"],
            "observed_not_corroborated": report["not_corroborated"],
            "not_checkable": report["not_checkable"],
            "not_implementation": report["not_implementation"],
        },
    }


def estado_del_informe(report: dict) -> str:
    """La palabra que resume lo que el material es.

    Un material que este contrato no puede leer no es un hallazgo: es un
    hueco. Una afirmacion que nadie ha podido mirar tampoco: nadie ha
    mirado. Solo una afirmacion que se ha mirado y no queda sostenida es
    un hallazgo, y es el unico que lo dice.

    Cuando hay hueco y hallazgo a la vez, manda el hueco: decir «tus
    afirmaciones no estan corroboradas» cuando lo que pasas es que no se
    las ha podido mirar es una acusacion falsa. Los recuentos cuentan las
    dos cosas, asi que nada se esconde.
    """
    if report["status"] != "current":
        return "UNREADABLE"
    if report["not_checkable"]:
        return "NOT_CHECKABLE"
    if report["not_corroborated"]:
        return "NOT_CORROBORATED"
    return "OK"


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
        report, inputs = examine(workspace_dir)
    except (ws.WorkspaceError, EvidenceError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2

    estado = estado_del_informe(report)
    result = {
        "status": estado,
        "workspace": str(workspace_dir),
        "gaps": report["gaps"],
        "inputs": inputs,
        "counts": {
            "corroborated": report["corroborated"],
            "observed_not_corroborated": report["not_corroborated"],
            "not_checkable": report["not_checkable"],
            "not_implementation": report["not_implementation"],
        },
        "claims": report["claims"],
    }

    if args.emit:
        target = workspace_dir / "evidence" / LEDGER_NAME
        try:
            _write_owned(target, json.dumps(ledger(workspace_dir, report, inputs), ensure_ascii=False,
                                            sort_keys=True, indent=2) + "\n")
        except (EvidenceError, OSError) as exc:
            print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
            return 2
        result["ledger"] = str(target)

    print(json.dumps(result, ensure_ascii=False, indent=2))

    # A claim that says it was observed but that nothing corroborates is a
    # defect, not a warning: the command fails so a caller cannot read a
    # clean exit as "everything is proven". A claim the material does not
    # let anyone look at is a defect too, and of another kind: it is not
    # proven either, and the exit has to say so.
    if args.check and (report["not_corroborated"] or report["not_checkable"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
