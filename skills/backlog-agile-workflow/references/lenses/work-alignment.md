# Work alignment — reconciliar código, tarea y evidencias

**Activación:** tras una edición, al retomar una sesión o antes de cerrar; nunca cambiar tareas por un simple hook.

1. Consultar `backlog task list --json` y `backlog task view <id> --json` para identificar la tarea **real**, estado, dependencias, lista original de `modifiedFiles` y referencias. No deducir tarea activa del nombre de rama.
2. Revisar `git status --short`, `git diff --name-only` y commits por IDs observados, con scope de worktree. Distinguir lectura, edición de herramienta, cambio sin commit y evidencia de test. Un commit no certifica Done.
3. Si Groma está presente, `groma view <ruta>` consulta el propietario del archivo: **solo leer no equivale a modificar**. Si no conoce un owner, indicar cobertura desconocida y no inventar C4 ni disparar scan.
4. Proponer `KEEP_AS_IS` cuando coincide; `UPDATE_PROGRESS` cuando falta registrar cambio real; `REVIEW_COMPLETION` si AC/DoD y gates necesitan validación; `UNTRACKED_WORK` sin asociación; `INSPECT_MORE` si hay datos ambiguos.
5. Para actualizar `modifiedFiles`, leer la lista completa vigente y preservar entradas previas; `--modified-file` **reemplaza** el conjunto. Usar `groma_task_links.py` si hay refs/IDs sustituidos.
6. Solo con permiso para la operación, usar CLI oficial y releer `task view --json`. Para Done seguir [verification](verification.md) y gates reales.

**Salida:** tarea real, leído/cambiado, propietario observado, diferencias en trazabilidad, evidencia, comando propuesto/no ejecutado.
