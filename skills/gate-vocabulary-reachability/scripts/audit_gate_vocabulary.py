#!/usr/bin/env python3
"""Audita la alcanzabilidad de un vocabulario de puerta declarado en un enum.

Extrae las variantes de un `enum` que un motor de políticas consume, y clasifica
cuáles son construibles desde código de producción y cuáles sólo existen en el
mapa de nombres, en las reglas o en tests.

    python3 audit_gate_vocabulary.py --enum src/domain.rs --enum-name Action
    python3 audit_gate_vocabulary.py --enum src/domain.rs --enum-name Action \\
        --map-fn src/policy.rs --skip-paths tests --skip-paths __cfg_test__

No adivina: el enum es la fuente de verdad, y `--check` compara el total
encontrado con `--expect-total` para que un inventario incompleto no pase
desapercibido.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Un `Variant,` o `Variant {` o `Variant(...)` al inicio de línea, dentro del
# cuerpo del enum. Exige que la línea esté sangrada y que no sea una etiqueta de
# variante con atributo encima (los atributos se permiten y se saltan).
VARIANT = re.compile(r"^\s{4}([A-Z][A-Za-z0-9_]*)\s*(?:,|\{|\()", re.M)
# Líneas que no son variantes: comentarios, atributos, `impl`, `pub`.
NOISE = re.compile(r"^\s*(//|///|//!|#\[|pub |impl |where |for )")


def extract_variants(path: Path, enum_name: str) -> tuple[list[str], int]:
    """Devuelve (variantes, línea donde empieza el enum)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(rf"pub enum {re.escape(enum_name)}\s*\{{", text)
    if not m:
        raise SystemExit(f"no se encuentra `pub enum {enum_name}` en {path}")
    # El enum termina en la primera llave de cierre a columna 0.
    end = text.find("\n}", m.end())
    if end == -1:
        raise SystemExit(f"no se encuentra el cierre de `{enum_name}` en {path}")
    body = text[m.end() : end]
    variants: list[str] = []
    for line in body.splitlines():
        if NOISE.match(line):
            continue
        hit = VARIANT.match(line)
        if hit:
            name = hit.group(1)
            if name not in variants:
                variants.append(name)
    return variants, text[:m.end()].count("\n") + 1


def production_files(root: Path, skip: list[str]) -> list[Path]:
    out: list[Path] = []
    for path in root.rglob("*.rs"):
        rel = str(path.relative_to(root))
        if any(s in rel for s in skip):
            continue
        out.append(path)
    return out


def strip_test_modules(text: str) -> str:
    """Blank out `#[cfg(test)] mod ... { ... }` bodies, brace-counted.

    Necessary and not optional: an inline test module in `src/` is full of
    `Action::Foo` references, and counting those as production turns every dead
    verb into a live one. That is the worst possible direction for this tool —
    it would report a clean audit over the exact defect it exists to find.

    Blanked rather than deleted so line numbers in the report stay true to the
    file the reader will open.

    KNOWN LIMITATION, and it is load-bearing: this counts braces, so a `{` or a
    `}` inside a string literal desynchronises it. A `format!("{x}")` in a test
    can leave the rest of the module unblanked. Rather than pretend otherwise,
    every reported hit carries the name of its enclosing function, so a hit
    inside a test says so on its face. **A "VIVO" line whose function name starts
    with `test_`, or that lives in a `mod tests`, is a test, not production** —
    re-read it before believing the report.
    """
    out = list(text)
    for m in re.finditer(r"#\[\s*cfg\s*\(\s*test\s*\)\s*\](?:\s*#\[[^\]]*\])*\s*mod\s+\w+", text):
        i = text.find("{", m.end())
        if i == -1:
            continue
        depth = 0
        j = i
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        for k in range(m.start(), min(j + 1, len(out))):
            if out[k] != "\n":
                out[k] = " "
    return "".join(out)


def enclosing_fn(lines: list[str], index: int) -> str:
    """El nombre de la función o módulo que envuelve la línea `index`.

    Lo que hace que un informe de este script sea auditable sin abrir el
    fichero: un hit dentro de un test se lee como un hit dentro de un test.
    """
    for i in range(index, -1, -1):
        m = re.match(r"\s*(?:pub\s+)?(?:async\s+)?fn\s+(\w+)", lines[i])
        if m:
            return f"fn {m.group(1)}"
        m = re.match(r"\s*mod\s+(\w+)", lines[i])
        if m:
            return f"mod {m.group(1)}"
    return "fuera de fn"


