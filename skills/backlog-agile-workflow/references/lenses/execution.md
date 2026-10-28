# Execution — una tarea, progreso verificable

1. Leer tarea completa y `backlog instructions task-execution`; constatar no archivada, `isReady=true` y plan vigente. Si hay otra tarea activa, evitar crear una segunda sin necesidad.
2. Antes de proponer estado In Progress, comprobar que ese estado existe en `statuses` del proyecto; y revisar `onStatusChange`, `autoCommit`, `remoteOperations`, `bypassGitHooks` antes de escribir.
3. Registrar progresos con `backlog task edit <id> --append-notes "..."` o comentarios para preguntas; nunca sobreescribir notas existentes con `--notes` por rutina.
4. Trabajo de aplicación real pertenece al agente consumidor y sus herramientas; esta skill sólo ordena el flujo y mantiene los metadatos de Backlog.md. No instalar, pushear ni ejecutar software desde el router.
5. Al detectar bloqueo, describir evidencia y el siguiente requisito; no marcar como completado por persistencia o por fatiga.

**Salida:** `estado observado | progreso | pruebas reales o NOT_RUN | próximos pasos | bloqueos`.
