# pipelinek-local-ci

Skill agent-first para **instalar, crear, migrar, revisar y operar PipelineK como CI/CD local**.

No es una wrapper de CLI: enseña al agente a convertir la política real del repositorio en `pipeline.kts`, usar la DSL Jenkins-familiar que el binario realmente soporte y cerrar trabajo con eventos/outcomes observables.

## Instalar la skill

```bash
npx skills add Rubentxu/agent-skill --skill pipelinek-local-ci --agent opencode
```

## Qué mejora la v3

- bootstrap reproducible por proyecto con mise/asdf;
- preflight read-only de PATH/shims/version/JDK;
- discovery de wrappers/manifests/CI antes de generar comandos;
- cookbook Jenkins → PipelineK orientado a semántica;
- cookbook CLI para run durable, rerun/resume, credenciales y plugins;
- recetas agentic para monorepos, fast/slow lane, retry y auto-fix;
- ejemplos adicionales de credenciales y monorepo poliglota;
- regla estricta: una tabla de compatibilidad nunca supera a `pipelinek validate` + runtime observado.

## Modos

- `bootstrap`: instalar/fijar PipelineK con mise o asdf y verificar identidad.
- `scaffold`: crear una pipeline real por stack.
- `review`: auditar una pipeline existente.
- `run`: usar PipelineK como gate local durante desarrollo.
- `migrate`: mover política CI desde Jenkins/Actions/GitLab.
- `diagnose`: resolver DSL, toolchains, shims, eventos y fallos.

## Scripts de la skill

```bash
bash scripts/pipelinek-preflight.sh
bash scripts/discover-ci-context.sh
```

Son sondas read-only: no instalan herramientas ni cambian gestores/versiones.

## Instalación de PipelineK

Consulta `references/09-installation-cookbook.md`.

### Mise

PipelineK usa el backend GitHub nativo de mise, con pin en `mise.toml`; no hace falta enrutar mise a través del plugin asdf.

### asdf

PipelineK usa `Rubentxu/asdf-pipelinek`, pin en `.tool-versions` y `asdf set` moderno.

En ambos casos instalar no basta: `requested == selected == pipelinek version`.

## Ejemplos

- `minimal.pipeline.kts` — smoke inocuo.
- `gradle-ci.pipeline.kts` — Gradle wrapper.
- `maven-ci.pipeline.kts` — Maven wrapper.
- `node-ci.pipeline.kts` — npm + checks paralelos.
- `rust-ci.pipeline.kts` — fmt/clippy/test/build.
- `python-uv-ci.pipeline.kts` — uv + tooling declarado.
- `go-ci.pipeline.kts` — vet/test/build.
- `credentials.pipeline.kts` — binding tipado de secret text.
- `polyglot-monorepo.pipeline.kts` — backend Gradle + frontend npm.
- `jenkins-familiar.pipeline.kts` — scopes, timeout/retry, parallel y artifacts.

Cada ejemplo declara precondiciones. El agente debe comprobarlas antes de copiarlo y validar la DSL con la versión seleccionada.

## Jenkins-familiar

PipelineK está orientado a ofrecer capacidades locales comparables a Jenkins Groovy Pipeline, pero la skill separa:

```text
intención Jenkins
→ carrier/semántica PipelineK
→ validate
→ ejecución observable
```

No inventa paridad para `when/post/agent/node/...` si la instalación todavía no la tiene. El mapa completo está en `references/10-jenkins-migration-cookbook.md` y `06-jenkins-familiar-dsl.md`.

## Principio agentic

```text
coding agent
   ↓
affected verification
   ↓
PipelineK local CI
   ↓ typed events / durable outcome
fix ↺                close
```

Hosted CI puede seguir existiendo para triggers, matrices de SO, release, distribución o deploy, pero no debería contener una segunda política de CI divergente.
