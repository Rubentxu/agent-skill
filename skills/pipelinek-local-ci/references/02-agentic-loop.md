# Bucle agentic de CI local

PipelineK debe dar al agente una señal ejecutable y reproducible, no una opinión sobre si el cambio “parece correcto”.

## Ciclo normal

```text
inspect
  ↓
change
  ↓
affected verification
  ↓
pipelinek validate
  ↓
pipelinek run
  ↓
typed outcome/events
  ├─ success → cierre/evidencia
  └─ failure → localizar causa → corregir → rerun/resume
```

## Preflight

Captura:

```bash
git rev-parse HEAD
git status --short
command -v pipelinek
readlink -f "$(command -v pipelinek)"
pipelinek version
pipelinek doctor
```

Si el path/version no es el esperado, no continúes como si la ejecución acreditase el proyecto; ve a `04-version-resolution.md`.

## Validate

```bash
pipelinek validate pipeline.kts
```

Cierre: exit observado y diagnóstico, no sólo “no imprimió error”.

## Run

Usa `--workspace` de forma explícita y state fuera del repo:

```bash
state="${XDG_STATE_HOME:-$HOME/.local/state}/pipelinek/$(basename "$PWD")"

pipelinek run   --workspace .   --db "$state/run.sqlite"   --control-root "$state/control"   pipeline.kts
```

No reutilices una DB de otro proyecto.

## Señal de éxito

Usa dos canales cuando estén disponibles:

1. exit code real;
2. evento terminal `RunFinished` y su `outcome`.

Si se contradicen, eso es un defecto/limitación a investigar; no elijas silenciosamente el canal favorable.

Para automatización, captura stdout sin perder el exit:

```bash
set -o pipefail
pipelinek run --workspace . pipeline.kts | tee /tmp/pipelinek-events.ndjson
rc=${PIPESTATUS[0]}
```

Después localiza el evento terminal con las herramientas disponibles. No hagas depender la skill de `jq` si no está instalado.

## Failure-driven repair

Ante fallo:

1. encuentra el primer `StepFailed` causal, no el último mensaje ruidoso;
2. registra `failureKind`, mensaje, stage/step y comando;
3. decide si el fallo es producto, test, entorno, credencial o pipeline;
4. corrige la causa mínima;
5. ejecuta primero la prueba/step afectado;
6. vuelve al gate exigido.

No conviertas automáticamente un fallo de herramienta ausente en cambio de código.

## Resume vs rerun

Si el contrato de la versión instalada soporta replay durable:

- **resume**: continuar un run interrumpido usando el mismo DB/control-root;
- **rerun**: reejecutar deliberadamente tras cambiar entradas/código.

No uses resume después de modificar una semántica cuyo fingerprint/replay contract no entiendes. Cuando haya duda, crea estado limpio o usa el modo de rerun documentado por la versión instalada.

## Cierre agentic

Un cierre útil contiene:

```text
HEAD/base:
pipelinek resolved path:
pipelinek version:
pipeline:
command:
exit:
terminal outcome:
tests/stages realmente ejecutados:
skips/bloqueos:
next action:
```

Un recibo previo, un workflow configurado o una pipeline que sólo valida sintaxis no acreditan el HEAD actual.
