# Execution — una tarea, progreso verificable

1. Leer tarea completa y `backlog instructions task-execution`; constatar no archivada, `isReady=true` y plan vigente. Si hay otra tarea activa, evitar crear una segunda sin necesidad.
2. Antes de proponer estado In Progress, comprobar que ese estado existe en `statuses` del proyecto; y revisar `onStatusChange`, `autoCommit`, `remoteOperations`, `bypassGitHooks` antes de escribir.
3. Registrar progresos con `backlog task edit <id> --append-notes "..."` o comentarios para preguntas; nunca sobreescribir notas existentes con `--notes` por rutina.
4. Trabajo de aplicación real pertenece al agente consumidor y sus herramientas; esta skill sólo ordena el flujo y mantiene los metadatos de Backlog.md. No instalar, pushear ni ejecutar software desde el router.
5. Al detectar bloqueo, describir evidencia y el siguiente requisito; no marcar como completado por persistencia o por fatiga.

**Salida:** `estado observado | progreso | pruebas reales o NOT_RUN | próximos pasos | bloqueos`.

**Handoffs según disponibilidad:** `pure-functional-design` cuando hay una transformación arquitectónica; `pipelinek-local-ci` para pipelines locales existentes; `agent-secretless` para operaciones con credenciales; `delivery-first-testing` para garantías y tests mínimos. No se presumen herramientas instaladas. El commit del slice debe enlazar los IDs existentes de Backlog.md/roadmap/ADR/SPEC, describir implementación y verificación y pasar el [guard de Git](../repository-hygiene.md) para evitar anexar documentación privada/ZIP de planificación.

**Seguimiento Groma opcional:** cuando el CLI real esté instalado, antes de un cambio consultar `groma view <archivo>`; después de **cada archivo modificado**, conservar la lista completa de `--modified-file` en Backlog.md (no solo el último). Usar [groma-task-linking](groma-task-linking.md) para mover referencias tras combine/rename y no reescanear/curar todo el mapa por cada edición rutinaria. Los comentarios de código no llevan IDs de roadmap/tareas; esos metadatos se conservan en Backlog.md y trailers del commit.
