# 03 — El motor de parches

## La idea

El motor de anclas evalúa las notas contra **refs de git**, porque eso sobrevive a
un rebase. Pero un parche se escribe en el **working tree**, y ahí hay un hueco que
el motor cruza explícitamente: antes de escribir, comprueba con `git hash-object`
que las líneas a sustituir siguen siendo, byte a byte, las que el revisor vio.

Ese es el motivo de que el parche se niegue cuando el ancla no es `valid` o
`moved`, **por mucho que el código "parezca el mismo"**: si no puedes demostrar qué
hay debajo, no puedes demostrar qué estás cambiando.

## El orden correcto

```text
note_update(noteId, suggestion=<código completo de la línea o rango>)
  ↓
patch_preview(ids?)     ← lee el diff. SIEMPRE.
  ↓
patch_apply(ids?)       ← escribe; cada parche se re-verifica justo antes
  ↓
verify_note(ids?)       ← ejecuta los checks; applied → verified
```

**Regla dura: no apliques nada que no hayas previsualizado en esta ronda.** El
preview no escribe, y es la única forma de ver el diff con la sustitución ya
resuelta en vez de imaginarla.

## Escribir la sugerencia

La `suggestion` **reemplaza el rango anclado**, no se inserta ni se fusiona. En la
práctica eso significa enviar la línea completa tal como debe quedar:

```text
mal:     const session = createSession(claims)
bien:    const session = createSession(claims, { audit: true })
```

Omitir la indentación hace que la primera línea quede al nivel de columna 0. La
sugerencia se limpia, pero **respeta la sangría que le des**: manda la del código
que la rodea.

Para un rango de varias líneas, envía todas, con `\n` entre ellas y la sangría de
cada una.

## Qué devuelve el preview

El preview es un diff unificado real, con `@@` y `+`/`−`, y dice qué haría:

- cuántas notas son aplicables y cuántas no;
- el motivo de cada rechazo;
- si el parche es de un solo fichero.

Si algo aparece como **NO APLICADO**, lee el motivo antes de nada más. No es un
fallo del motor: es la información que te faltaba.

## Rechazos y qué hacer

| Motivo | Qué hacer |
|---|---|
| ancla `content-changed` | **no lo fuerces**. Reancla sobre el código actual y decide de nuevo |
| ancla `obsolete` | la nota ya no aplica; márcala `obsolete` con `note_update` |
| sin `suggestion` | adjúntala primero; `patch_apply` no inventa código |
| parche ya aplicado | no es un error; comprueba el estado de la nota |

## Verificar

```text
verify_note(ids?)  →  ejecuta el check de cada nota applied
```

- Sin `check` declarado: no hay nada que ejecutar y la herramienta lo dice. No lo
  conviertas en `verified` a mano.
- Con `check`: se ejecuta en el repo con un tiempo máximo por defecto de 120 s.
  Si se pasa, `applied` → `verified`. Si falla, la nota se queda en `applied` y el
  fallo se reporta.
- `verify_note` **no aplica nada**. Si te pide verificar antes de aplicar, estás
  saltándote el paso de `patch_apply`.

## Acciones manuales

```text
patch_apply(dryRun=true, failIfAny=true)  ← si tu cliente lo expone
```

El CLI equivalente es `agc apply [ids...] [--dry-run] [--fail-if-any]` y
`agc verify [ids...] [--all] [--force] [--fail-if-any]`. Es el mismo motor: la
tool, el botón de la GUI y el comando ejecutan literalmente el mismo código.