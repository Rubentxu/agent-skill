# Roadmap de backlog-agile-workflow

## S0 — Skill portable y navegación (entregado)

- `SKILL.md` autodetectable por intención y recurso `lens-registry.json` `ready/planned`.
- Lentes de descubrimiento, captura, triage, refinamiento, ejecución, cierre y mantenimiento.
- Router puro y parser puro de instantáneas oficiales JSON; no instala ni ejecuta Backlog.md.
- Convivencia declarativa con skills relacionadas, sin imports entre skills.
- Pruebas unitarias de navegación, idempotencia, límites y casos adversariales.

## S1 — Compatibilidad real de CLI (pendiente)

- Evals de agente sobre un proyecto temporal Backlog.md, **autorizado** y efímero, siguiendo CLI verificada localmente.
- Verificar configuración especial `--no-git`, directorios custom, estados y prioridades configurables, DoD y callbacks.
- Comparar versiones de CLI; registrar diferencias como restricciones de compatibilidad, no heurísticas inventadas.
- Mantener duración y dependencia de herramientas por debajo de lo que exige el valor, sin un CI adicional.

## S2 — Mejora de utilidad por conversación (pendiente)

- Medir selección incorrecta de lentes, carga de contexto, abstenciones correctas, elección de tarea con dependencias y falsos cierres.
- Adicionar lentes solo si aportan una pregunta distinta; retirar redundantes.
- Reutilizar selección/lectura cuando otras skills puedan hacerlo mediante protocolos simples, no un motor universal.

## Fuera de alcance

- Ejecutar tareas, modificar código de aplicaciones consumidoras, ejecutar un daemon o duplicar Backlog.md.
- Sincronizar automáticamente roadmaps, crear sprints ficticios o instalar un MCP sin consentimiento.
- Dar por `PASS` pruebas del proyecto por haber pasado tests del router.

## S3 — Proyección segura de ROADMAP/ADR/SPEC/hitos (entregado)

- Lentes `specification-intake`, `spec-decomposition`, `spec-reconciliation`, descubiertas por intención.
- Contrato efímero `spec-packet` con IDs canónicos, hitos, dependencias, gates, estado declarado, requisitos, ADR/SPEC, AC/DoD y prioridad propuesta.
- Proyector puro determinista: rechaza referencias inválidas/ciclos/duplicidades; preserva trabajo histórico; compara `task-list` existente y bloquea creación ante corpus incompleto o coincidencia sospechosa; nunca ejecuta la CLI.
- Tests de comportamiento sobre escenarios sintéticos, sin alterar proyectos consumidores.

### S4 — Futuras evaluaciones (pendiente)

- Evals de agente con documentos sintéticos extensos y mezclados (planes, históricos, receipts, contradicciones).
- Validar con una instalación temporal de Backlog.md el formato exacto de `references` y compatibilidad de versiones antes de automatizar propuestas de `--ref`.
- Medir falsos positivos de extracción, cantidad de preguntas necesarias y coste de navegación. No introducir indexador, base de datos secundaria ni sincronización automática como requisito.

## S5 — Privacidad Git e identificadores cruzados

- Detectar planificaciones y ZIP rastreados en índices de aplicaciones consumidoras; conservar bytes, reubicar/respaldar y proponer `.gitignore`/untracking, no ejecutar destrucción de forma automática.
- Escribir en commits IDs estables de tarea, bloque roadmap, ADR/SPEC existentes junto con implementación y evidencia; revisar historia antes de generar trabajo duplicado.
- Reconciliar tareas con historial mediante índice puro opcional. Ante implementaciones ya abordadas, pedir revisión, no crear una segunda tarea ni certificar DONE.
- Invocar especialistas por disponibilidad: testing, CI PipelineK, refactorización funcional y secretless.
- Probar con fixtures sintéticas sin modificar proyectos reales. La modalidad de Backlog.md con Git ignorado requiere plan de conservación/sincronización externa.

## S6 — Groma integrado como capacidad opcional

- Investigación de la integración oficial mediante `workSources.backlog`, `task list/view --json`, `--watch`, referencias y changed files.
- Lentes de arquitectura C4 y enlace de tareas, router con Groma opcional y Backlog independiente.
- Helper puro que preserva la lista completa `modifiedFiles` y referencias, incluidos los IDs sustituidos por combine/rename.
- Guard Git de OKF, config y ZIP/exportaciones privadas, con advertencias sobre la historia Git que se pierde al ignorarlos.
- Validación sintética del router, helper y clasificación; **pendiente** una prueba conjunta de ambas CLIs en un workspace autorizado y efímero. No reclamar compatibilidad completa de versiones, watch, modo --no-git o action de PR sin ella.

## S7 — CRUD Kanban completo y seguro

- Nuevas lentes de creación, transiciones y archivo/restauración; `delete` permanece como operación destructiva fuera del ciclo automático.
- Router de intención que distingue `create-task`, `move-task`, `archive-task`, `restore-task`, `delete-task` sin inventar estados ni archivar automáticamente al cerrar.
- Propuestas deterministas de argv mediante `board_crud.py`: preflight de configuración, validación de evidencia de Done, readiness para comenzar, idempotencia y revisión de dependencias de cancelaciones.
- Tests unitarios con fixtures sintéticas sin escribir tareas ni abrir el tablero TUI. Validar en entorno temporal autorizado con versión real de la CLI antes de afirmar compatibilidad end-to-end.
- Conservar el mismo contrato de tareas privadas fuera de Git y trazabilidad mediante IDs/SHAs en commits.
