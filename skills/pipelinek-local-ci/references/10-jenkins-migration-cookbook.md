# Jenkins → PipelineK cookbook

PipelineK persigue familiaridad y paridad local con Jenkins Pipeline, pero la migración debe seguir **semántica observable**, no equivalencia textual. La versión instalada manda.

## Estructura

Jenkins:

```groovy
pipeline {
  stages {
    stage('verify') {
      steps { sh './gradlew check' }
    }
  }
}
```

PipelineK:

```kotlin
pipeline {
    stages {
        stage("verify") {
            sh("./gradlew check")
        }
    }
}
```

PipelineK no necesita un `steps {}` ornamental en la forma actual.

## Scopes

Jenkins:

```groovy
dir('backend') {
  withEnv(['CI=true']) {
    sh './gradlew check'
  }
}
```

PipelineK:

```kotlin
dir("backend") {
    withEnv(listOf("CI=true")) {
        sh("./gradlew check")
    }
}
```

## Timeout + retry

```kotlin
timeout(time = 15, unit = "MINUTES") {
    retry(count = 2) {
        sh("./mvnw -B -ntp verify")
    }
}
```

Retry sólo para fallos potencialmente transitorios; no para assertions/compilación deterministas.

## Parallel

Jenkins `parallel` se expresa como un único root paralelo dentro del stage:

```kotlin
stage("checks") {
    parallel {
        branch("lint") { sh("npm run lint") }
        branch("test") { sh("npm test") }
    }
}
```

Las ramas deben ser independientes en outputs/cwd/estado.

## Artifacts

```kotlin
stage("package") {
    sh("./gradlew assemble")
    stash(name = "jars", includes = "build/libs/*.jar")
    archiveArtifacts(
        artifacts = "build/libs/*.jar",
        allowEmptyArchive = false,
    )
}
```

`stash/unstash` es transporte intra-run; `archiveArtifacts` es retención final.

## Credentials

Jenkins `withCredentials` se migra a bindings tipados, no a secretos inline:

```kotlin
withCredentials(
    StepSpec.CredentialsBinding.string("registry-token", "REGISTRY_TOKEN")
) {
    sh("./scripts/publish-using-env.sh")
}
```

El script consumidor lee `REGISTRY_TOKEN`; nunca imprime el valor.

## Error shaping

Cuando la versión instalada lo soporte:

```kotlin
catchError(buildResult = "UNSTABLE", stageResult = "UNSTABLE", message = "quality degraded") {
    sh("./scripts/quality-check.sh")
}
```

No uses `catchError` para ocultar un gate obligatorio. `warnError`/resultado unstable deben aparecer en outcome/eventos.

## Declarative environment/options

PipelineK moderno puede soportar `environment {}` y `options { timeout(...) }`, pero son semánticas distintas de `withEnv {}` y `timeout {}`. Valida la instalación y no intercambies ambas formas como si fueran aliases.

## Features que exigen especial cuidado

- `when/post/agent/node/git/load/ansiColor`: históricamente han pasado por estados fail-closed/partial. Nunca las migres por memoria; confirma la versión instalada y `pipelinek validate`.
- `checkout(scmGit(...))`: constructor SCM y efecto checkout son cosas distintas; no descartes el builder.
- `pwd()/isUnix()`: runtime-returning calls, no simples builders declarativos.
- plugins externos: pueden requerir `--plugin-jar`; no hardcodees keys de plugin en core.

## Controller semantics

No hay equivalencia automática para capacidades de controller Jenkins:

- `build(job: ...)`;
- queue/controller orchestration;
- remote node allocation;
- Jenkins-specific plugins;
- approvals/input administrados por controller.

Clasifica esas responsabilidades como `REMOTE_ORCHESTRATION`, `RELEASE_HARNESS` o integración externa hasta que PipelineK tenga carrier/interpreter real.

## Regla de futuro

Cuando PipelineK implemente nuevas directivas equivalentes a Jenkins, actualiza el mapa a partir de la superficie certificada/instalada. No mantengas una lista estática más fuerte que el binario real.
