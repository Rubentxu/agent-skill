# pipelinek-local-ci

Skill agent-first para **instalar, crear, migrar, revisar y operar PipelineK como CI/CD local**.

No es sólo una wrapper de CLI: enseña al agente a convertir la política real del repositorio en `pipeline.kts`, aprovechar la DSL Jenkins-familiar que PipelineK soporta y usar eventos/outcomes como señal de auto-diagnóstico.

## Instalar la skill

```bash
npx skills add Rubentxu/agent-skill --skill pipelinek-local-ci --agent opencode
```

## Modos

- `bootstrap`: instala/fija PipelineK con mise o asdf y verifica identidad.
- `scaffold`: crea una pipeline real por stack.
- `review`: audita una pipeline existente.
- `run`: usa PipelineK como gate local durante desarrollo.
- `migrate`: mueve política CI desde Jenkins/Actions/GitLab.
- `diagnose`: resuelve DSL, toolchains, shims, workspaces, eventos y fallos.

## Workspace local-first

La skill sigue el contrato RP-034 de PipelineK:

```bash
cd /repos/mi-proyecto
pipelinek run /ruta/al/pipeline.kts
```

El directorio de invocación es el workspace Attached por defecto; la ubicación del fichero `pipeline.kts` es independiente. Usa `--workspace <repo>` sólo como override explícito y `--isolated` cuando quieras un scratch Managed. `dir { }` cambia el cwd scoped, no la raíz ni el ownership.

Consulta `references/09-workspaces-and-execution-location.md` para la semántica completa, seguridad de `deleteDir/cleanWs` y diagnóstico.

## Instalación de PipelineK

La skill incluye recetas actuales para mise y asdf en `references/04-version-resolution.md`. Las recetas siempre terminan comprobando la identidad runtime; instalar no equivale a verificar.

## Ejemplos incluidos

- `minimal.pipeline.kts` — sólo `echo`, sin comandos ficticios.
- `gradle-ci.pipeline.kts` — Gradle wrapper + timeout + artifact.
- `maven-ci.pipeline.kts` — Maven wrapper + verify + artifact.
- `node-ci.pipeline.kts` — npm + ramas lint/test paralelas.
- `rust-ci.pipeline.kts` — fmt/clippy/test.
- `python-uv-ci.pipeline.kts` — uv + ruff/pytest.
- `go-ci.pipeline.kts` — vet/test/build.
- `jenkins-familiar.pipeline.kts` — composición de `withEnv`, `timeout`, `retry`, `parallel`, `stash/unstash` y `archiveArtifacts`.

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

El objetivo es que PipelineK sea el equivalente local agent-first de una pipeline Jenkins: familiar en DSL, pero con contratos tipados, replay durable y hechos observables para automatización.
