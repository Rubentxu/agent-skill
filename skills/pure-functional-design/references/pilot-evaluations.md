# Pilotos R4 de diagnóstico sobre aplicaciones reales (sin modificar producción)

Estas evaluaciones ejercitan el **router y su criterio de abstención**, no certifican
un refactor de los repositorios analizados. Se inspeccionaron fragmentos del código
productivo en las revisiones fijadas; **no** se ejecutó Cargo, Gradle ni tests de
los productos. Los hechos observados no equivalen a una evaluación completa de
dependencias, contratos, rendimiento o semántica temporal.

## Rust: búsqueda de texto en hodei-artifacts

- **Repositorio/revisión:** [hodei-artifacts `26c5c08`](https://github.com/Rubentxu/hodei-artifacts/tree/26c5c08b646960e9545f0918847d207bb5d0acec)
- **Código observado:** [`crates/search/src/features/search_full_text/use_case.rs`](https://github.com/Rubentxu/hodei-artifacts/blob/26c5c08b646960e9545f0918847d207bb5d0acec/crates/search/src/features/search_full_text/use_case.rs#L50-L344)
- **Hechos:** `execute_search` valida, invoca analizadores/búsqueda/ranking y publica
  métricas (líneas 52–92); `validate_query` solo examina datos, pero es `async`
  (162–184); el enriquecimiento lanza tareas con semáforo (200–264);
  `record_search_metrics(...).await?` hace que falle toda la operación si falla
  la monitorización (90–92, 324–344).
- **Riesgos que requieren aclaración:** `with_max_concurrent_queries(0)` permite
  construir un semáforo sin permisos (45–48, 200–211); el asignador de scores
  por posición presupone compatibilidad entre el orden devuelto por el ranker y
  el orden de resultados originales (299–310). Son **hipótesis de riesgo**,
  no defectos comprobados con ejecuciones.
- **Diagnóstico acotado:** hay un candidato a extraer validación pura, pero no se
  ha caracterizado el contrato completo: mensajes de error, orden de efectos,
  ranking, comportamiento ante fallos de monitorización y concurrencia.
- **Decisión del router:** `INSPECT_MORE`, no `APPLY`. Elegir primero el caso
  pequeño `validate_query`, caracterizar reglas y errores, después extraer
  una función síncrona sin modificar API pública ni semántica de fallos.
- **No hacer:** reemplazar el `for` de enriquecimiento por un `fold` con clones,
  cambiar `tokio::spawn` o degradar fallos de observabilidad sin contrato acordado.
- **Evidencia ejecutable del selector:** [sesión Rust](../examples/pilot-hodei-search-rust.json).

## Kotlin: dispatch durable en pipeline-kotlin

- **Repositorio/revisión:** [pipeline-kotlin `7033703`](https://github.com/Rubentxu/pipeline-kotlin/tree/703370304673f45aa1aeaf03e54a8cc432d5f010)
- **Código observado:** [`StepDispatchEngine.kt`](https://github.com/Rubentxu/pipeline-kotlin/blob/703370304673f45aa1aeaf03e54a8cc432d5f010/pipelinek/pipeline-application/src/main/kotlin/dev/rubentxu/pipeline/v2/application/durable/StepDispatchEngine.kt#L65-L88)
- **Hechos:** el código explica que dispatch, body y reentrada forman un ciclo
  cohesionado (65–88); `invokeBodyChildren` delega en `BodyExecutionEngine`
  y entrega un `BodyChildDispatcher` que vuelve a `dispatch` (965–1011);
  `dispatchChild` también reentra por el mismo punto (1018–1036).
  `mergeBodyAndCleanup` es una decisión total sobre resultados tipados
  (1135–1148), y la emisión de eventos queda en el borde (1155–1181).
- **Diagnóstico:** un archivo extenso por sí solo **no demuestra** múltiples
  responsabilidades separables. Romper este ciclo para reducir LOC puede
  introducir wrappers y más acoplamiento; la extracción concreta se descarta.
- **Decisión del router:** `KEEP_AS_IS` para separar esa recursión. No significa
  que todo el archivo sea perfecto ni descarta otros refactors futuros.
- **Prueba antes de recomendar otras extracciones:** observar llamadas,
  consumidores, orden de eventos y comportamiento durable con el build real.
- **Evidencia ejecutable del selector:** [sesión Kotlin](../examples/pilot-pipelinek-dispatch-kotlin.json).

## Criterio de cierre y límites

Las dos sesiones son **ficheros declarativos** con señales registradas manualmente;
su `basis=observed` solo refleja inspección de fragmentos en un SHA.
Los tests comprueban la navegación/decisiones del selector, no verifican
el comportamiento real de hodei-artifacts o pipeline-kotlin.

Antes de considerar R4 completado faltan refactors pequeños realizados en ramas
de producto, caracterización de contratos, verificación oficial de Cargo/Gradle
y comparación de coste/mantenibilidad. `delivery-first-testing` conserva
la responsabilidad de seleccionar los tests necesarios.
