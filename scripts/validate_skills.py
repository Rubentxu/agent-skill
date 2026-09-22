#!/usr/bin/env python3
"""Valida la estructura mínima y referencias relativas de todas las skills.

No instala herramientas, no ejecuta código de las skills, ni requiere dependencias.
No es un parser YAML completo: comprueba solo los campos obligatorios simples.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
LOCAL_LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)]+)\)")
EXCLUDED = {"http://", "https://", "mailto:", "#"}


def validate_skill(skill: Path) -> list[str]:
    errors: list[str] = []
    root = skill.resolve()
    if not SLUG.fullmatch(skill.name):
        errors.append(f"{skill}: el nombre debe ser un slug kebab-case")
    entry = skill / "SKILL.md"
    if not entry.is_file():
        return [f"{skill}: falta SKILL.md"]
    body = entry.read_text(encoding="utf-8")
    front = re.match(r"\A---\s*\n(.*?)\n---\s*\n", body, re.S)
    if not front:
        errors.append(f"{entry}: falta front matter YAML")
    else:
        meta = front.group(1)
        name = re.search(r"^name:\s*['\"]?([a-z0-9-]+)['\"]?\s*$", meta, re.M)
        desc = re.search(r"^description:\s*(\S.*)$", meta, re.M)
        if not name or name.group(1) != skill.name:
            errors.append(f"{entry}: name debe coincidir con {skill.name}")
        if not desc or not desc.group(1).strip("'\" "):
            errors.append(f"{entry}: description no puede estar vacía")
    for file in sorted(skill.rglob("*.md")):
        if file.is_symlink():
            errors.append(f"{file}: no se admiten enlaces simbólicos")
            continue
        for target in LOCAL_LINK.findall(file.read_text(encoding="utf-8")):
            target = target.strip().split("#", 1)[0].split("?", 1)[0]
            if not target or any(target.startswith(prefix) for prefix in EXCLUDED):
                continue
            if target.startswith(("/", "~")):
                errors.append(f"{file}: enlace local absoluto: {target}")
                continue
            resolved = (file.parent / target).resolve()
            if not resolved.is_relative_to(root) or not resolved.exists():
                errors.append(f"{file}: enlace local roto o externo a la skill: {target}")
    return errors


def main() -> int:
    skills = sorted(s for s in SKILLS.iterdir() if s.is_dir()) if SKILLS.is_dir() else []
    if not skills:
        print("ERROR: no hay skills en skills/")
        return 1
    errors = [e for s in skills for e in validate_skill(s)]
    for error in errors:
        print("ERROR:", error)
    if errors:
        return 1
    print(f"OK: {len(skills)} skill(s) con manifiestos y enlaces locales comprobados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
