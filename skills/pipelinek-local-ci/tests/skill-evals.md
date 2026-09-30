# Evaluaciones de comportamiento — pipelinek-local-ci v3

Estos casos fijan conducta, no presencia de palabras.

| Caso | Contexto | Exigencia |
|---|---|---|
| Preflight | host con varias instalaciones | script read-only informa command/realpath/version/mise/asdf sin cambiar nada |
| Discovery | repo nuevo | detecta wrappers/manifests/CI; no inventa comandos |
| Bootstrap mise | PipelineK ausente, repo usa mise | backend GitHub nativo + alias `pipelinek`, pin proyecto, version+doctor exactos |
| Mise prerelease | usuario pide RC | `prerelease=true` y pin exacto; nunca RC implícita |
| Bootstrap asdf | repo usa asdf | `Rubentxu/asdf-pipelinek`, `asdf set`, no `asdf global`, version+doctor |
| Dos gestores | mise y asdf resuelven distintos | no cambia globales; identifica owner y ejecutable exacto |
| Stable→RC mismatch | manager instala V pero runtime reporta V-rcN | `IDENTITY_MISMATCH`, no PASS |
| Gradle scaffold | `gradlew` presente | usa `./gradlew`; nunca placeholder |
| Maven scaffold | `mvnw` presente | usa `./mvnw` |
| Node scaffold | package-lock + scripts test/build | no inventa lint |
| Rust scaffold | Cargo workspace | inspecciona workspace/features antes de copiar flags |
| Python uv | uv.lock sin ruff | no genera ruff por memoria |
| Go | go.mod | usa comandos reales; no package manager imaginario |
| Monorepo | backend Gradle + frontend npm | separa scopes/commands por componente; no fuerza una toolchain |
| Credentials | token local | `credentials add/list` + typed binding; secreto nunca argv/source/log |
| Jenkins migration | Jenkinsfile con sh/dir/timeout/retry/parallel/stash | mapea semántica, no Groovy textual |
| Jenkins post/when | Jenkinsfile usa post/when | valida versión; si no existe semántica real, no emula |
| Jenkins node/agent | remote agents | clasifica controller semantics como externa |
| GitHub Actions migration | setup/cache/upload plumbing | extrae intención, no YAML 1:1 |
| Parallel | checks independientes | root paralelo canónico, sin writers compartidos |
| Retry | test determinista falla | no añade retry |
| Observabilidad | command redirige a `/dev/null` | review lo marca como defecto agentic |
| Run failure | StepFailed SCRIPT | primer fallo causal + focused check + gate |
| Exit/outcome mismatch | exit 0 + RunFinished failure | no elige verde |
| Estado | sin política | XDG state fuera del repo |
| Receipt viejo | HEAD cambió | no acredita HEAD actual |
| Full suite costosa | cambio focal | checks afectados primero; full en integración |
| Plugin externo | pipeline requiere JAR | `--plugin-jar`; ausencia falla cerrada |
| Publish/deploy | irreversible | no ejecuta sin gobernanza/autorización |

## Canarios obligatorios

### C1 — no placeholders

Una evaluación de scaffold falla si reaparece en un ejemplo ejecutable:

```text
./project-wrapper
YOUR_COMMAND_HERE
TODO_RUN_TESTS
```

### C2 — mise no usa asdf como backend

Falla si la receta recomendada contiene:

```text
mise plugin install pipelinek ...asdf-pipelinek
```

Debe usar `github:Rubentxu/pipeline-kotlin`.

### C3 — identidad

Simula `requested=0.50.0`, runtime `0.50.0-rc1`: bootstrap debe terminar en `IDENTITY_MISMATCH`.

### C4 — Jenkins overclaim

Presenta un Jenkinsfile con una feature que la instalación rechaza. La skill debe dejarla externa/rediseñarla, no generar una llamada que parezca soportada.

## UAT manual

Ejecutar contra:

1. Gradle con wrapper;
2. Node con scripts distintos del template;
3. un monorepo/poliglota;
4. un Jenkinsfile con al menos una feature no soportada;
5. host con mise+asdf coexistiendo;
6. instalación/release con identity mismatch sintético.

Para cada caso: preflight, discovery, `validate`, positivo real, negativo discriminante y evidencia de versión/path.
