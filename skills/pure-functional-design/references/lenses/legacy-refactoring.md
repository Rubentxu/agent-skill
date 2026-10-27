# Lente: refactorización incremental de aplicaciones existentes

**Pregunta:** ¿cómo crear un seam reversible sin cambiar involuntariamente los contratos?

## Algoritmo

1. Definir el comportamiento que debe sobrevivir: errores, orden, concurrencia, persistencia, cancelación, serialización, compatibilidad y consumidores.
2. Elegir la frontera observable más estrecha. Si faltan tests, caracterizar exactamente el comportamiento crítico (no capturar toda implementación privada).
3. Seleccionar receta por bloqueo: `legacy-seam` si no se puede aislar; `mikado-refactor` si surgen dependencias; `parallel-change` para consumidores versionados; `branch-by-abstraction` cuando es imprescindible convivir con dos implementaciones.
4. Extraer una sola decisión/slice; introducir puntos de comparación y reversión solo si el riesgo lo justifica. No fabricar interfaces, flags o dual writes permanentes.
5. Migrar **un** consumidor; comprobar paridad con la entrada real y el artefacto actual; retirar gradualmente el código viejo después de la convergencia.
6. Para protocolos y esquema persistido, documentar transición de lectura/escritura de versiones. En doble escritura considerar idempotencia, consistencia y reparación.
7. Entregar evidencia (`NOT_RUN` si no se ejecutó) y coordinación con `delivery-first-testing` para la mínima protección pertinente.

**No aplicar** branch-by-abstraction a una función privada que se puede modificar atómicamente; no cortar una transacción por crear un módulo nuevo.
