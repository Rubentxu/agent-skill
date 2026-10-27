#!/usr/bin/env python3
"""Contratación de la selección curada para vistas C4, sin leer el checkout.

Este módulo valida un artefacto ya derivado bajo HOME; no selecciona
afirmaciones, no inventa relaciones y no dibuja vistas.
"""
from __future__ import annotations

import json
from pathlib import Path

VIEW_GENERATOR = "cognicode-diagrams-c4-view"
MAX_CLAIMS = 128
MAX_LABEL = 200
MAX_BYTES = 128 * 1024


class SelectionError(ValueError):
    """Selección inexistente, insegura o mal formada."""


def load(path: Path) -> dict:
    """Leer y validar una selección sin aceptar enlaces simbólicos.

    La semántica de clases y preguntas C4 pertenece al proyector c4_view;
    aquí se validan las invariantes compartidas del documento de selección.
    """
    path = Path(path)
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise SelectionError("enlace simbólico en la ruta de selección")
    try:
        if not path.is_file() or path.stat().st_size > MAX_BYTES:
            raise SelectionError("selección ausente o demasiado grande")
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SelectionError("no se pudo leer la selección JSON") from exc
    if not isinstance(data, dict):
        raise SelectionError("la selección debe ser un objeto")
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise SelectionError("versión de selección no admitida")
    for field in ("lens", "question"):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip() or len(value) > MAX_LABEL:
            raise SelectionError(f"campo {field} inválido")
    label = data.get("label")
    if not isinstance(label, str) or not label.strip() or len(label) > MAX_LABEL:
        raise SelectionError("etiqueta ausente o excesiva")
    ids = data.get("claim_ids")
    if (not isinstance(ids, list) or not 1 <= len(ids) <= MAX_CLAIMS
            or any(not isinstance(cid, str) or not cid.strip() or len(cid) > MAX_LABEL
                   for cid in ids)
            or len(ids) != len(set(ids))):
        raise SelectionError("claim_ids ausentes, duplicados o inválidos")
    if not isinstance(data.get("kinds"), dict):
        raise SelectionError("kinds debe ser un objeto")
    return data
