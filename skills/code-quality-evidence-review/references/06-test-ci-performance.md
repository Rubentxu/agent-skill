# Verificación por riesgo, CI exacta, benchmarks y observabilidad

## Selector de pruebas (adaptable al coste real)

| Momento | Señal | Selección inicial | Escala cuando… |
|---|---|---|---|
| PR / desarrollo | archivo/contrato modificado | typecheck/compilación selectiva + tests del módulo + consumidores directos + caso de regresión | interfaz pública, serialización, concurrencia, datos, permisos o riesgo de integración atraviesan módulos |
| Integración | cambio listo para rama compartida | suite completa **según política del repo** y tests de contrato/compatibilidad, build en matriz relevante | CI muestra skips, fail, flake, reportes ausentes o discrepancia de toolchain |
| Release | nuevo SHA/artefacto | gates íntegros exigidos + UAT/seguridad/compatibilidad/performance acordadas + confirmación de artefactos del SHA | no hay run actual o test del artefacto que realmente se publicará |

No presupongas que “suite completa” equivale a **cada** herramienta del catálogo; si la política no existe, plantea los gates proporcionales al producto sin afirmarlos ejecutados. Un fallo por timeout requiere identificar la causa antes de inferir defecto del SUT. Si hay flake, anota test, tasa/ejecuciones cuando se mida y consecuencias de rerun. Comandos de ejemplos se encuentran en `references/04-language-recipes.md`.

## Registro de ejecución

`evidence_id; SHA; fecha; entorno (SO/runtime/hardware si importa); comando exacto; filtros/exclusiones; exit status; cuenta tests PASS/FAIL/SKIP si existe; duración si hay medida; artifact/run; interpretación`.

Un job `skipped` que el proyecto requiere deja gate `NO EJECUTADO` o `FALLA` según reglas del gate, **nunca PASS**. Los jobs de matrices se cuentan uno a uno; el estado agregado debe justificar excepciones. Si solo se ve la configuración y no el run, indicar `CONFIGURADO, NO VERIFICADO`.

## Benchmarks comparables

Definir workload y objetivo antes de medir: cold/warm, representatividad de dataset, rendimiento crítico de aplicación vs rendimiento del build, concurrencia, cache, warm-up, máquina aislada, clocks, percentiles/distribución, RAM/CPU/IO, errores, límite temporal. Comparar baseline y nuevo SHA en entorno equivalente, repetir y registrar variabilidad; no inferir SLA de un microbenchmark. Solo propone integrar benchmark en CI si es fiable y tiene budget; para pruebas de carga, trabajar contra sistemas autorizados y con límites explícitos.

## Observabilidad verificable

Hacer una ejecución con correlación `trace_id/run_id`, forzar un fallo *inofensivo* y confirmar si el operador encuentra causa y componente. Comprobar que no se exportan secretos/PII, no hay explosión de cardinalidad y se puede recuperar estado de un retry/replay donde exista. No recomendar OpenTelemetry como única opción: eventos, logs y métricas internas pueden ser suficientes según necesidades.
