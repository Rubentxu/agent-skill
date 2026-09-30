# Árbol de decisión para adoptar PipelineK

## 1. Detecta el modo

```text
¿pipelinek existe y resuelve una versión inequívoca?
├─ no  → bootstrap
└─ sí
   ├─ no hay pipeline.kts → scaffold
   ├─ hay pipeline.kts y piden calidad → review
   ├─ piden verificar cambio → run
   ├─ hay Jenkinsfile/.github/.gitlab-ci → migrate
   └─ hay fallo → diagnose
```

## 2. Detecta stack por evidencia

| Evidencia | Comandos candidatos | Regla |
|---|---|---|
| `gradlew` | `./gradlew ...` | wrapper antes que Gradle global |
| `mvnw` | `./mvnw ...` | wrapper antes que Maven global |
| `package-lock.json` | `npm ci`, scripts de `package.json` | no inventar `lint/test/build`: leer scripts |
| `pnpm-lock.yaml` | `pnpm install --frozen-lockfile`, scripts | usar sólo si pnpm está provisionado |
| `yarn.lock` | yarn del repo | detectar versión/config |
| `pyproject.toml` + `uv.lock` | `uv sync --frozen`, `uv run ...` | comprobar tools definidas |
| `poetry.lock` | `poetry install`, `poetry run ...` | comprobar scripts/tools |
| `Cargo.toml` | `cargo fmt/clippy/test/build` | respetar workspace/features |
| `go.mod` | `go vet/test/build` | respetar módulos/build tags |
| `Makefile` | targets reales de `make` | inspeccionar target antes de usar |
| `justfile` | recipes reales de `just` | `just --list` si disponible |

Si hay varios, trátalo como monorepo/poliglota y diseña stages por componente. No presupongas que `files:` o un gestor cambia el cwd de los procesos.

## 3. Elige forma de pipeline

```text
barato + secuencial     → stages lineales
checks independientes   → stage con parallel { branch(...) }
operación flaky real    → retry(count) { ... }
operación con presupuesto → timeout(time, unit) { ... }
subdirectorio          → dir(path) { ... }
env temporal           → withEnv(...) { ... }
secreto                → withCredentials(...) { ... }
salida entre stages    → stash / unstash
salida final           → archiveArtifacts
```

No uses `parallel` por estética: branches deben ser independientes. No uses retry para esconder defectos deterministas.

## 4. Fast lane / slow lane

Durante desarrollo el agente ejecuta tests afectados y stages focales. En integración ejecuta la pipeline completa. Certificación pesada, matrices externas, distribución o release harness permanecen fuera si el proyecto ya las separa.
