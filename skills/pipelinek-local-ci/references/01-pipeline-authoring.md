# Diseñar y crear `pipeline.kts`

## Regla cero: cero placeholders ejecutables

`./project-wrapper` no existe salvo que el repositorio tenga exactamente ese archivo. Nunca pongas un comando ficticio para completar un template.

Antes de escribir DSL enumera comandos **observados**:

```bash
test -x ./gradlew && echo gradle-wrapper
test -x ./mvnw && echo maven-wrapper
test -f package.json && cat package.json
test -f pyproject.toml && sed -n '1,220p' pyproject.toml
test -f Cargo.toml && sed -n '1,220p' Cargo.toml
test -f go.mod && cat go.mod
test -f Makefile && sed -n '1,220p' Makefile
test -f justfile && sed -n '1,220p' justfile
```

## Diseña por preguntas observables

- **Validate/Static:** ¿configuración, formato, lint y tipos son válidos?
- **Build:** ¿el producto compila/construye?
- **Unit/Contract:** ¿contratos rápidos pasan?
- **Integration/UAT:** ¿flujo real pasa?
- **Package:** ¿se produjo el artefacto correcto?
- **Release Verification:** ¿artefacto instalado se identifica/arranca? Sólo cuando pertenezca a este repo.

No copies el número de jobs del CI anterior. Un stage existe si separa una responsabilidad, un presupuesto o una semántica de fallo.

## Patrón mínimo real

Cuando aún no conoces comandos del proyecto, empieza sólo con una pipeline inocua:

```kotlin
pipeline {
    stages {
        stage("preflight") {
            echo("PipelineK is wired to this repository")
        }
    }
}
```

Después reemplaza/amplía usando comandos observados. Nunca presentes este smoke como CI completa.

## Composición Jenkins-familiar

Cuando la instalación los soporte, usa blocks en lugar de shell artesanal:

```kotlin
stage("verify") {
    withEnv(listOf("CI=true")) {
        timeout(time = 20, unit = "MINUTES") {
            retry(count = 2) {
                sh("./gradlew --no-daemon check")
            }
        }
    }
}
```

Para checks independientes:

```kotlin
stage("checks") {
    parallel {
        branch("lint") { sh("npm run lint") }
        branch("test") { sh("npm test") }
    }
}
```

En la forma canónica actual, un stage `parallel` no mezcla siblings fuera del root paralelo.

## Artefactos

Salida temporal intra-run:

```kotlin
stash(name = "compiled", includes = "build/libs/*.jar")
```

y posteriormente:

```kotlin
unstash(name = "compiled")
```

Retención final:

```kotlin
archiveArtifacts(
    artifacts = "build/libs/*.jar",
    allowEmptyArchive = false,
)
```

No uses `publishHTML(keepAll=true)` sin verificar: esa opción es parcial/fail-closed en la superficie actual.

## Variables y secretos

Variables no secretas:

```kotlin
withEnv(listOf("CI=true", "MODE=test")) {
    sh("./gradlew check")
}
```

Para credenciales usa bindings soportados y no hagas `echo` del secreto. Consulta `07-security.md`.

## Version-aware DSL

Tras cada cambio estructural:

```bash
pipelinek validate pipeline.kts
```

Si el construct falla, contrasta `06-jenkins-familiar-dsl.md` y la versión real. No reemplaces `when/post/agent` no soportados por una simulación silenciosa.

## Templates

Los ejemplos bajo `examples/` son starters de intención. Antes de copiarlos:

1. confirma la herramienta/wrapper;
2. confirma cada script/target;
3. adapta paths y artefactos;
4. valida DSL;
5. ejecuta un positivo y un negativo discriminante.
