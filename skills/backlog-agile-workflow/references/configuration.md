# Configuración avanzada y riesgos previos a un flujo ágil

**Fuentes upstream:** [ADVANCED-CONFIG.md](https://github.com/MrLesk/Backlog.md/blob/main/ADVANCED-CONFIG.md) y [CLI-INSTRUCTIONS.md](https://github.com/MrLesk/Backlog.md/blob/main/CLI-INSTRUCTIONS.md). El agente debe **inspeccionar** el proyecto concreto y la versión de CLI; no imponer estos valores a otros repositorios.

## Comprobaciones antes de la primera escritura

| Clave | Valor por defecto documentado | Riesgo/acción |
|---|---|---|
| `autoCommit` | `false` | si `true`, una edición de tarea puede crear commit; comprobar política Git antes |
| `remoteOperations` | `true` | puede consultar remotos; para offline local-first, proponer `backlog config set remoteOperations false` **solo con consentimiento** |
| `bypassGitHooks` | `false` | si `true`, omite hooks en commits automáticos; no activar por conveniencia |
| `checkActiveBranches` | `true` | precisión entre ramas con coste potencial; no desactivar silenciosamente |
| `activeBranchDays` | `30` | ventana de ramas activas; observar antes de optimizar |
| `onStatusChange` | desactivado | **puede ejecutar comandos shell** al cambiar estado; revisar texto/efectos antes |
| `statuses` | `To Do, In Progress, Done` | configurables: leer antes de marcar estado final |
| `defaultStatus` | primera columna | no asumir que toda nueva tarea empieza en `To Do` |
| `definition_of_done` | sin definir | usar DoD real, no imponer checklist genérico |
| `priorities` | `High, Medium, Low` | pueden variar; no transformar etiquetas ni inventar SLA |
| `projects` | sin definir | `--project` solo si el monorepo la configuró |
| `defaultAssignee` | opcional | se hereda al crear sin `-a`; `-a ""` evita asignar según documentación |

Claves consultables con `backlog config get <clave>` según API de la versión actual; el archivo de configuración de la instalación puede ser `backlog.config.yml`, `backlog/config.yml` o `.backlog/config.yml`. El directorio de backlog custom se declara en `backlog.config.yml` raíz; no suponer rutas ni mover el directorio sin cuidado.

Las claves como `statuses`, `priorities`, `projects` y otros listados se editan en el archivo de **configuración** con revisión explícita: el CLI `config set` no soporta todos los campos. Esto no autoriza editar directamente las tareas, los docs o las decisiones propiedad de Backlog.md. `onStatusChange` puede contener código: mostrar el efecto, no ejecutarlo en el router.

Si la CLI fue inicializada con `--no-git`, no trasladar automáticamente políticas de ramas o remotos. En un repositorio Git, una lectura del tablero puede reflejar corpus de ramas activas; consultar IDs y dependencias antes de actuar y no interpretar `isReady` como compromiso de sprint.

**Regla de privacidad:** el backlog puede almacenar información confidencial. No exportar tablero ni compartir contenido a servicios de terceros por defecto. No instalar Backlog.md globalmente sin petición.
