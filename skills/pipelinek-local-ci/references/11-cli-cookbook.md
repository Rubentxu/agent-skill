# CLI cookbook para agentes

## Preflight

```bash
bash <skill>/scripts/pipelinek-preflight.sh
pipelinek version
pipelinek doctor
```

## Validar DSL

```bash
pipelinek validate pipeline.kts
```

Validar no ejecuta Steps.

## Run durable

```bash
root="$(git rev-parse --show-toplevel)"
state="${XDG_STATE_HOME:-$HOME/.local/state}/pipelinek/$(basename "$root")"
mkdir -p "$state"

set -o pipefail
pipelinek run \
  --workspace "$root" \
  --db "$state/run.sqlite" \
  --control-root "$state/control" \
  "$root/pipeline.kts" | tee "$state/events.ndjson"
rc=${PIPESTATUS[0]}
```

Usa exit + `RunFinished.outcome`.

## Rerun tras modificar inputs/código

```bash
pipelinek run --workspace "$root" \
  --db "$state/run.sqlite" \
  --control-root "$state/control" \
  --rerun "$root/pipeline.kts"
```

## Resume tras interrupción

```bash
pipelinek run --workspace "$root" \
  --db "$state/run.sqlite" \
  --control-root "$state/control" \
  --resume "$root/pipeline.kts"
```

No lances dos `--resume` simultáneos sobre el mismo run/state salvo prueba explícita de concurrencia.

## Credenciales

```bash
pipelinek credentials list
pipelinek credentials add --kind secret-text registry-token
pipelinek credentials rotate --kind secret-text registry-token
pipelinek credentials remove registry-token
```

Nunca introduzcas el secreto en argv; la entrada de `add/rotate` es interactiva.

Si el proyecto usa store alternativo:

```bash
export PIPELINE_CREDENTIALS_STORE="$state/credentials.bin"
```

## Plugins externos

Cuando el proyecto entrega un plugin JAR compatible:

```bash
pipelinek run \
  --workspace "$root" \
  --plugin-jar /absolute/path/plugin.jar \
  "$root/pipeline.kts"
```

El plugin debe estar presente para compilación/runtime; un plugin ausente debe fallar cerrado, no degradar silenciosamente.

## Fallos

- exit `2`: normalmente invocación/compilación/admission en la línea moderna; lee el diagnóstico.
- exit `1`: runtime/pipeline failure.
- exit `0`: exige también outcome coherente si la versión expone NDJSON terminal.

No universalices códigos históricos de una versión antigua: observa la versión instalada.
