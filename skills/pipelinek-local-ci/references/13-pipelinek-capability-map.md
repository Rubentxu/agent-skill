# PipelineK capability map

Esta referencia describe **PipelineK**, no Jenkins. Jenkins aparece sólo como vocabulario de migración cuando ayuda.

La autoridad final es siempre la versión instalada:

```text
pipelinek version
→ pipelinek validate
→ sonda runtime cuando la semántica importa
```

## Núcleo de authoring

La línea moderna de PipelineK modela estas familias:

### Estructura

- `pipeline { }`
- `stages { }`
- `stage("...") { }`

### Proceso y control básico

- `echo`
- `sh`
- `error`
- `sleep`

### Workspace / filesystem

- `dir { }`
- `pwd()`
- `isUnix()`
- `writeFile`
- `readFile`
- `fileExists`
- `deleteDir`
- `cleanWs`

### Contexto

- `withEnv { }`
- `environment { }`
- `withCredentials { }`
- `timestamps { }`

### Control flow

- `timeout { }`
- `retry { }`
- `waitUntil { }`
- `parallel { branch(...) { } }`
- `catchError { }`
- `warnError { }`
- `unstable(...)`

### Artifacts

- `stash`
- `unstash`
- `archiveArtifacts`
- `artifactQuery`
- `publishHTML` (ha tenido superficie parcial; validar opciones)

### Coordinación

- `milestone`

### SCM

- `scmGit(...)` construye configuración.
- `checkout(...)` realiza el efecto y puede depender del plugin/capability disponible.
- No confundas builder y efecto.

### Directivas

- `options { timeout(...) }` y `timeout { }` son semánticas distintas.
- `directives { ... }` es una superficie de extensión; no debe usarse como escape hatch para lógica no soportada.

## Superficies en evolución

`when`, `post`, `agent/node` y otras superficies de compatibilidad han cambiado durante el roadmap semántico. Nunca las uses sólo porque otro CI las tenga.

Si una construcción no tiene carrier/interpreter real en la versión instalada:

```text
NO soporte
→ fail closed
→ rediseñar
```

No la emules mediante un body que siempre se ejecuta o metadata que nadie consume.

## Plugins de Steps

PipelineK es open-world en Steps:

```text
typed DSL façade
→ RegistryStepSpec / RegistryBlockSpec
→ StepRegistry
→ StepDefinition
→ capability admission
→ durable engine
→ typed result/events
```

Un plugin externo no obtiene un camino privilegiado.

El usuario puede aportar JARs con `--plugin-jar` cuando el plugin está construido para el SDK compatible.

## Eventos y replay

Una pipeline no es sólo una lista de comandos. El agente debe explotar:

- `RunStarted/RunFinished`;
- `StageStarted/Finished/Skipped`;
- `StepStarted/Finished/Failed`;
- eventos de timeout/retry/control cuando existan;
- identidad de run/sequence/causation;
- journal durable para replay/resume.

## Regla de diseño

Cuando PipelineK ya tiene una primitive tipada, úsala antes que shell artesanal:

```text
dir(...)          > sh("cd ... && ...")
withEnv(...)      > prefijar variables manualmente
withCredentials   > token en command line
timeout           > shell timeout ad-hoc
archiveArtifacts  > copiar a una carpeta sin contrato
```

Pero una primitive sólo merece usarse si aporta semántica real, replay, eventos, seguridad o composición.