# Triage — decidir el siguiente trabajo sin falsos listos

1. Leer `backlog task list --json`; comprobar sobre JSON real `schemaVersion == 1` y `kind == task-list`. Filtrar `archived=false`, `isReady=true` y estados no finales **según configuración**; `task list --ready --json` es alternativa.
2. Priorizar por valor observable, riesgo de bloqueo y coste incremental; respetar prioridad/ordinal configurados, no inventar scoring ni estimación ficticia. Elegir WIP=1 como valor inicial, no como política irrebatible.
3. Si `isReady` falta o depende de `unknown/ambiguous`, detenerse y pedir datos. Archivado no equivale a completado; dependencias archivadas solo satisfacen si están en estado final.
4. Inspeccionar `task view <id> --json` y su `dependencyGraph` para comprender todos los bloqueos; no crear ciclos.
5. Para demasiadas tareas abiertas: proponer dividir/repriorizar, mantener un backlog corto, mover ideas inciertas a borradores. Cambios sujetos a autorización.

**Anti-patrón:** seleccionar el primer `High` aunque esté bloqueado, en lugar de la tarea que realmente puede entregarse. **Salida:** tarea priorizada y por qué, obstáculos, pregunta pendiente o `KEEP_AS_IS`.
