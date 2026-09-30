# pipelinek-local-ci

Skill para agentes que usan **PipelineK como CI/CD local**: crea y mantiene `pipeline.kts`, migra intención desde GitHub Actions/Jenkins/GitLab CI, ejecuta gates durante desarrollo y usa outcome/eventos como evidencia.

## Instalación

```bash
npx skills add Rubentxu/agent-skill --skill pipelinek-local-ci --agent opencode
```

Para instalación global añade `--global` si el host/agente lo soporta.

## Qué hace

- inspecciona el stack real antes de diseñar stages;
- crea/refactoriza `pipeline.kts` sin traducir YAML/Groovy mecánicamente;
- reutiliza wrappers y comandos del propio proyecto;
- valida la DSL contra el binario PipelineK realmente resuelto;
- ejecuta CI local con estado durable fuera del repositorio;
- interpreta exit, `RunFinished.outcome` y eventos tipados;
- ayuda a sustituir CI alojado por PipelineK manteniendo sólo triggers remotos cuando aporten valor;
- detecta conflictos comunes de PATH/shims/mise/asdf antes de confiar en una ejecución.

## Estructura

- `SKILL.md`: procedimiento y guardas.
- `references/01-pipeline-authoring.md`: diseño y creación de pipelines.
- `references/02-agentic-loop.md`: bucle de uso por un coding agent.
- `references/03-migration-hosted-ci.md`: migración desde CI alojado/Jenkins.
- `references/04-version-resolution.md`: resolución exacta del binario.
- `references/05-events-and-troubleshooting.md`: eventos, outcomes y triage.
- `examples/minimal.pipeline.kts`: ejemplo mínimo que siempre debe validarse contra la versión instalada antes de adoptarlo.
- `tests/skill-evals.md`: escenarios de comportamiento de la skill.

La skill **no instala PipelineK** ni modifica automáticamente mise/asdf/SDKMAN. La distribución de PipelineK evoluciona independientemente; el agente debe verificar siempre qué binario está ejecutando.
