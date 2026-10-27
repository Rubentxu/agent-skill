# Lente: leyes algebraicas, ecuaciones y pruebas económicas

**Pregunta:** ¿qué verdades permiten refactorizar sin inmovilizar la implementación? **Señales:** `invalid-state`, `complex-algorithm`, `legacy-test-coupling`.

## Algoritmo

1. Definir transformación y equivalencia observable entre implementación anterior y nueva (salida, error, orden y eventos de borde que importan).
2. Buscar leyes pertinentes, no imponerlas todas: identidad/composición de `map`, monoid (asociatividad + identidad), roundtrip de parser/serializer, idempotencia de operación, conservación de suma, restricciones de máquina de estados.
3. Proponer propiedades refutables sobre **datos válidos** y datos inválidos; generadores con rangos, shrink y semillas si hay propiedad. Un oráculo circular (comparar una función consigo misma) no vale.
4. Para state transition: invariantes preservadas en éxito, estado intacto en rechazo, órdenes relevantes, ausencia de transiciones no permitidas.
5. Acotar a tests puros baratos; en integración garantizar solo las composiciones/efectos que el core no puede certificar; remitir `delivery-first-testing`.
6. Cuando concurrencia, persistencia o seguridad sean críticas, no declarar que tests algebraicos sustituyen la verificación del sistema real.

**Criterio de cierre:** ley expresada como ecuación, generador/ejemplos y test que un defecto real la quebraría. Si no se ejecutó, `NOT_RUN`. **No aplica:** laws arbitrarias sobre funciones que no prometen esas propiedades.
