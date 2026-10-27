# Plantilla de resultado de lente

- **Referencia de código:** repo, revisión, slice, símbolos relevantes (o `UNKNOWN`).
- **Observaciones:** evidencias separadas de hipótesis.
- **Pregunta elegida:** lente y por qué sus señales aplican.
- **Lenguaje:** versión real, idioms y restricciones.
- **Ontología:** actor, comando, estado, evento, invariantes, errores, bounded context cuando proceda.
- **Antes/después:** firmas puras y dueños de efectos; compatibilidad y semántica preservada.
- **Algoritmo:** complejidad de tiempo/memoria; evitar introducir dependencias sin beneficio.
- **Slice propuesto:** primera entrega verificable y reversible, no refactor horizontal.
- **Verificación:** invariantes, ejemplos, leyes; pruebas ejecutadas/NOT_RUN y handoff a delivery-first-testing.
- **Riesgos:** atomicidad, serialización, orden de eventos, cancelación, referencias mutables, coste de CPU/RAM.
