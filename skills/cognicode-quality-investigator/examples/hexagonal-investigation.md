# Ejemplo sintético, NO resultado de ejecución

Una ADR de un proyecto hipotético prohíbe `domain -> infrastructure`. `impact_detect_cycles` devuelve un ciclo entre `DomainService` y `InfraAdapter`. **No basta**: puede ser una arista de llamadas legítima hacia un port o un ciclo de grafo incompleto.

- `E-01 DOCUMENTED`: la ADR fija exactamente qué paquetes y qué tipos de dependencia prohíbe.
- `E-02 GRAPH`: el grafo identifica `DomainService → InfraAdapter` con su tipo y ancla de código, base de análisis y posibles archivos omitidos.
- `E-03 SOURCE`: inspección de `DomainService` y `InfraAdapter` detecta import concreto y comprueba que NO se trata solo de una interfaz interna o test fixture.
- `E-04 EXECUTION`: un test arquitectónico independiente del extractor del grafo falla para ese paquete y la versión del proyecto. Si no se ejecuta, escribir `NO_EJECUTADO` y mantener la clasificación como candidata o parcial según evidencia disponible.

Solo después de contrastar origen, destino, contrato, configuración de build y excepciones, crear H-01 con severidad contextual, ubicación exacta, evidencia, impacto y recomendación; de lo contrario registrar la hipótesis y su falsador.
