# Migrar Jenkins / GitHub Actions / GitLab CI a PipelineK

Migra **política de entrega**, no sintaxis.

## Inventario

Por cada job/stage registra: trigger, cwd, toolchain, build, tests, matrix, cache, secrets, artifacts, publish/deploy y condición.

Clasifica cada pieza:

```text
PORTABLE_LOCAL      → PipelineK
REMOTE_TRIGGER      → workflow fino opcional
MATRIX_EXTERNAL     → hosted/harness si la máquina local no lo cubre
RELEASE/PUBLISH     → release train/harness según gobernanza
PROVIDER_PLUMBING   → eliminar
```

## GitHub Actions

No traduzcas automáticamente `actions/checkout`, `setup-*`, caches cloud o upload/download artifacts. Pregunta qué capacidad representan.

Ejemplo:

```text
checkout → setup-java → ./gradlew check → upload jar
```

puede convertirse localmente en:

```kotlin
pipeline {
    stages {
        stage("verify") { sh("./gradlew --no-daemon check") }
        stage("package") {
            sh("./gradlew --no-daemon assemble")
            archiveArtifacts("build/libs/*.jar", allowEmptyArchive = false)
        }
    }
}
```

si el repo contiene `gradlew` y esos tasks.

## Jenkins Pipeline

Mapeo de intención actual:

| Jenkins | PipelineK |
|---|---|
| `pipeline/stages/stage` | familiar y soportado |
| `sh`, `echo`, `error`, `sleep` | soportado |
| `dir`, `withEnv`, `withCredentials` | soportado |
| `timeout`, `retry`, `waitUntil` | soportado |
| `parallel` | soportado con shape canónica |
| `stash/unstash`, `archiveArtifacts`, `milestone` | soportado |
| `post` | no usar hasta runtime semantics reales |
| declarative `when` / legacy `whenCondition` | no usar hasta soporte real |
| `agent` / `node` remoto | no equivale a allocator local; fail-closed actual |
| Jenkins `git` shortcut | no usar; checkout SCM actual es parcial/plugin-dependent |
| controller jobs (`build(job)`) | responsabilidad externa |

Consulta `06-jenkins-familiar-dsl.md` antes de migrar un Jenkinsfile.

## Condicionales

No sustituyas un `when` no soportado por una función que simplemente ejecuta el body. Mientras la versión instalada no tenga predicado declarativo real, rediseña la selección fuera del pipeline o como Kotlin/command flow sólo si su semántica está certificada para ese caso.

## Hosted CI residual

Una arquitectura válida es:

```text
developer / coding agent
        ↓
PipelineK local = CI authority
        ↓
artifact/evidence
        ↓
optional remote trigger
        ↓
matrix / release harness / deploy
```

El remoto no vuelve a definir qué tests constituyen CI.

## Gate de sustitución

No elimines el CI anterior hasta demostrar:

1. pipeline nueva valida;
2. positivo real;
3. negativo discriminante;
4. gates/artifacts equivalentes identificados;
5. secretos no degradados;
6. responsabilidades que siguen remotas documentadas;
7. humanos y agentes pueden reproducir localmente.
