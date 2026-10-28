# Kanban: crear tarjeta con CLI real

1. Descubrir proyecto y configuraciones: `backlog instructions overview`, `backlog instructions task-creation`, `backlog config get statuses`, `defaultStatus`, `priorities`, `projects`, `definition_of_done`, `autoCommit`, `remoteOperations`, `onStatusChange` y `bypassGitHooks`.
2. Buscar antes de crear: `backlog search "consulta" --json`, `backlog task list --json`, y revisar coincidencias, borradores, archivados y las referencias de ROADMAP/ADR/SPEC/commits. La lista activa **no** es un inventario de archivados o ramas: no concluir unicidad sin inspección. Una idea vaga → `backlog draft create "Título"`; una tarea lista → `backlog task create "Resultado" -d "Problema y por qué" --ac "Resultado verificable"`.
3. Añadir cada criterio por `--ac` repetido. `--ref` para IDs existentes de documentos de gestión o componentes Groma y `--doc` para documentos existentes. `--priority`, `-s`, `--project`, `--dep` solo con valores e IDs observados; los defaults configurados de DoD se aplican solos. No inventar due dates ni asignación. Crear no implica empezar; el plan se redacta **justo antes de ejecutar** (salvo trabajo que ya estaba iniciado).
4. Si se pide acción no interactiva, `scripts/board_crud.py` proporciona argumentos estructurados, nunca los ejecuta. Controlar permiso y efectos Git/callbacks antes de pasar de propuesta a escritura.
5. Tras ejecutar, capturar ID real devuelto por la CLI y consultar `backlog task view <ID> --json`, confirmar `status`, AC y refs, y constatar presencia en el board. No deducir IDs por ordinal.

**No:** abrir duplicados por cambios de título, rellenar plan prematuro, tocar Markdown Backlog.md directamente. **Salida:** ID real, estado/configuración, criterios, bloque roadmap, evidencia de creación. 
