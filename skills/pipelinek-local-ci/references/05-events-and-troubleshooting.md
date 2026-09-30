# Eventos, observabilidad y auto-diagnóstico

Un coding agent necesita fallos **legibles y causales**. La salida que sólo vive en un artifact o fichero oculto no sirve para un loop autónomo.

## Regla de visibilidad

- no `> /dev/null`;
- no `--quiet/-q` en comandos cuyo fallo hay que diagnosticar;
- no `cmd > log 2>&1` sin mantener también salida visible;
- no `|| true` para convertir error en PASS;
- si hay pipe, `set -o pipefail`.

PipelineK emite hechos tipados. Prioriza:

```text
RunFinished
StageStarted/Finished/Skipped
StepStarted/Finished/Failed
block/directive events (Retry*, Timeout*, CatchError*, ...)
credential lifecycle events
```

## Clasificación

| Señal | Clase | Acción inicial |
|---|---|---|
| validate/compile diagnostic | PIPELINE_DSL | corregir DSL |
| `StepFailed(SCRIPT)` | CODE/TOOL | reproducir comando en mismo workspace |
| executable missing / shim error | ENVIRONMENT | resolver toolchain/cwd |
| credential resolution | CREDENTIAL | revisar store/binding, nunca imprimir valor |
| timeout | BUDGET/DEADLINE | determinar si trabajo es lento o budget incorrecto |
| duplicate/concurrency anomaly | RUNTIME | preservar runId/sequence/state y escalar |
| exit/outcome contradicen | PIPELINEK_DEFECT | preservar ambos, no autocorregir a verde |

## Primer fallo causal

No arregles el último mensaje del log por defecto. Busca el primer hecho que convirtió el flujo en failure/unstable y sigue `runId`, stage, step/body identity y causation.

## Parallel

stdout de ramas puede intercalarse. Adjudica fallos por identidad/eventos, no por proximidad textual.

## Retry

Antes de añadir retry pregunta: ¿el fallo es realmente transitorio? Si es compilación, assertion determinista, permiso o versión incorrecta, retry sólo quema tiempo.

## Reporte para auto-fix

```text
classification:
confidence:
runId:
stage/step:
failureKind:
command:
exit:
RunFinished.outcome:
first causal event:
reproduction:
proposed smallest fix:
verification:
```

Si la clasificación no es suficientemente fuerte, ampliar investigación es mejor que modificar pipeline/producto al azar.
