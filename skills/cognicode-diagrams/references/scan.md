# Investigación activa y estructurada de CogniCode

**Solo CogniCode CLI/MCP puede investigar código implementado.** No abrir archivos del checkout, documentación, tests, manifiestos, ADR o búsquedas externas. El problema no se resuelve con `read_file(raw)` y `search_content` cuando falla una herramienta estructurada.

1. Definir **una pregunta concreta**, lenguaje y símbolo/alcance. Descubrir `--help`/`capabilities` del CLI *cuando existan*, o `initialize` + `tools/list` paginado en MCP. Comprobar schema y permisos. Herramienta anunciada no equivale a operativa.
2. Asociar nombres reales a roles de [research-protocol.md](research-protocol.md). Son roles de orientación, no comandos obligatorios. Probar una capacidad pertinente sobre un símbolo real: índice, identidad/ubicación, contexto, relaciones y cobertura por **capacidad + lenguaje**.
3. Consultar con la operación estructurada más directa. Para leer contexto elegir función de código **por símbolo**, no lectura arbitraria de archivos. `search_content` solo produce candidatos, que necesitan confirmación estructurada.
4. Si falla el grafo o la herramienta elegida, preservar el fallo acotado; otra capacidad del mismo lenguaje puede funcionar. No declarar Kotlin entero `unsupported` por una prueba aislada.
5. Contrastar entidades y **cada extremo/arista** mediante resultados y fragmentos devueltos por CogniCode. `calls` prueba topología estática, no un proceso separado o comunicación runtime. Registrar `query_id`, claim y cobertura en [evidence.md](evidence.md).
6. Terminar si hay suficiente evidencia para responder; si no hay nueva prueba ni otra capacidad viable, cerrar `PARTIAL/UNKNOWN` sin bucles, sin documentos, sin otra herramienta.

No ejecutar `analyze .` ni construir todo el grafo por rutina. El coste y la profundidad los gobierna la pregunta. Para «más detalle», nueva pregunta sobre el componente requerido, no un dibujo más grande a partir del mismo reporte.
