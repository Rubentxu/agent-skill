# Filtros de eventos PipelineK para agentes

PipelineK emite NDJSON tipado por stdout. Un agente debería conservar el stream completo como evidencia y derivar vistas pequeñas para decidir qué hacer.

## Regla

**Filtrar no significa descartar evidencia.**

Patrón correcto:

```bash
set -o pipefail

events="$(mktemp)"
pipelinek run \
  --workspace . \
  --db "$STATE/run.sqlite" \
  --control-root "$STATE/control" \
  pipeline.kts | tee "$events"

pipeline_rc=${PIPESTATUS[0]}
```

El fichero temporal contiene el stream completo. Los filtros siguientes son **proyecciones** sobre él.

No hagas:

```bash
pipelinek run pipeline.kts | jq 'select(.kind == "RunFinished")'
```

como única evidencia: perderías los eventos causales y, sin `pipefail`, además podrías perder el exit real del proceso.

## Outcome terminal

```bash
jq -s -e '
  [.[] | select(.kind == "RunFinished")] as $runs
  | ($runs | length) > 0
    and ($runs[-1].outcome == "success")
' "$events"
```

Resumen legible:

```bash
jq -s -r '
  [.[] | select(.kind == "RunFinished")] | last
  | "run=\(.runId) outcome=\(.outcome) seq=\(.sequence)"
' "$events"
```

## Primer fallo causal

```bash
jq -s -c '
  [.[] | select(.kind == "StepFailed")] | first // empty
' "$events"
```

Vista compacta:

```bash
jq -r '
  select(.kind == "StepFailed")
  | [.sequence, .failureKind, .stepName, .message]
  | @tsv
' "$events" | head -1
```

No uses sólo el último error: un fallo secundario de cleanup puede ocultar el fallo causal anterior.

## Timeline de stages

```bash
jq -r '
  select(.kind == "StageStarted" or .kind == "StageFinished")
  | [.sequence, .kind, (.stageName // ""), (.outcome // "")]
  | @tsv
' "$events"
```

## Vista agentic mínima

Útil para ciclos fix/rerun sin cargar todo el transcript:

```bash
jq -c '
  select(
    .kind == "CompilationFinished"
    or .kind == "StageFinished"
    or .kind == "StepFailed"
    or .kind == "RunFinished"
  )
' "$events"
```

El agente conserva el fichero completo y usa esta proyección para decidir.

## Sólo eventos de control

```bash
jq -c '
  select(
    .kind == "RetryAttemptStarted"
    or .kind == "RetryAttemptFinished"
    or .kind == "TimeoutScheduled"
    or .kind == "TimeoutTriggered"
    or .kind == "ParallelBranchStarted"
    or .kind == "ParallelBranchFinished"
    or .kind == "WaitUntilPolled"
    or .kind == "WaitUntilCompleted"
  )
' "$events"
```

Sirve para diagnosticar control flow sin parsear stdout humano.

## Credenciales: sólo metadatos de lifecycle

```bash
jq -c '
  select(
    .kind == "CredentialBound"
    or .kind == "CredentialUsed"
    or .kind == "CredentialUnbound"
  )
  | {
      sequence,
      kind,
      credentialsId,
      purpose
    }
' "$events"
```

Nunca añadas filtros que intenten imprimir valores de entorno/material secretos. El contrato de eventos debe contener metadata, no bytes secretos.

## Verificar balance de bindings

Para una credencial concreta:

```bash
CRED_ID="registry-token"

jq -s --arg id "$CRED_ID" '
  {
    bound:   ([.[] | select(.kind=="CredentialBound"   and .credentialsId==$id)] | length),
    used:    ([.[] | select(.kind=="CredentialUsed"    and .credentialsId==$id)] | length),
    unbound: ([.[] | select(.kind=="CredentialUnbound" and .credentialsId==$id)] | length)
  }
' "$events"
```

No presupongas que `used == bound`: depende de la operación. Sí investiga un binding sin su cleanup terminal cuando el contrato exige `Unbound`.

## Compilación/DSL

```bash
jq -c '
  select(.kind == "CompilationFinished")
  | {
      sequence,
      diagnostics
    }
' "$events"
```

Si no aparece ningún `StepStarted`, empieza por esta vista.

## Parallel

No uses el orden textual del stdout para atribuir trabajo a ramas. Usa identidades y eventos:

```bash
jq -r '
  select(.kind | startswith("ParallelBranch"))
  | [.sequence, .kind, (.branchName // ""), (.outcome // "")]
  | @tsv
' "$events"
```

La intercalación de logs es normal. Duplicación de identidad/sequence no lo es.

## Guard de contradicción

No permitas un falso verde entre shell y eventos:

```bash
terminal="$(jq -s -r '[.[] | select(.kind=="RunFinished")] | last | .outcome // "missing"' "$events")"

printf 'pipeline_rc=%s terminal=%s\n' "$pipeline_rc" "$terminal"

if [ "$pipeline_rc" -eq 0 ] && [ "$terminal" != "success" ]; then
  echo "PIPELINEK_CONTRADICTION: exit=0 but terminal=$terminal" >&2
  exit 70
fi

if [ "$pipeline_rc" -ne 0 ] && [ "$terminal" = "success" ]; then
  echo "PIPELINEK_CONTRADICTION: exit=$pipeline_rc but terminal=success" >&2
  exit 70
fi
```

No conviertas la contradicción en el resultado que más convenga.

## Sin jq

No hagas que `jq` sea requisito oculto. Si no existe:

- conserva NDJSON completo;
- usa Python stdlib sólo si Python ya forma parte del toolchain;
- o informa que la proyección compacta no está disponible.

Ejemplo Python:

```bash
python3 - "$events" <<'PY'
import json, sys
events = [json.loads(line) for line in open(sys.argv[1]) if line.strip()]
terminal = [e for e in events if e.get("kind") == "RunFinished"]
failures = [e for e in events if e.get("kind") == "StepFailed"]
print("terminal:", terminal[-1].get("outcome") if terminal else "missing")
if failures:
    f = failures[0]
    print("first failure:", f.get("failureKind"), f.get("message"))
PY
```

## Output contract para otro agente

Entrega como máximo este resumen y conserva el stream original:

```text
pipelinek path/version:
runId:
pipeline exit:
terminal outcome:
first causal failure:
failed stage/step:
control-flow evidence:
credential lifecycle metadata:
full NDJSON path:
next action:
```
