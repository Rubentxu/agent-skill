# CLI: guía mínima verificada contra upstream

**Fuente primaria:** [CLI-INSTRUCTIONS.md](https://github.com/MrLesk/Backlog.md/blob/main/CLI-INSTRUCTIONS.md). Consultar `backlog instructions overview`, `backlog --help` y `backlog <subcommand> --help` antes de ejecutar cambios si la instalación difiere. El prefijo de IDs y los estados son **configurables**.

| Necesidad | Comando |
|---|---|
| Instrucciones de flujo | `backlog instructions overview` |
| Listar guías | `backlog instructions` |
| Tareas estructuradas | `backlog task list --json` |
| Trabajo sin dependencias pendientes | `backlog task list --ready --json` |
| Ver tarea | `backlog task view TASK-1 --json` |
| Buscar antes de crear | `backlog search "término" --json` |
| Crear (autorizado) | `backlog task create "Título" -d "Contexto" --ac "Resultado verificable"` |
| Capturar borrador | `backlog draft create "Idea por refinar"` |
| Convertir borrador | `backlog draft promote 3.1` (usar ID real) |
| Actualizar plan | `backlog task edit TASK-1 --plan "Enfoque acotado"` |
| Añadir progreso sin borrar | `backlog task edit TASK-1 --append-notes "Evidencia concreta"` |
| Añadir pregunta | `backlog task edit TASK-1 --comment "Pregunta para revisión"` |
| Marcar AC por índice observado | `backlog task edit TASK-1 --check-ac 1` |
| Marcar DoD por índice observado | `backlog task edit TASK-1 --check-dod 1` |
| Añadir resumen final | `backlog task edit TASK-1 --final-summary "Resultado verificado"` |
| Archivar (expreso) | `backlog task archive TASK-1` |
| Diagnosticar inconsistencias | `backlog doctor` |
| Board compartible | `backlog board export` (escritura; revisar destino) |

**JSON:** `task list --json` -> `{ "schemaVersion":1, "kind":"task-list", "tasks":[...] }`; `task view <id> --json` -> `kind:"task-view",task:{...}`. `isReady` es **derivado** y se refiere al corpus visible; una dependencia archivada solo está satisfecha si su estado era final. Un ID ausente/ambiguo bloquea. `--json --watch` produce objetos completos sucesivos hasta terminación: no encadenarlo como consulta efímera sin manejo del stream.

**Multilínea:** los caracteres `\n` en argumentos son literales, no saltos reales; preferir nuevas líneas reales o uso de `--append-notes` por líneas. **Peligro:** `--notes` reemplaza, `--append-notes` añade. La CLI preserva contenido ajeno y rehúsa reemplazar secciones heredadas ambiguas sin marcadores: no sortear esa validación editando Markdown manualmente.

**No recomendadas a agentes sin control:** `backlog cleanup` requiere terminal interactivo; `backlog board`, `backlog browser` y `backlog config` sin argumentos también son interactivos; `backlog task delete` elimina definitivamente (tras archivo) y puede reescribir dependencias; `backlog doctor --fix` puede renumerar conflictos. Ninguno debe dispararse por una recomendación del router.

## Kanban CRUD comprobado contra documentación upstream

```bash
backlog task create "Título" -d "Motivación" --ac "Criterio 1" --ac "Criterio 2"
backlog task view <ID> --json
backlog task edit <ID> -s "<columna-configurada>"
backlog task archive <ID>
backlog task restore <ID>
```

Ver las guías [creación](lenses/board-create.md), [transiciones](lenses/board-transitions.md) y [archivo/restauración](lenses/board-archive-restore.md). **No se archiva de oficio cuando Done**, ni se marca Done por archivar. Archivar una tarea sin terminar deja sus dependencias bloqueadas. La restauración conserva ID y estado; la tarea archivada no puede editarse. `backlog task delete` requiere archivado previo, puede liberar IDs y actualizar enlaces de otros registros: fuera de automatizaciones.
`backlog board` es una interfaz interactiva, no un API para agentes; preferir `task list/view --json`. `backlog browser` inicia servidor local y no es necesario para CRUD. Antes de editar, leer `config get statuses` y efectos Git/callbacks. Tras cada operación, releer la tarea observada.
