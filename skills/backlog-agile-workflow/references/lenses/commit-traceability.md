# Lente: compromisos y referencias entre backlog, roadmap, ADR y Git

**Cuándo:** antes de seleccionar tareas, al generar un plan desde especificaciones, al hacer commit o antes de cerrar un hito.

1. Leer [contrato](../commit-traceability.md) y obtener identificadores exactos del documento **privado** y de la tarea Backlog.md. Los IDs son estables, las rutas locales no son enlaces públicos.
2. Revisar Backlog.md y la historia de commits por IDs, no solo títulos. No duplicar tareas cuando hay progreso previo o implementación parcial.
3. Componer commit con `Backlog-Task:`, `Roadmap-Block:`, `Spec-Ref:`, `ADR-Ref:`, `Implementation:` y `Verification:` (solo los IDs existentes; no inventar ADR).
4. `scripts/commit_trace.py` indexa mensajes **curados** para proponer revisión antes de importar tareas; si no hay commit inspeccionado, ausencia no significa no implementado.
5. Tras merge, registrar en Backlog.md el SHA y el estado observado; verificar AC/DoD y recibos antes de marcar Done. No poner `PASS` cuando no se ejecutó un gate.

**Salida:** `TASK ID | documental IDs | commit SHAs | cambio implementado | evidencia | faltantes/contradicciones`.
