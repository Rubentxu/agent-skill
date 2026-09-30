# Bucle agentic: PipelineK como autoridad CI local

## Lanes

| Momento | Qué ejecutar | Objetivo |
|---|---|---|
| edición | test/check afectado | feedback rápido |
| bloque funcional | consumidores + stage relevante | detectar integración local |
| integración | `pipelinek validate` + pipeline completa | gate del HEAD |
| release | pipeline + gates/release harness definidos por el proyecto | evidencia final |

No conviertas la full suite en respuesta refleja tras cada edición, ni cierres un bloque sólo con tests focales si la política exige integración.

## Preflight

```bash
git rev-parse HEAD
git status --short
command -v pipelinek
readlink -f "$(command -v pipelinek)"
pipelinek version
pipelinek doctor
```

Si hay mise/asdf conflictivos, detente y usa `04-version-resolution.md`.

## Estado durable fuera del repo

```bash
root="$(git rev-parse --show-toplevel)"
repo_id="$(basename "$root")"
state="${XDG_STATE_HOME:-$HOME/.local/state}/pipelinek/${repo_id}"
mkdir -p "$state"
```

## Validate

```bash
pipelinek validate "$root/pipeline.kts"
```

`validate` acredita forma/compilación de DSL, no comportamiento de Steps.

## Run observable

```bash
set -o pipefail
pipelinek run \
  --workspace "$root" \
  --db "$state/run.sqlite" \
  --control-root "$state/control" \
  "$root/pipeline.kts" \
  | tee "$state/events.ndjson"
rc=${PIPESTATUS[0]}
printf 'pipelinek_exit=%s\n' "$rc"
```

stderr queda visible en terminal; stdout conserva la secuencia de eventos. No redirijas todo a un fichero invisible al agente.

## Oracle

Usa conjuntamente:

1. exit real;
2. `RunFinished.outcome`;
3. primer `StepFailed`/fallo causal;
4. eventos específicos de block/directive cuando la semántica dependa de ellos.

Si exit y outcome se contradicen: **FAIL/INVESTIGATE**, no elijas el favorable.

## Auto-fix loop

```text
failure
  ↓
classify
  ├─ code/test bug
  ├─ pipeline DSL bug
  ├─ dependency/toolchain
  ├─ environment/workspace
  ├─ credentials
  ├─ timeout/concurrency
  └─ PipelineK defect/unknown
  ↓
smallest causal fix
  ↓
affected check
  ↓
required PipelineK gate
```

Un rerun de infraestructura sólo es válido si hay evidencia de causa transitoria. No conviertas flaky en `retry` por defecto.

## Resume / rerun

- `--resume`: para un run durable interrumpido cuando el contrato de la instalación lo soporte.
- `--rerun`: nueva ejecución deliberada tras cambiar inputs/código.

No uses simultáneamente dos `--resume` contra el mismo run/state salvo que estés ejecutando una prueba explícita de concurrencia: ownership cross-process ha sido una frontera histórica sensible.

## Reporte de cierre

```text
HEAD:
PipelineK realpath/version:
pipeline:
workspace:
gate:
exit:
RunFinished:
first causal failure:
stages executed/skipped:
evidence path:
remaining blocker:
```
