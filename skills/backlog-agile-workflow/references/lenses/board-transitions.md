# Kanban: transiciones de estado por CLI

1. Leer `backlog config get statuses` y `backlog config get defaultStatus`; el estado terminal se determina por política del proyecto, **no** por texto "Done" supuesto. Inspeccionar `backlog task view <ID> --json`, `readiness` y `archived`. Releer inmediatamente antes de escribir: puede haber ediciones concurrentes del Web UI/agentes.
2. **Iniciar tarea:** `isReady=true`, dependencias resueltas, WIP razonable; usar `backlog task edit <ID> -s "<estado-activo-configurado>"`. `backlog instructions task-execution` dirige planificación y registro de progreso.
3. **Progreso entre columnas:** solo según estado real, nunca para mejorar métricas de tablero. Las columnas del proyecto pueden tener nombres personalizados. Cambiar columna no comprueba AC/DoD.
4. **Finalizar:** `backlog instructions task-finalization`, verificar individualmente AC/DoD/gates reales, registrar `--final-summary` y después `backlog task edit <ID> -s "<estado-final-configurado>"`. No inferir PASS de existencia de commit o tests sin ejecutar.
5. **Reabrir:** preservar historia/IDs; justificar por qué el final ya no es válido, revisar las dependencias y volver a un estado configurado. Revalidar gates que lo necesiten.
6. Antes de cada cambio, revisar `onStatusChange` (puede ejecutar shell) y `autoCommit`, `remoteOperations`, `bypassGitHooks`. No tratar la transición como un cambio libre de efectos. La ayuda del CLI instalado prevalece.
7. Reconsultar `task view --json` y `task list --json` después de escribir. Error, estado sin cambios o snapshot antiguo ≠ transición conseguida.

**Propuestas automáticas:** `scripts/board_crud.py` comprueba configuraciones, readiness, estado de archivo, objetivo configurado y evidencia de finalización. Nunca modifica tareas. 
