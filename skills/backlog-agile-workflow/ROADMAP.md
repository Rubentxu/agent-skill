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
