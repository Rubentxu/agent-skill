# Eventos y recomendaciones: contrato cross-agent

`plugins/backlog-context` es un **adaptador opt-in** de Claude Code. La skill continúa siendo la autoridad de instrucciones reutilizable por agentes sin hooks.

- **SessionStart:** si existe proyecto Backlog, aconsejar consultar tareas. Un ID activo solo procede de `BACKLOG_CONTEXT_TASK_ID` explícito; no inferirlo del último commit.
- **PostToolBatch/Read:** archivos consultados son oportunidades de `groma view <ruta>`, lectura sin escaneo ni edición. El hook extrae IDs de propietario, no incluye descripciones libres ni código. Un proyecto Groma moderno se reconoce por `project.md` e `index.md`, no por `config.json`; si no hay owner, indicar cobertura desconocida.
- **PostToolUse/Edit|Write:** registrar ruta de código editada correctamente, no marcar AC/DoD ni añadir en Backlog directamente.
- **PostToolUseFailure:** no registrar modificación; un error de herramienta no certifica cambios en el repositorio.
- **PostToolBatch/Stop:** emitir una recomendación de reconciliación por cambio pendiente, conservar lista completa `modifiedFiles`, no forzar cierre ni crear nuevas tareas. `Stop` se silencia con `stop_hook_active=true` y evita bucles de feedback repetido.
- **SessionEnd:** eliminar estado mínimo de `CLAUDE_PLUGIN_DATA`; nunca limpiar archivos de trabajo.

La capa de eventos no interpreta comandos arbitrarios Bash ni MCP; los cambios externos necesitan adaptador aparte. Los eventos `TaskCreated` y `TaskCompleted` de Claude Code **no son registros de Backlog.md**. Para reconciliación real usar [work-alignment](work-alignment.md), para desvío [unplanned-work](unplanned-work.md), para bloqueos [dependency-management](dependency-management.md), para jerarquía [epic-management](epic-management.md).
