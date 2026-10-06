# 02 — Semántica de las notas

## kinds

El `kind` no es una etiqueta de estilo: define qué se espera de ti y qué la hace
cerrable.

| Kind | Cuándo | Qué se espera del agente | Cómo se cierra |
|---|---|---|---|
| `blocker` | el cambio no es aceptable tal cual | arreglarlo, o justificar por escrito por qué no | `patch_apply` + `verify_note` |
| `should` | es mejor así, pero no bloquea | argumentar por qué mejora el cambio | parche o respuesta razonada |
| `question` | no entiendes algo del diff | **responder con evidencia** | `note_update` con la respuesta |
| `nit` | detalle menor | agruparlos y aplicarlos en una pasada | parche |
| `task` | trabajo mayor que el diff | pedir plan propio antes de empezar | fuera del ciclo de parches |

Dos errores caros aquí:

- **Marcar algo como `blocker` para que no se te discuta.** Un `blocker` que no
  describes bien es ruido que el equipo tiene que kindar hacia abajo. Si dudas entre
  `blocker` y `should`, casi siempre es `should`.
- **Usar `nit` para no pensar.** Un `nit` sobre un fallo de seguridad es un
  `blocker` disfrazado de cortesía.

## Los siete estados

```text
open        ──▶ in_progress ──▶ applied ──▶ verified
   │               │              │           │
   │               │              └───────────┴──▶ obsolete
   └───────────────┴──────────────────────────────▶ rejected | wontfix
```

| Estado | Significado | Quién lo pone |
|---|---|---|
| `open` | abierta, sin tocar | `note_add` |
| `in_progress` | alguien está trabajando en ella | tú o el humano |
| `applied` | el parche está escrito en disco | `patch_apply` |
| `verified` | el check pasó **sobre lo aplicado** | `verify_note` |
| `wontfix` | se decidió no hacerlo, con motivo | humano, con tu `reason` |
| `rejected` | el código propuesto no vale | humano o tú, con motivo |
| `obsolete` | el código que señalaba ya no existe | el motor, no tú |

Dos movimientos que parecen libres y no lo son:

- **`obsolete` no lo pones tú.** Es el veredicto del motor cuando el ancla ya no
  existe en el ref. Si crees que una nota es obsoleta, es que el ancla está mal.
- **`verified` sin `applied` es imposible a propósito.** Un check que pasa sobre
  código que nadie ha cambiado no demuestra nada. El motor lo rechaza.

## Salud del ancla

Al reevaluar, cada nota queda en una de cuatro:

| Salud | Significado | ¿Parcheable? |
|---|---|---|
| `valid` | el contenido sigue byte a byte donde estaba | sí |
| `moved` | se movió de sitio, el contenido es el mismo | sí |
| `content-changed` | las líneas cambió | **no** |
| `obsolete` | ya no hay nada que se parezca al código anotado | no, y no hay nada que recuperar |

`content-changed` es el caso que más engaña: el código "parece el mismo" pero no lo
es. No lo persigas. Reancla la nota sobre el código que sí está y decide de nuevo.

## checks

```text
check: { command, status }
```

`status` es `pending` cuando se crea y pasa a `verified` al ejecutarse. El comando
se ejecuta **en el repo**, con el shell del sistema.

Reglas al declararlo:

1. **Prueba el comando antes de declararlo.** Un check que no arranca deja la nota
   perpetuamente en `applied`.
2. Que sea **específico y rápido**. `pnpm test` sobre un monorepo entero tarda
   minutos y agota el tiempo del motor.
3. Que **verifique la nota**, no "que compile". Un `tsc --noEmit` verde no
   demuestra que la expiración se comprueba.
4. Los checks importados de otra persona llegan **suspendidos**: son comandos de
   shell arbitrarios. No los actives sin leerlos. Ver
   [`04-mcp-and-install.md`](04-mcp-and-install.md).