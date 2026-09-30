# Creación y definición de pipelines

## 1. Extraer intención antes de escribir DSL

Inspecciona primero:

- `AGENTS.md`, ADRs y reglas de testing/release;
- wrappers y manifests: `gradlew`, `mvnw`, `package.json`, `Cargo.toml`, `pyproject.toml`, `Makefile`, `justfile`;
- comandos que los desarrolladores ejecutan realmente;
- CI existente sólo como fuente de intención: triggers, matrices, build, tests, artefactos, credenciales, publicación.

Produce un mapa breve:

```text
source/change
  -> validate/static
  -> compile/build
  -> unit/contract
  -> integration/UAT
  -> package
  -> release verification
```

No todas las fases deben existir. No introduzcas stages vacíos ni herramientas que el proyecto no usa.

## 2. Diseñar stages por responsabilidad

Un stage debe responder a una pregunta observable. Ejemplos útiles:

- Validate: ¿configuración/DSL/build files son válidos?
- Compile/Build: ¿el producto compila/se construye?
- Unit/Contract: ¿los contratos afectados pasan?
- Architecture/Static: ¿los fitness gates del repo pasan?
- Integration/UAT: ¿un flujo real funciona?
- Package: ¿se genera el artefacto?
- Release Verification: ¿el artefacto instalado se identifica y arranca correctamente?

Evita stages que sólo repitan nombres heredados del CI anterior.

## 3. Comandos: proyecto primero

Prefiere wrappers y scripts ya versionados por el proyecto (`./gradlew`, `./mvnw`, scripts de package manager, `cargo`, `just`, `make`). No sustituyas un wrapper por una instalación global sólo porque exista en el host.

Para repos poliglotas, usa `dir("subproject") { ... }` sólo si la versión instalada lo valida. Si no, usa paths explícitos.

## 4. DSL version-aware

PipelineK evoluciona. Antes de adoptar una construcción nueva:

1. comprueba `pipelinek version`;
2. busca un ejemplo ya usado por el propio repo;
3. escribe el cambio mínimo;
4. ejecuta `pipelinek validate pipeline.kts`;
5. cuando la semántica importe, ejecuta una sonda discriminante.

No deduzcas soporte porque una función aparezca en documentación histórica o porque el script compile de otra forma.

Especialmente sensibles: directivas declarativas, block steps, runtime-returning calls, environment/credentials, retry/timeout/parallel y builders que devuelven configuración.

Si la intención no tiene representación real, **fail closed o elimina la construcción**.

## 5. Plantilla inicial conservadora

Adapta, no copies ciegamente:

```kotlin
pipeline {
    stages {
        stage("Build") {
            sh("./project-wrapper build")
        }

        stage("Tests") {
            sh("./project-wrapper test")
        }
    }
}
```

Después:

```bash
pipelinek validate pipeline.kts
pipelinek run --workspace . pipeline.kts
```

El ejemplo de esta skill está en [minimal.pipeline.kts](../examples/minimal.pipeline.kts).

## 6. Testing eficiente para agentes

Durante desarrollo:

```text
cambio
→ tests afectados
→ contratos consumidores
→ pipeline/stage focal si existe
```

Frontera de integración/release:

```text
→ pipeline completo
→ artefacto real
→ UAT/release gates exigidos
```

No rebajes gates para conseguir verde. Si el pipeline completo tarda demasiado, mejora su arquitectura/caché/partición.

## 7. Estado fuera del repositorio

Por defecto:

```bash
repo_id="$(basename "$(git rev-parse --show-toplevel)")"
state="${XDG_STATE_HOME:-$HOME/.local/state}/pipelinek/${repo_id}"
mkdir -p "$state"

pipelinek run --workspace .   --db "$state/run.sqlite"   --control-root "$state/control"   pipeline.kts
```

Si el proyecto define otra ubicación, sigue esa autoridad.
