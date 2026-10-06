# 01 — El bucle de revisión

## Abrir la revisión

Una revisión es el diff entre dos refs, **congelado**: guarda los sha de base, head
y merge-base en el momento de abrirla. Todo lo que viene después se evalúa contra
esos sha, nunca contra `HEAD`. Por eso el encargo es reproducible aunque la rama
avance durante la revisión.

```text
review_open(base, head, dots?)  →  abre o reanuda la revisión
```

`dots=2` compara sólo los dos commits señalados; `dots=3` (por defecto) usa el
merge-base, que es lo que se quiere al revisar una rama entera.

Si ya existe una revisión para esos refs, `review_open` la reanuda en vez de crear
un duplicado.

## Leer el encargo

**Empieza siempre por aquí.** `review_brief` es un encargo escrito para un LLM: sólo
las tareas pendientes, con el código actual de cada ancla, el código propuesto si lo
hubiera, y el criterio de aceptación de cada una. Ya descarta lo obsoleto.

```text
review_brief(format?)  →  md (por defecto) | json | github-comment
```

`format=json` es el que debes elegir si vas a processar el resultado
programáticamente; `github-comment` produce texto listo para pegar en un PR.

Para inspeccionar en crudo:

```text
review_status(health?) →  veredicto + conteos por kind y estado
notes_list(kind?, status?, file?)  →  el backlog filtrado
note_read(noteId)      →  ancla, salud, semántica, código actual y propuesto
review_diff(file?)     →  los ficheros, hunks y líneas del diff
```

`review_status` con `health=true` re-evalúa cada ancla. Es más lento y es lo
correcto antes de tocar parches: es la única forma de saber si el código se movió
desde la última vez.

## Anotar

```text
note_add(file, line, endLine?, kind, title, body?, expect?, check?, tags?)
```

El ancla se calcula del **contenido**, no del número de línea. Si pasas una línea,
`agc` toma lo que hay ahí y lo convierte en hash; si el código se desplaza después,
la nota lo sigue.

Ancla un rango cuando el defecto abarque varias líneas consecutivas: `endLine` lo
cubre en un solo hash.

Dos campos que se subestiman y valen mucho:

- `expect` — el criterio de aceptación en una frase. Es lo que cierra la nota.
- `check` — el comando que demuestra que está hecha (`--check "pnpm test"`).

```text
note_update(noteId, status?, body?, expect?, suggestion?, check?, tags?)
```

## Reglas del anotado

1. **Un defecto, una nota.** Dos problemas en el mismo bloque son dos notas: se
   cierran por separado y tienen estados distintos.
2. **El `title` dice qué está mal, no dónde.** El motor ya sabe dónde: lo pone en el
   gutter. `✖ no valida expiración` funciona; `línea 42` no.
3. **No anotes en binarios ni en ficheros fuera del diff.** El motor no puede
   anclar ahí y la nota quedaría obsoleta al instante.
4. **`question` es una stopper.** Si abres una pregunta, no sigas anotando como si
   la respuesta fuera evidente: vuelve a ella.

## Cuándo parar de anotar

El bucle de `note_add` es infinito si no hay tope. Para cuando:

- has revisado todos los ficheros del diff, o has justificado los que no;
- cada `blocker` tiene `expect` y (si es automatizable) `check`;
- `review_brief` ya no devuelve tareas nuevas que no sean respuesta a las tuyas.

Nada de esto te autoriza a arreglar nada todavía: anotar y parchear son modos
distintos. Ver [`03-patch-engine.md`](03-patch-engine.md).