# Lente: diseño compacto de casos — data-driven, límites y propiedades

**Pregunta:** ¿cuál es el conjunto mínimo de entradas que diferencia los comportamientos relevantes?

1. Identificar la **regla observable** y su oráculo: resultado esperado, evento, estado, rechazo o propiedad. Si no puede fallar con una implementación incorrecta, mejorar el oráculo antes de añadir casos.
2. Particionar entradas equivalentes válidas e inválidas. Incluir mínimo/máximo y vecinos de límites donde corresponda; añadir valores que representen historial de defectos reales.
3. Reunir los ejemplos en un test parametrizado con IDs y aserciones diagnósticas por fila. **No confundir** menos métodos escritos con menos ejecuciones: eliminar filas solo si conservan la misma distinción semántica. **No-vacuidad de generadores/factorías:** si se esperan 3 × 2 combinaciones, comprobar mecánicamente seis identificadores únicos y todos los pares antes de devolver tests dinámicos. Una factoría vacía, un filtro que selecciona cero filas o un reporte sin casos **no es PASS**.
4. Si la garantía es algebraica/invariante, valorar property-based testing: generadores acotados, semilla reproducible, shrinking y ejemplos mínimos. Usar metamorphic testing cuando no exista un oráculo simple (transformación inversa, orden, idempotencia, serialización round-trip).
5. Para combinaciones de parámetros, pairwise o t-way puede reducir producto cartesiano, **solo** si las interacciones de orden superior no son críticas; añadir expresamente combinaciones peligrosas conocidas. No usar pairwise como garantía universal.
6. Situar la prueba en la capa más barata que cubra la garantía, reservar un smoke real para composición y consumo. No convertir cada fila en E2E permanente.

**Ejemplo mínimo (conceptual):** rango inclusivo 1..100 → entradas 0, 1, 50, 100, 101; cada caso tiene resultado esperado explícito. Para lógica de permisos incluir denegaciones, no solo éxitos.

**Cierre:** tabla de particiones/límites, oráculos discriminantes, casos **ejecutados realmente por el runner oficial**, falsos verdes explorados y razones para mantener o retirar combinaciones. Contrastar XML/reporte por caso con el cardinal esperado, cero skips y SHA exacto. Una compilación Kotlin con shim/JUnit simulado ayuda a aislar sintaxis y lógica, pero **no sustituye Gradle/JUnit ni autoriza el merge** si el repositorio exige el gate oficial: declarar `NOT_RUN` o `BLOCKED` cuando falte. Adaptar al runner existente (JUnit/Kotest, pytest, Rust proptest, Vitest, etc.); no instalar herramientas ni frameworks automáticamente.

**Referencias:** [NIST combinatorial testing](https://csrc.nist.gov/projects/automated-combinatorial-testing-for-software), [pytest parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html), [Hypothesis](https://hypothesis.readthedocs.io/).
