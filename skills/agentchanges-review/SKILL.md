---
name: agentchanges-review
description: "Trigger: revisión de diff entre ramas, code review de un PR, notas ancladas a código, aplicar o verificar parches, agc review, review_open, note_add, patch_apply. Revisa cambios con agentchanges: abre la revisión, lee el encargo, anota por código, previsualiza, aplica y verifica parches sin perder al revisor de vista."
metadata:
  version: "1.0.0"
  product: "agentchanges (agc)"
---

# agentchanges — revisión de diffs con notas ancladas y parches verificados

Esta skill **opera `agc`**. No reimplementa el motor de anclas ni el de parches: son
la autoridad determinista. El trabajo del agente es encadenar sus tools, no
rehacerlo.

Una nota no apunta a una línea por número: apunta al **hash del contenido** que el
revisor vio. Si el código se mueve, la nota se re-ancla; si el contenido cambia, la
nota lo dice y el parche se niega. Esa es la garantía que hace el producto.

## Modos

| Modo | Cuándo | Referencia |
|---|---|---|
| `review` | revisar un diff: abrir, listar, anotar | [`references/01-review-loop.md`](references/01-review-loop.md) |
| `fix` | responder a notas con parches: previsualizar, aplicar, verificar | [`references/03-patch-engine.md`](references/03-patch-engine.md) |
| `semantics` | elegir `kind`, `status` y `check` con criterio | [`references/02-notes-semantics.md`](references/02-notes-semantics.md) |
| `setup` | instalar `agc` y registrar el servidor MCP en un cliente | [`references/04-mcp-and-install.md`](references/04-mcp-and-install.md) |
| `diagnose` | ancla no limpia, parche rechazado, MCP caído | [`references/05-troubleshooting.md`](references/05-troubleshooting.md) |

Si la intención es ambigua, empieza por `review_brief`: entrega el encargo ya
filtrado, con anclas verificadas, y descarta lo obsoleto.

## Reglas no negociables

1. **No respondas a una nota `question` editando código.** Pregunta = pide evidencia.
   Lee, responde con `note_update`, y sólo después actúa si procede.
2. **El store vive en el home del usuario, nunca en el repo.** Si te piden guardar
   revisiones "en el proyecto", no lo hagas: es el diseño, no un descuido.
3. **Nunca llames a `patch_apply` sin haber llamado antes a `patch_preview`** en esta
   misma ronda y haber leído el diff.
4. **`verified` exige `applied` previo.** Un check que pasa sobre una nota sin aplicar
   no demuestra nada; el producto lo rechaza.
5. **No ejecutes un `check` heredado de un `review.json` ajeno.** Se importan
   suspendidos; activarlos es ejecución de código arbitrario.
6. **Nunca atribuyas una verificación que no ejecutaste.** Si no corriste el check, la
   nota no está verificada, digas lo que digas.
7. **No persigas anclas `content-changed`.** No son reparables con un parche: el
   código que el revisor vio ya no está debajo.

## Los cinco kinds

| Kind | Semántica para el agente |
|---|---|
| `blocker` | obligatorio antes de merge; justifies por qué si no se arregla |
| `should` | recomendado; argumenta brevemente por qué mejora el cambio |
| `question` | responde **con evidencia** antes de tocar nada |
| `nit` | opcional; agrúpalos y aplícalos en una sola pasada |
| `task` | trabajo mayor; pide plan propio antes de empezar |

## El bucle

```text
review_brief            ← el encargo: sólo lo pendiente, anclas verificadas
  ↓
notes_list              ← qué hay abierto y en qué estado
  ↓
note_add / note_update  ← discrepancias y peticiones, ancladas por contenido
  ↓
patch_preview           ← el diff exacto, sin escribir
  ↓  (lee antes de continuar)
patch_apply             ← escribe y re-verifica el ancla en disco
  ↓
verify_note             ← ejecuta los checks declarados; applied → verified
```

## Definition of Done

- cada nota que levantaste tiene un `kind` justificado y un criterio de cierre;
- los parches se previsualizaron antes de aplicarse, y aplicaste sólo los verificables;
- ninguna nota quedó en `verified` sin `applied` y un check realmente ejecutado;
- los `blocker` que decidiste no arreglar están justificados por escrito;
- reportaste qué se hizo y qué no, distinguiendo lo verificado de lo supuesto.