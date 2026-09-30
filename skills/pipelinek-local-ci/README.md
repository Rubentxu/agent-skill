# pipelinek-local-ci

Skill agent-first para **instalar, crear, migrar, revisar y operar PipelineK como CI/CD local**.

No es sólo una wrapper de CLI: enseña al agente a convertir la política real del repositorio en `pipeline.kts`, aprovechar la DSL Jenkins-familiar que PipelineK soporta, usar eventos/outcomes como señal de auto-diagnóstico y ejecutar operaciones autenticadas con una postura de credenciales explícita.

## Instalar la skill

```bash
npx skills add Rubentxu/agent-skill --skill pipelinek-local-ci --agent opencode
```

## Modos

- `bootstrap`: instala/fija PipelineK con mise o asdf y verifica identidad.
- `scaffold`: crea una pipeline real por stack.
- `review`: audita una pipeline existente.
- `run`: usa PipelineK como gate local durante desarrollo.
- `observe`: proyecta el NDJSON de eventos para agentes sin perder la evidencia completa.
- `secretless`: combina PipelineK con Agent Secretless Vault (ASV) para signer/proxy/session sin entregar el secreto al agente.
- `migrate`: mueve política CI desde Jenkins/Actions/GitLab.
- `diagnose`: resuelve DSL, toolchains, shims, credenciales, eventos y fallos.

## Instalación de PipelineK

La skill incluye recetas actuales para mise y asdf en `references/04-version-resolution.md`. Las recetas siempre terminan comprobando la identidad runtime; instalar no equivale a verificar.

## Credenciales

Hay dos niveles distintos:

```text
PipelineK withCredentials
  -> secreto entra de forma controlada en el child
  -> lifecycle + redacción + wipe

PipelineK dentro de ASV
  -> child ve socket/surrogate/capability
  -> secreto real permanece en broker
```

Consulta:

- `references/07-security.md` para bindings/store/redacción de PipelineK.
- `references/09-agent-secretless.md` para strong-secretless, KeePassXC como fuente operator-side y mecanismos Linux.
- `references/10-event-filters.md` para filtrar `RunFinished`, `StepFailed`, control-flow y lifecycle de credenciales sin imprimir valores.

## Ejemplos incluidos

- `minimal.pipeline.kts` — sólo `echo`, sin comandos ficticios.
- `gradle-ci.pipeline.kts` — Gradle wrapper + timeout + artifact.
- `maven-ci.pipeline.kts` — Maven wrapper + verify + artifact.
- `node-ci.pipeline.kts` — npm + ramas lint/test paralelas.
- `rust-ci.pipeline.kts` — fmt/clippy/test.
- `python-uv-ci.pipeline.kts` — uv + ruff/pytest.
- `go-ci.pipeline.kts` — vet/test/build.
- `jenkins-familiar.pipeline.kts` — composición de `withEnv`, `timeout`, `retry`, `parallel`, `stash/unstash` y `archiveArtifacts`.
- `secretless-git.pipeline.kts` — operación Git normal que puede ejecutarse dentro de una sesión ASV sin conocer la clave privada.

Los templates son **starters condicionados**: sólo se adoptan si el repositorio contiene la herramienta/script correspondiente y la instalación de PipelineK valida la DSL.

## Principio

```text
coding agent
   ↓
affected verification
   ↓
PipelineK local CI
   ↓ typed events / durable outcome
fix ↺                close
```

Cuando hay autenticación fuerte:

```text
coding agent
   ↓
ASV session
   ↓
PipelineK
   ↓
normal tool command
   ↓
broker signer/proxy
```

El objetivo es que PipelineK sea el equivalente local agent-first de una pipeline Jenkins: familiar en DSL, pero con contratos tipados, replay durable, hechos observables para automatización y una vía explícita para ejecutar trabajo autenticado sin convertir secretos en prompt/env del agente.
