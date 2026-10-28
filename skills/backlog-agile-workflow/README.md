# backlog-agile-workflow

Skill portable para **trabajo ágil ligero** con [Backlog.md](https://github.com/MrLesk/Backlog.md). En vez de reimplementar tareas en scripts, usa la CLI oficial y selecciona una guía por problema. No requiere Scrum, sprints, servicio remoto ni integración MCP.

## Activaciones

- «Convierte esta idea en tareas pequeñas y criterios de aceptación»
- «Prioriza lo que puedo implementar ahora, respetando dependencias»
- «Prepara un plan para la tarea actual, sin tocar código»
- «¿Está lista para cerrar? ¿Qué falta en su Definition of Done?»
- «Revisa bloqueos, WIP y trabajo obsoleto del backlog»
- «¿Cómo configuro Backlog.md en un proyecto local-first sin commits automáticos?»

## Contrato

1. **Lectura primero:** detectar la CLI, el proyecto y su configuración; `backlog instructions overview` es el primer manual operativo.
2. **Ruta bajo demanda:** seleccionar una o dos lentes; no cargar todos los documentos.
3. **Sugerir antes de escribir:** la skill distingue exploración, propuestas y ejecución autorizada.
4. **Un único propietario:** tareas/estados/IDs solo los escribe Backlog.md. Esta skill nunca toca archivos de trabajo ni crea su propio estado.
5. **Entrega verificable:** criterios de aceptación y DoD demostrados, no checkboxes optimistas. No modificar aplicaciones por el mero uso de la skill.

## Uso local (tests del router, sin Backlog.md instalado)

```bash
python3 skills/backlog-agile-workflow/scripts/affordances.py skills/backlog-agile-workflow/examples/triage.json
python3 skills/backlog-agile-workflow/scripts/ready_candidates.py skills/backlog-agile-workflow/examples/ready-list.json
python3 -m unittest discover -s skills/backlog-agile-workflow/tests -p 'test_*.py' -v
```

Instalación desde `Rubentxu/agent-skill` cuando esté publicada:

```bash
npx skills add Rubentxu/agent-skill --skill backlog-agile-workflow --agent opencode
```

La herramienta **Backlog.md** es un requisito separado para usar tareas reales. No se instala automáticamente. Tras instalarla y con un proyecto autorizado, empezar por `backlog instructions overview`. Para ejecución ocasional, `npx backlog.md <comando>`; `npx backlog` corresponde a otro paquete.

## Compatibilidad y límites

- Probado: selector, rutas internas, escenarios sintéticos. No se afirma haber ejecutado una CLI externa ni un proyecto real.
- Integraciones opcionales: `delivery-first-testing` (garantías), `pure-functional-design` (diseño/refactor), `cognicode-diagrams` (observaciones con sus restricciones). Sin acoplamiento de archivos.
- En backlog sin inicializar, la recomendación es preparación, no una ejecución de `init` en segundo plano.
