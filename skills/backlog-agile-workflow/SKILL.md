---
name: backlog-agile-workflow
description: "Gestiona trabajo ágil local-first con Backlog.md CLI: captura y refina tareas, elige trabajo listo por dependencias, planifica justo a tiempo, verifica AC/DoD, cierra con evidencia y descubre playbooks bajo demanda. Úsala para backlog, kanban, prioridades, roadmap, sprints ligeros y seguimiento de trabajo; no manipula archivos Backlog.md directamente."
---

# Backlog Agile Workflow — navegación contextual, no otro gestor de tareas

**Propósito:** ayudar a agentes y humanos a entregar valor en incrementos pequeños usando la CLI de [Backlog.md](https://github.com/MrLesk/Backlog.md); Backlog.md es el sistema de registro y su CLI la autoridad sobre tareas, identificadores, estados, dependencias y configuración. Esta skill es **portable** entre aplicaciones, repositorios y agentes. No añade servidor, daemon, motor de scheduling, base de datos, ni API de tareas alternativa.

## Contrato de arranque y descubrimiento

1. Determinar la **intención de la conversación** y etapa vigente: `discover|capture|triage|refine|plan|execute|verify|close|review|maintain|specify|decompose|sync-specs|catalog`. No arrastrar lentes de otra intención por inercia.
2. Verificar si `backlog` existe y qué proyecto está activo **sin instalar ni inicializar automáticamente**. Para tareas reales, leer primero `backlog instructions overview`; después solo `backlog instructions task-creation`, `task-execution` o `task-finalization` cuando correspondan. La ayuda local prevalece si difiere de la documentación empaquetada.
3. Si la CLI no está disponible, mostrar opciones de instalación para aprobación; `npx backlog.md ...` es una alternativa ocasional, **nunca** `npx backlog ...` (paquete distinto). Si no hay proyecto inicializado, proponer `backlog init` pero no ejecutar una configuración interactiva sin autorización.
4. Descubrir preferencias y límites del proyecto vía `backlog config get <clave>` cuando se conozca el comando y consultando la CLI actual; `statuses`, `defaultStatus`, `definition_of_done`, `projects`, `remoteOperations`, `autoCommit`, `bypassGitHooks`, `checkActiveBranches`, `onStatusChange`. No suponer columnas fijas ni que cerrar equivale a archivar.
5. Leer el estado **real** mediante `backlog task list --json`, `backlog task view <id> --json`, `backlog search ... --json`, `backlog milestone list --plain`; usar `schemaVersion` y `kind` para los parsers. `--watch` es una suscripción de larga duración, no una consulta puntual.
6. Seleccionar como máximo **dos lentes** desde `references/lens-registry.json` según intención y hechos disponibles. `scripts/affordances.py` es un router determinista y **sin acceso a la CLI ni a aplicaciones**; emite enlaces a recursos y recomendaciones, nunca ejecuta comandos. `scripts/spec_projection.py` compara un paquete explícito de especificaciones con una instantánea `task-list` sin mutar ninguno. `scripts/ready_candidates.py` valida una instantánea JSON **ya obtenida** y devuelve tareas listas sin mutarla ni consultar Backlog.md.
7. Si aparecen huecos, abrir solo la lente siguiente. Los handoffs a otras skills se ofrecen únicamente si el anfitrión confirma `available_skills`. No importar ficheros de otra skill.

## Flujo ágil: valor, límites de WIP y evidencia

- **Desde especificaciones:** ROADMAP, ADR, SPEC, gates y receipts son autoridades diferentes: convertir objetivos en propuestas de tareas con referencia estable, reconstruir dependencias y comparar con el backlog existente antes de escribir. Ver [contrato spec-packet](references/spec-contract.md) y [proyección](references/lenses/spec-reconciliation.md). Nunca transformar cada sección histórica en una tarea.
- **Capturar:** buscar duplicados antes de crear. Ambigüedades → borrador (`backlog draft create`) o tarea con incertidumbre explícita, según aceptación; no convertir una idea vaga en veinte tareas especulativas.
- **Refinar:** una capacidad observable por tarea, criterios de aceptación verificables y pequeños, Definition of Done del proyecto; dependencias solamente si son bloqueantes reales. Registrar decisiones arquitectónicas como decisiones, no como pseudo-tareas.
- **Priorizar:** seleccionar trabajo listo (`isReady` derivado de JSON, o `backlog task list --ready`) y alto valor con bajo riesgo; no inventar estimaciones, sprint commitments, ni prioridades. Una tarea bloqueada o identidad de dependencia ambigua no es lista.
- **Planificar justo antes de construir:** plan acotado en `backlog task edit <id> --plan ...`; revisar seams y contratos actuales. El plan puede modificarse, pero no escribir código de producción desde esta skill.
- **Ejecutar:** **una tarea por flujo** por defecto; registrar notas con `--append-notes` (no reemplazar progreso existente), observar cambios y verificar el contrato mediante las herramientas autorizadas.
- **Verificar:** comprobar criterios de aceptación y DoD de **forma individual**, marcándolos solo tras evidencia real; tests `NOT_RUN` no equivalen a `PASS`. Delegar selección de pruebas a `delivery-first-testing` solo si disponible.
- **Cerrar:** escribir `--final-summary` con resultado y riesgos, marcar estado final configurado solo con evidencias; archivar después durante mantenimiento explícito, no al completar.
- **Revisar:** analizar bloqueos, exceso de WIP y tareas abandonadas; ajustar primero políticas y descomposición, no multiplicar reuniones ni burocracia.

## Políticas de seguridad, Git y concurrencia

- Las **lecturas** no autorizan **escrituras**; para init, config, create/edit/status, archivar, restaurar o eliminar se necesita intención explícita del usuario o permiso previo específico. Los scripts de esta skill no ejecutan comandos Backlog.md.
- No editar directamente Markdown/frontmatter de tareas, borradores, docs, decisiones ni milestones gestionados por Backlog.md; usar CLI/MCP oficial. Si el CLI rechaza un bloque legado sin marcadores, detenerse y pedir reparación humana; no sobrescribirlo manualmente.
- `autoCommit=true` puede crear commits; `remoteOperations=true` puede consultar remotos; `bypassGitHooks=true` omite hooks; `onStatusChange` puede ejecutar shell. **Inspeccionar antes de modificar** y advertir si afectan a la operación. No cambiar la configuración silenciosamente. `checkActiveBranches` condiciona coste/visibilidad, no habilita estados inventados.
- Git tiene historia; el backlog puede tener estados diferentes en ramas/worktrees. No confiar en un ID ambiguo. `backlog doctor` es diagnóstico; `--fix` requiere autorización y revisión de cambios. Nunca usar `backlog task delete` o `backlog cleanup` automáticamente.
- Las subtareas son opcionales, no una métrica. Evitar tareas huérfanas y dependencias circulares. No crear nuevos estados o prioridades sin observar configuración real.
- `--notes` reemplaza el campo; preferir `--append-notes` para progresos. Las secuencias literales `\n` no se convierten en saltos: usar saltos reales o flags repetidas. Para mensajes de comentario, usar `--comment`; para cierre, `--final-summary`.
- En automatizaciones no interactivas, evitar `backlog config` sin argumentos, `backlog init` interactivo, `board`, `browser`, `cleanup`, editores y suscripciones `--watch` sin ciclo de vida controlado.

## Enlaces bajo demanda

| Pregunta | Lente |
|---|---|
| ¿Hay Backlog.md y qué configuración es segura? | [discovery](references/lenses/discovery.md) |
| ¿Cómo interpretar ROADMAP, ADR, SPEC y gates sin reabrir historia? | [specification-intake](references/lenses/specification-intake.md) |
| ¿Cómo priorizar hitos y descomponerlos en tareas útiles? | [spec-decomposition](references/lenses/spec-decomposition.md) |
| ¿Cómo conciliar especificaciones y tareas ya existentes? | [spec-reconciliation](references/lenses/spec-reconciliation.md) |
| ¿Cómo registrar ideas y evitar duplicados? | [capture](references/lenses/capture.md) |
| ¿Qué tarea aporta valor y está desbloqueada? | [triage](references/lenses/triage.md) |
| ¿Cómo separar una capacidad en una tarea verificable? | [refinement](references/lenses/refinement.md) |
| ¿Cómo ejecutar un ciclo corto sin deriva? | [execution](references/lenses/execution.md) |
| ¿Cuándo marcar AC/DoD y finalizar? | [verification](references/lenses/verification.md) |
| ¿Qué mejorar del flujo y cómo limpiar? | [review-maintenance](references/lenses/review-maintenance.md) |

Navegación [HATEOAS-like](references/navigation.md) · [Comandos comprobados](references/cli-reference.md) · [Configuración avanzada y riesgos](references/configuration.md) · [integración con otras skills](references/skill-registry.json) · [fuentes](references/sources.md). El router nunca certifica una ejecución ni presume capacidades instaladas.
