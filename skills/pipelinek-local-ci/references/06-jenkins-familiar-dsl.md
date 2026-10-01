# DSL Jenkins-familiar: uso actual y objetivo de paridad

PipelineK busca una experiencia local familiar para usuarios de Jenkins Groovy Pipeline, pero **la paridad se acepta feature a feature**. Esta tabla es snapshot orientativo; `pipelinek validate` y la versión instalada son autoridad.

## Superficie preferible hoy

| Patrón | Estado orientativo | Uso |
|---|---|---|
| `pipeline / stages / stage` | estable | estructura |
| `echo`, `sh`, `error`, `sleep` | estable | pasos básicos |
| `writeFile`, `readFile`, `fileExists` | estable | filesystem relativo a ubicación de ejecución |
| `deleteDir`, `cleanWs` | estable con safety | raíz Attached protegida; Managed puede limpiar su raíz |
| `dir {}` | estable | deriva cwd scoped; no cambia workspace root/ownership |
| `withEnv {}` | estable | env scoped |
| `withCredentials {}` | estable | secretos tipados |
| `timeout {}` | estable | deadline block |
| `retry {}` | estable | reintentos |
| `waitUntil {}` | estable | polling body |
| `parallel { branch {} }` | estable | branches concurrentes |
| `archiveArtifacts` | estable | retención |
| `stash/unstash` | estable | transferencia intra-run |
| `milestone` | estable | coordinación ordinal |
| `timestamps` | estable | output decorator |
| `environment {}` | estable | declarative env |
| `options { timeout(...) }` | estable | stage-wide shell deadline |
| `catchError/warnError/unstable` | comportamiento estable, compatibilidad deprecada | no elegir para diseños nuevos sin necesidad Jenkins-compat |

## Usar con cautela

| Patrón | Estado |
|---|---|
| `checkout(scmGit(...))` | parcial; verificar plugin/versión |
| `publishHTML` | parcial; `keepAll=true` falla cerrado |
| `directives { directive(...) }` | experimental mientras evoluciona kernel |
| `registryStep/registryBlock` | experimental/plugin author surface |
| `pwd()/isUnix()` | runtime calls; `pwd()` observa el cwd efectivo |

## No usar como feature real todavía

| Jenkins-familiar | Situación |
|---|---|
| `post {}` | fail-closed hasta semántica runtime real |
| `when` / `whenCondition` | fail-closed; no evaluator de strings |
| `agent` | fail-closed; no allocator remoto |
| `node` | fail-closed en perfil actual |
| `git(...)` shortcut | fail-closed |
| `load` | sin handler |
| `ansiColor` | fail-closed actual |

## Workspace y cwd

En runtimes RP-034:

```text
invocation directory -> WorkspaceRoot Attached por defecto
pipeline.kts path     -> definición, no workspace
dir("x")              -> CurrentDirectory = WorkspaceRoot/x
```

`dir` no redefine raíz ni ownership y restaura cwd al salir. No conviertas una limpieza Jenkins en una limpieza ciega del checkout: `deleteDir/cleanWs` sobre la raíz Attached debe fallar cerrado. Para scratch destructible usa `pipelinek run --isolated ...`.

Consulta `09-workspaces-and-execution-location.md`.

## Patrones de composición

### Scope

```kotlin
dir("backend") {
    withEnv(listOf("CI=true")) {
        sh("./gradlew check")
    }
}
```

### Budget + retry

```kotlin
timeout(time = 15, unit = "MINUTES") {
    retry(count = 2) {
        sh("./mvnw -B -ntp verify")
    }
}
```

### Parallel

```kotlin
stage("checks") {
    parallel {
        branch("lint") { sh("npm run lint") }
        branch("test") { sh("npm test") }
    }
}
```

### Artifacts

```kotlin
stage("package") {
    sh("./gradlew assemble")
    stash(name = "jars", includes = "build/libs/*.jar")
    archiveArtifacts("build/libs/*.jar", allowEmptyArchive = false)
}
```

## Regla de migración

Si un Jenkinsfile depende de una feature no soportada, no la emules de modo que el pipeline parezca verde. Mantén esa responsabilidad externa o rediseña el flujo hasta que exista un carrier/interpreter real.
