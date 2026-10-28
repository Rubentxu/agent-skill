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
