# Lente: selección de algoritmos y composición funcional

**Pregunta:** ¿qué transformación resuelve la regla con menor coste y prueba clara? **Señales:** `complex-algorithm`, `nested-data`.

## Árbol de decisiones

1. Precisar entradas/salidas, dominio de valores, invariantes, orden, estabilidad, cardinalidad, streaming, fallos y volumen esperado.
2. Si cada elemento se transforma sin dependencias, `map`. Si se elimina, `filter`. Si se multiplican resultados, `flatMap`. Si se agrega estado, `fold`/`try_fold` (Rust) o `fold` (Kotlin). Si se detiene por condición, usar `find`/`any`/`all` en vez de recorrer todo.
3. Si cada elemento puede fallar, elegir `traverse/sequence` por comportamiento: Rust `collect::<Result<Vec<_>,E>>()`; Kotlin iteración con `Either/Raise` si instalado, o `Result`/sealed error sin dependencia adicional.
4. Para árboles, preferir recursión estructural simple; fusionar recorridos cuando hay múltiples asignaciones importantes, sin forzar recursion schemes/HKT.
5. Para problemas de optimización decidir según condiciones demostradas: greedy requiere argumento de optimalidad; divide-and-conquer si independencia; dinámica con subproblemas solapados; búsqueda exhaustiva solo con cotas/branch-and-bound.
6. Razonar con leyes (asociatividad, identidad, reversibilidad) y complejidad `O(tiempo, memoria)`; medir costes de copias, asignación, pila y boxing. **No** convertir `for` eficiente en `fold` con clonaciones cuadráticas.
7. Crear un contraejemplo pequeño y test de límite; elegir API clara sobre abstracción excesiva.

**Resultado:** ecuación/regla, condiciones de validez del algoritmo, función propuesta, complejidad, memoria y prueba discriminante. Fuente base: Bird & Gibbons, *Algorithm Design with Haskell*.
