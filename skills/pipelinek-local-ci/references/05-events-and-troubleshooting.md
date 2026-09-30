# Eventos, outcomes y troubleshooting

PipelineK está orientado a eventos. Para un agente, los eventos son mejores que inferir estado desde texto libre.

## Jerarquía de evidencia

Para una ejecución:

1. proceso realmente ejecutado;
2. exit code;
3. evento terminal del run;
4. `StepFailed` / evento de fallo causal;
5. transcript/log redactado cuando haga falta;
6. journal durable sólo a través de APIs/CLI soportadas.

No leas SQLite directamente como contrato estable.

## Triage mínimo

### Compile/validation failure

Síntomas: no aparecen Steps, diagnóstico de compilación/DSL, exit no-cero.

Acción: corrige el pipeline, no el producto, salvo que la DSL aceptada/documentada falle contra una reproducción mínima.

### SCRIPT failure

Un `sh` terminó no-cero.

Acción: reproduce el comando en el mismo workspace/entorno si es seguro; identifica dependencia/toolchain/path; corrige el comando o el producto; no añadas `|| true` para obtener verde.

### Environment/tool missing

Distingue:

```text
producto defectuoso
vs
toolchain no provisionada
vs
version manager no resuelto
vs
workspace incorrecto
```

Los fallos de shims al ejecutarse fuera del root suelen indicar un `--workspace`/cwd incorrecto.

### Timeout/retry

No conviertas retry en solución genérica para un fallo determinista. Usa retry sólo para el contrato que lo necesita. Un timeout debe producir evidencia de cancelación/fallo; que el proceso termine después no convierte el run en éxito.

### Parallel

Cuando investigues ramas paralelas, usa sus identidades/events, no orden textual del stdout. La intercalación de salida es normal; colisión de identidad/control-root no lo es.

## Resultado contradictorio

Si observas:

```text
exit 0 + RunFinished failure
```

o:

```text
exit non-zero + RunFinished success
```

preserva ambos datos y repórtalo. No escondas la contradicción con un parser que sólo mire el valor favorable.

## Informe de fallo para otro agente

```text
PipelineK version/path:
repo SHA:
pipeline path:
workspace:
db/control-root:
stage/step:
event kind/failureKind:
command:
exit:
terminal outcome:
reproduction:
expected:
observed:
```

No incluyas secretos; conserva sólo valores redactados.