def constructed(
    variant: str, enum_name: str, files: list[Path], map_fn: str | None, root: Path
) -> list[str]:
    """Ficheros de producción que CONSTRUYEN la variante, no la nombran.

    Busca el **tipo cualificado** (`Action::Foo`), nunca el nombre suelto. Es la
    diferencia entre una auditoría y una mentira: `PostgresConnect` existe
    como variante del enum de *peticiones* y como variante de *acciones*, y
    buscar el literal marca como "construida" una acción que ningún punto de
    evaluación nombra jamás.

    Tampoco cuenta la declaración del propio enum: la variante aparece allí por
    definición, y contarla convertiría el inventario en un todos-verdes.

    Y el mapa de nombres se excluye, porque es exhaustivo por diseño: ahí
    sobreviven las variantes muertas sin previo aviso.
    """
    hits: list[str] = []
    # `Action::Foo`, cualificado. El límite de palabra evita que `Foo` case con
    # `Foobar`.
    needle = re.compile(rf"\b{re.escape(enum_name)}::\s*{re.escape(variant)}\b")
    for path in files:
        if map_fn and map_fn in str(path.relative_to(root)) and path.name == map_fn:
            continue
        text = strip_test_modules(path.read_text(encoding="utf-8", errors="replace"))
        lines = text.splitlines()
        for n, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            # El brazo del mapa de nombres: `Foo => "foo",`. Es exhaustivo por
            # diseño, así que contiene todas las variantes Included las muertas.
            if re.match(rf"(?:\w+::)*{re.escape(variant)}\s*=>", stripped):
                continue
            if needle.search(line):
                hits.append(f"{path.relative_to(root)}:{n} ({enclosing_fn(lines, n - 1)})")
                break
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path("."), help="raíz del repositorio")
    ap.add_argument("--enum", type=Path, required=True, help="fichero con el enum")
    ap.add_argument("--enum-name", required=True, help="nombre del enum")
    ap.add_argument("--map-fn", default=None, help="fichero con el match que mapea a nombres (se excluye)")
    ap.add_argument(
        "--skip-paths",
        action="append",
        default=[],
        dest="skip",
        metavar="SUBSTR",
        help="subcadena de ruta a excluir; repetible. Por defecto: tests y __cfg_test__",
    )
    ap.add_argument("--expect-total", type=int, default=None, help="total esperado; falla si no cuadra")
    args = ap.parse_args()

    skip = list(args.skip) or ["tests", "__cfg_test__"]
    root = args.root.resolve()
    enum_path = args.enum if args.enum.is_absolute() else root / args.enum

    variants, line = extract_variants(enum_path, args.enum_name)
    files = production_files(root, skip)

    if args.expect_total is not None and args.expect_total != len(variants):
        print(
            f"INVENTARIO INCOMPLETO: {args.enum_name} tiene {len(variants)} variantes, "
            f"esperabas {args.expect_total}. Rehaz el inventario antes de concluir.",
            file=sys.stderr,
        )
        return 2

    print(f"#{args.enum_name} declarado en {enum_path.relative_to(root)}:{line}")
    print(f"#{len(variants)} variantes · {len(files)} ficheros de producción considerada\n")

    dead: list[str] = []
    live = 0
    for variant in variants:
        hits = constructed(variant, args.enum_name, files, args.map_fn, root)
        if hits:
            live += 1
            print(f"  VIVO    {variant:34} {', '.join(hits[:2])}")
        else:
            dead.append(variant)
            print(f"  INERTE  {variant:34} (ninguna construcción en producción)")

    print(f"\nresumen: {live}/{len(variants)} construidas, {len(dead)} inertes")
    if dead:
        print("\nPara cada INERTE, contesta antes de calificarlo:")
        print("  1. ¿se construye en otro crate, dinámicamente, o como parámetro?")
        print("  2. ¿el default concede? entonces es un FALSO CONTROL, no deuda")
        print("  3. ¿qué podría hacer un atacante que hoy no puede?")
    return 1 if dead else 0


if __name__ == "__main__":
    raise SystemExit(main())
