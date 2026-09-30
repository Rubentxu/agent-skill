# pipelinek-local-ci

Skill agent-first centrada en **PipelineK**: DSL, CLI, ejecución durable, eventos, credenciales y extensiones.

## Instalar la skill

```bash
npx skills add Rubentxu/agent-skill --skill pipelinek-local-ci --agent opencode
```

## Qué cubre

- instalar/verificar PipelineK;
- crear y revisar `pipeline.kts` reales;
- usar PipelineK como gate local durante desarrollo;
- replay/resume, eventos y diagnóstico causal;
- credenciales mediante bindings seguros;
- plugins de Steps y directivas;
- modelo de extensión para CredentialProvider/Secret Providers;
- migración desde Jenkins/Actions/GitLab sólo como fuente de intención.

## Qué NO intenta hacer

- reproducir todo Jenkins;
- convertir Groovy/YAML 1:1;
- inventar capacidades que PipelineK aún no tenga;
- hacer que mise/asdf formen parte conceptual del producto.

Mise y asdf aparecen sólo como **canales opcionales para obtener/pinear el binario**.

## Referencias principales

- `13-pipelinek-capability-map.md` — qué familias ofrece PipelineK y cómo decidir si usarlas;
- `01-pipeline-authoring.md` — creación de `pipeline.kts`;
- `11-cli-cookbook.md` — validate/run/rerun/resume/credentials/plugins;
- `14-plugin-extension-model.md` — Steps/directivas externas;
- `15-credential-provider-extensions.md` — secret providers y límites actuales;
- `05-events-and-troubleshooting.md` — feedback agentic por eventos.

## Instalación

`09-installation-cookbook.md` contiene mise/asdf/instalador directo. Esta parte es secundaria a la skill: el objetivo es terminar con un `pipelinek` reproducible y verificable.

## Ejemplos

- `minimal.pipeline.kts`
- `gradle-ci.pipeline.kts`
- `maven-ci.pipeline.kts`
- `node-ci.pipeline.kts`
- `rust-ci.pipeline.kts`
- `python-uv-ci.pipeline.kts`
- `go-ci.pipeline.kts`
- `credentials.pipeline.kts`
- `polyglot-monorepo.pipeline.kts`
- `jenkins-familiar.pipeline.kts` — sólo compatibilidad/migración

## Arquitectura mental

```text
project intent
   ↓
PipelineK DSL
   ↓
typed carrier / Step / directive
   ↓
registry + capabilities
   ↓
durable execution
   ↓
typed events / outcome
   ↓
agent fixes or closes
```

Si falta una capacidad, la skill debe decidir si se resuelve con una primitive existente, un plugin o un capability gap del producto; no simularla.