---
name: pipelinek-local-ci
description: "Usa PipelineK como CI/CD local agent-first: instala y verifica PipelineK, crea/revisa pipeline.kts, ejecuta gates con replay y eventos, usa credenciales de forma segura y extiende PipelineK mediante plugins de Steps/directivas/providers cuando la instalación lo soporte. Jenkins/Actions/GitLab sólo se usan como fuentes de migración, no como modelo de capacidades."
metadata:
  version: "3.1.0"
---

# PipelineK local CI — agent-first

El centro de esta skill es **PipelineK**: su DSL real, CLI, ejecución durable, eventos, credenciales y modelo de plugins.

> Router: carga sólo la referencia necesaria para la tarea.

## Modos

| Modo | Cuándo | Carga |
|---|---|---|
| `bootstrap` | conseguir/verificar `pipelinek` | `04-version-resolution.md`, `09-installation-cookbook.md` |
| `scaffold` | crear/ampliar `pipeline.kts` | `00-decision-tree.md`, `01-pipeline-authoring.md`, `13-pipelinek-capability-map.md` |
| `review` | auditar DSL/semántica | `08-review-checklist.md`, `13-pipelinek-capability-map.md` |
| `run` | usar PipelineK como gate | `02-agentic-loop.md`, `05-events-and-troubleshooting.md`, `11-cli-cookbook.md` |
| `extend` | Steps/directivas/providers | `14-plugin-extension-model.md`, `15-credential-provider-extensions.md` |
| `migrate` | traer política desde Jenkins/Actions/GitLab | `03-migration-hosted-ci.md`; `10-jenkins-migration-cookbook.md` sólo si procede |
| `diagnose` | DSL/runtime/toolchain/plugin | `04-version-resolution.md`, `05-events-and-troubleshooting.md` |

## Reglas

1. **PipelineK primero.** No diseñes por paridad con otra herramienta.
2. **Identidad exacta.** `command → realpath → pipelinek version`; requested/selected/runtime deben coincidir.
3. **Cero comandos ficticios.** Descubre wrappers/scripts/targets reales.
4. **DSL observada.** Toda edición estructural termina en `pipelinek validate`; control-flow sensible requiere sonda runtime.
5. **Primitive tipada antes que shell artesanal** cuando PipelineK ya ofrece semántica real equivalente.
6. **No overclaim.** Si no hay carrier/interpreter real, fail closed o rediseña.
7. **Eventos son API de feedback.** Usa outcome + eventos + exit, no sólo texto.
8. **Durabilidad explícita.** DB/control-root fuera del repo salvo política.
9. **Plugins sin privilegios.** Step/directive externo usa registry/capabilities/durable spine común.
10. **Secretos por referencias/bindings.** Nunca valores en source/argv/logs.
11. **Provider-neutral no significa plugin-hosting automático.** Comprueba si la instalación expone discovery/selection del provider.
12. **Fast/slow lane.** Feedback focal en desarrollo; full pipeline en integración; certificación externa donde corresponda.

## Flujo normal

### 1. Descubrir

```bash
bash <skill>/scripts/pipelinek-preflight.sh
bash <skill>/scripts/discover-ci-context.sh
```

Lee además instrucciones del repo y `pipeline.kts` existente.

### 2. Conocer capacidades PipelineK

Carga `13-pipelinek-capability-map.md`. No copies una feature sólo porque sea familiar de Jenkins.

### 3. Crear pipeline

Diseña stages por responsabilidades reales y usa sólo comandos observados en el proyecto.

### 4. Validar

```bash
pipelinek validate pipeline.kts
```

### 5. Ejecutar

Usa journal/control-root durable y observa `RunFinished`, `StepFailed` y eventos de control.

### 6. Extender si falta capacidad

Si falta una capacidad universal/first-party/vendor, decide si corresponde core, plugin Step/directiva o CredentialProvider. No metas casos específicos en el coordinator.

## Definition of Done

- [ ] binario/version inequívocos;
- [ ] `pipeline.kts` valida;
- [ ] comandos existen;
- [ ] positivo real;
- [ ] negativo discriminante cuando se crea/migra semántica;
- [ ] eventos/outcome revisados;
- [ ] estado fuera del repo salvo política;
- [ ] secretos no expuestos;
- [ ] plugins usan seams públicos;
- [ ] cualquier capability no soportada queda explícitamente marcada, no simulada.