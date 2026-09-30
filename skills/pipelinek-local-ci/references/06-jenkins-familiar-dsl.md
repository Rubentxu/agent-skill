# DSL Jenkins-familiar: uso actual y objetivo de paridad

PipelineK busca una experiencia local familiar para usuarios de Jenkins Groovy Pipeline, pero **la paridad se acepta feature a feature**. Esta tabla es snapshot orientativo; `pipelinek validate` y la versión instalada son autoridad.

## Superficie preferible hoy

| Patrón | Estado orientativo | Uso |
|---|---|---|
| `pipeline / stages / stage` | estable | estructura |
| `echo`, `sh`, `error`, `sleep` | estable | pasos básicos |
| `writeFile`, `readFile`, `fileExists`, `deleteDir`, `cleanWs` | estable | workspace |
| `dir {}` | estable | cwd scoped |
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
| `pwd()/isUnix()` | runtime calls; verificar contexto |

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
