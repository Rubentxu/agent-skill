# DSL Jenkins-familiar: mapa operativo

PipelineK persigue una experiencia local comparable a Jenkins Groovy Pipeline, pero la skill aplica una regla estricta:

> **paridad sólo cuando existe carrier + interpreter + evidencia en la versión instalada**.

La tabla siguiente es orientación basada en la línea moderna del proyecto. Antes de usar una fila: `pipelinek version` + `pipelinek validate` + sonda runtime cuando la semántica importe.

## Familias

### Estructura y steps

| Jenkins-familiar | PipelineK | Lectura |
|---|---|---|
| `pipeline/stages/stage` | misma forma conceptual | estable en línea moderna |
| `echo`, `sh`, `error`, `sleep` | steps tipados | básicos |
| `writeFile/readFile/fileExists/deleteDir/cleanWs` | workspace steps | no sustituyen scripts de build |
| `archiveArtifacts` | retención final | distinguir de stash |
| `stash/unstash` | transporte intra-run | no storage remoto general |
| `milestone` | coordinación ordinal | usa sólo con contrato claro |

### Scopes y control

| Patrón | PipelineK | Nota |
|---|---|---|
| `dir {}` | cwd scoped | preferible a `cd ... &&` |
| `withEnv {}` | env scoped | variables no secretas |
| `withCredentials {}` | bindings tipados | carga `07-security.md` |
| `timestamps {}` | decorador de output | si instalación lo soporta |
| `timeout {}` | block deadline | distinto de `options.timeout` |
| `retry {}` | max attempts | no usar para fallo determinista |
| `waitUntil {}` | polling body | conserva eventos de polling |
| `parallel { branch {} }` | branches | root paralelo canónico |
| `catchError/warnError/unstable` | shaping de outcome | no esconder gate obligatorio |

### Declarative

| Construct | Regla |
|---|---|
| `environment {}` | puede existir como directiva declarativa; distinta de `withEnv` |
| `options { timeout(...) }` | stage-wide shell deadline; distinta de block `timeout` |
| `directives { ... }` | superficie experimental de Directive Kernel; no usar para CI de usuario salvo necesidad explícita |

## Builders y runtime values

- `scmGit(...)` es un builder puro: construir configuración no ejecuta checkout.
- `checkout(...)` es el efecto y ha tenido estados parciales/plugin-dependent: verificar versión/plugin.
- `pwd()/isUnix()` son runtime-returning calls; no tratarlos como constantes de construcción.

## Superficies históricamente no disponibles o en evolución

`post`, declarative `when`, `agent`, `node`, shortcut `git`, `load`, `ansiColor` han pasado por estados unsupported/partial/fail-closed. No uses esta skill como excusa para anticipar el roadmap.

Proceso obligatorio:

```text
quiero patrón Jenkins
→ mirar versión instalada
→ probar shape mínima con validate
→ si cambia control/efectos: ejecutar sonda discriminante
→ usar sólo si la semántica observada coincide
```

## Plugins

PipelineK tiene registry abierto para Steps/directivas. Un plugin externo puede requerir `--plugin-jar`. La skill nunca debe:

- meter un `when(stepKey)` en core;
- asumir que un plugin está bundled porque existe en source;
- tratar plugin ausente como no-op;
- inventar un DSL façade no visible al compilador instalado.

## Jenkins controller ≠ PipelineK local

Capacidades como controller queue, `build(job)`, approvals/input centralizados, remote node allocation o plugins vendor-specific no se convierten automáticamente en local Steps. Mantenlas como integración externa o release harness hasta que exista soporte real.

## Cookbook

Para transformaciones concretas Jenkins → PipelineK carga `10-jenkins-migration-cookbook.md`.
