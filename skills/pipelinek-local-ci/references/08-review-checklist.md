# Checklist de review de una pipeline PipelineK

El modo `review` no modifica por defecto. Produce evidencia por categoría y sólo aplica cambios si el usuario lo pide o el encargo ya incluye corrección.

## Categorías

| Categoría | PASS | WARN/FAIL típicos |
|---|---|---|
| Identity | versión/path inequívocos | shim ambiguo, runtime != requested |
| Commands | todos existen en el repo/toolchain | placeholder, script/target inventado |
| DSL honesty | constructs soportados y validados | `post/when/agent/node/git` usados como si fueran reales |
| Stage anatomy | responsabilidad clara | mega-stage, stages ornamentales |
| Parallelism | branches independientes | writers compitiendo por el mismo output |
| Failure semantics | rojo permanece rojo | `|| true`, retry sobre fallo determinista |
| Observability | stdout/stderr/eventos utilizables | quiet, `/dev/null`, file-only logs |
| Durability | state fuera del repo y ownership entendido | DB compartida entre proyectos, resume concurrente accidental |
| Credentials | binding/store o ASV con postura explícita | secretos en argv/log/artifact; llamar secretless a env/file |
| Secretless boundary | signer/proxy/session mantiene bytes fuera del child cuando se exige | agent consulta Secret Service/KeePass/ASV para obtener valor |
| Event projections | NDJSON completo preservado + vistas compactas | filtro destruye evidencia o oculta exit/outcome |
| Artifacts | stash/archive con consumidor claro | duplicación, allowEmpty que oculta fallo |
| Fast/slow lanes | checks focales vs integración/release delimitados | full suite tras cada edición o CI remoto duplicado |
| Migration | política única | Jenkins/Actions y PipelineK divergen |

## Procedimiento

1. Resuelve PipelineK y registra versión.
2. Ejecuta `pipelinek validate`.
3. Lee pipeline y comandos referenciados.
4. Comprueba que los wrappers/scripts/targets existen.
5. Revisa cada categoría y marca `PASS`, `WARN` o `FAIL` con evidencia concreta.
6. Si hay autenticación, clasifica la postura: strong-secretless / short-lived / isolated / process exposure.
7. Si es seguro y está pedido, ejecuta la pipeline y contrasta outcome/eventos; conserva el NDJSON completo antes de filtrar.
8. Prioriza tres cambios por impacto en corrección, feedback agentic y mantenibilidad.

## Salida

```text
Pipeline: pipeline.kts
PipelineK: <realpath> / <version>
Validation: PASS|FAIL

Identity: PASS|WARN|FAIL — evidencia
Commands: ...
DSL honesty: ...
Stage anatomy: ...
Parallelism: ...
Failure semantics: ...
Observability: ...
Durability: ...
Credentials: ...
Secretless boundary: ...
Event projections: ...
Artifacts: ...
Fast/slow lanes: ...
Migration: ...

Top 3 fixes:
1. ...
2. ...
3. ...
```

Una pipeline que compila pero contiene una intención descartada o una feature unsupported es `FAIL`, no `WARN`.