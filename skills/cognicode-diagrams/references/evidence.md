# Evidencias para cualquier lente

La skill no crea una base de conocimiento nueva. CogniCode proporciona índices, resultados MCP/CLI y caches según su versión, mientras el agente compone una ficha derivada y efímera de afirmaciones arquitectónicas o de código para el objetivo solicitado.

## Campos recomendados del handoff del agente

- **Solicitud**: intención, lente, formatos, alcance (subrepositorio, componente, endpoint, requisito, etc.).
- **Identidad**: workspace, ruta, Git HEAD, estado dirty + archivos relevantes cuando se conozcan, versión CLI/MCP, instantánea de comandos consultados y fecha de observación.
- **Cobertura**: idiomas/providers soportados, número de símbolos/aristas si hay métricas, archivos omitidos y truncamiento. `partial` no equivale a 100 %.
- **Afirmación**: id de entidad/relación, fuente rastreable (archivo/línea, ruta, ADR, UAT, log, traza), `OBSERVED|INFERRED|CURATED|UNKNOWN`, alcance y contradicciones.
- **Límites**: qué **NO** demuestra la evidencia. `calls` no prueba un protocolo ni orden, un crate no prueba proceso desplegado; un test no acredita producción.
- **Operaciones realizadas**: nombre de comando/tool real, parámetros, resultado/error. No reutilizar por similitud de nombres.

## Handoff por lentes

El modelo que el agente mantiene al interpretar o generar no es una nueva ontología genérica persistida. Cada lente define sus propios elementos y leyes; la ficha solo conserva identidad, evidencias, dudas y destinatarios de representación. Si existe un diagrama curado, conservarlo como entrada independiente de los hechos observados, no sobrescribirlo como producto de una inferencia.

## Casos que nunca acreditan preparación

- `build_graph` devolvió 0 pero nadie pudo consultar el grafo después.
- La herramienta se anunció en documentación, pero `tools/list` del servidor actual no la contiene.
- `graph full` emitió estado parcial por archivos omitidos; el agente lo redujo a `complete`.
- Se usó el SHA de Git ignorando cambios no commiteados que afectan símbolos o despliegue.
- Se interpretó la topología estática como historia de ejecución ordenada.
- Se hizo una segunda consulta MCP del mismo grafo y se afirmó corroboración independiente.
