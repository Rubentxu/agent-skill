# backlog-context — plugin de Claude Code

**Integración contextual, no un segundo gestor de tareas.** Complementa [backlog-agile-workflow](../../skills/backlog-agile-workflow/SKILL.md), que conserva toda la política de trabajo portable.

## Instalación y validación

Requiere Claude Code compatible con plugins y **Node.js >=22**. Desde tu terminal:

```bash
claude plugin marketplace add Rubentxu/agent-skills
claude plugin install backlog-context@rubentxu-agent-skills
claude plugin list
```

Claude Code registra automáticamente `hooks/hooks.json` del plugin instalado.

```bash
claude plugin validate ./plugins/backlog-context
node --disable-warning=ExperimentalWarning --experimental-strip-types --test plugins/backlog-context/tests/*.test.mjs
```

No instala Backlog.md, Groma.md, MCP ni modifica permisos. Los hooks no invocan `backlog`, `groma scan`, ni escriben tareas, configuración, repositorios o código.

## Comportamiento

- **SessionStart**: si detecta una carpeta Backlog, propone revisar tareas; solo asocia una tarea con `BACKLOG_CONTEXT_TASK_ID` explícito, nunca infiere identidad a partir de un nombre o estado.
- **PostToolBatch**: agrupa las lecturas `Read` exitosas y, si existe `groma/config.json` o `.groma/config.json`, ejecuta `groma view <archivo>` sobre **un archivo de código** nuevo por lote (timeout 1,5 s). Extrae únicamente IDs de propietario y padre, no código ni descripciones arbitrarias.
- **PostToolUse**: registra solo ediciones confirmadas de Write/Edit/MultiEdit/NotebookEdit, nunca lecturas, Bash ambiguo, documentos administrativos o herramientas MCP no reconocidas.
- **PostToolBatch/Stop**: recomienda reconciliar `modifiedFiles` conservando **la lista completa** del task view original. Recordatorio `Stop` como máximo una vez por archivo y sesión, y ninguno con `stop_hook_active=true`.
- **PostToolUseFailure**: jamás trata una edición fallida como prueba de cambio. **SessionEnd** limpia el estado efímero.

El estado se guarda en `CLAUDE_PLUGIN_DATA/sessions` mediante escritura atómica y bloqueo exclusivo fuera del repositorio. Se limita a rutas relativas, ID opcional y tokens de deduplicación, máximo 64 valores por colección. No se guardan prompts, transcripciones, resultados de herramientas, código ni secretos.

## Límites y permisos

- Los hooks son deliberadamente **read-only para Backlog y el repositorio**. El agente debe invocar las CLIs oficiales por sus herramientas autorizadas tras consultar configuración, AC/DoD, dependencias y estado real.
- Si falta Groma, la consulta arquitectónica se omite; una lectura sin dueño no justifica `groma scan`.
- Los cambios hechos por otras herramientas, scripts Bash, editores externos o agentes MCP requieren adaptadores adicionales; no interpretar comandos shell con expresiones regulares.
- `Stop` puede reabrir un turno una vez para recordar una sincronización pendiente. Se puede retirar ese hook si se prefiere un cierre totalmente silencioso.
- Para trabajo inesperado y dependencias, seguir las lentes `unplanned-work` y `dependency-management` de la skill; no crear nuevos tickets automáticamente.

La API del núcleo de recomendaciones es puro TypeScript; la integración con eventos de Claude Code permanece en `src/hook.ts`.
