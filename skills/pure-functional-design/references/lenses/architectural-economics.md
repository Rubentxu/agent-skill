# Lente: economía arquitectónica y criterio de no actuar

**Pregunta:** ¿qué cambio reduce el coste total sin empeorar rendimiento ni garantías?

## Comparación ordinal explícita

1. Definir **criterios prioritarios no negociables**: integridad, contrato observable, seguridad, concurrencia, cancelación, semántica de errores y datos persistidos.
2. Para los candidatos elegibles comparar en orden: evidencia del problema, reversibilidad, coste de migración, esfuerzo, carga de mantenimiento, acoplamiento semántico/connascence y coste operativo. No mezclar estas dimensiones en una puntuación mágica.
3. Analizar antes/después: propietarios de reglas, consumidores a modificar por cambio de negocio, dependencias inversas y límites de transacción.
4. Estimar coste `O(tiempo, memoria)`, clones, allocations, colecciones intermedias, stack, boxing/JVM, serialization. Medir si se trata de un hot path y existe benchmark representativo.
5. `KEEP_AS_IS` gana si no existe mejora observable o si el coste de migración es injustificado. La simplicidad de una mutabilidad **local encapsulada** puede superar una abstracción FP.
6. Verificar con contraprueba: reducir LOC o duplicados de texto no prueba mejora; introducir diez clases tampoco reduce un God Service si siguen coordinadas.

**Salida:** matriz `candidato | garantías | reversibilidad | esfuerzo | rendimiento | acoplamiento | veredicto | evidencia faltante`. Restringir afirmaciones de velocidad a mediciones reales.
