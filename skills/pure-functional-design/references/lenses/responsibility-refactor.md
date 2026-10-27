# Lente: detectar concentraciones de lógica y refactorizar por responsabilidad

**Pregunta:** ¿por qué una clase/archivo decide demasiadas cosas? **Señales:** `large-service`, `duplicate-logic`, `legacy-test-coupling`.

## Algoritmo

1. Inventariar funciones/tipos y efectos del archivo grande, y mapearlos por casos de uso; separar complejidad esencial (reglas) de accidental (mezcla de responsabilidades).
2. Señalar duplicación semántica, no solo textual: repetir la misma regla de transición, validación o ownership en handlers diferentes. Comprobar que los casos son semánticamente equivalentes antes de unificar.
3. Identificar seams de extracción (`parse`, `validate`, `decide`, `apply`, `present`) y dueño de cada regla; evitar una superclase/helper que centraliza lógica ajena.
4. Refactor seguro: conservar la firma pública; crear función pura nueva; desviar **un** consumidor; contrastar invariantes y errores; repetir para el resto; eliminar código viejo al cerrar.
5. En estructuras durables, preservar orden de escritura, cancelación, stdout/stderr, backpressure y secuencia de eventos cuando formen contrato.
6. Detectar test drift: tests acoplados a rutas, números de métodos o logs internos frente a invariantes. Delegar la decisión de sustitución/retiro a `delivery-first-testing`.
7. Medir complejidad útil: ramas de reglas, acoplamiento entre contextos, funciones con efectos, duplicaciones, peso de APIs y coste de feedback. LOC por sí sola no prueba mejora.

**Contraprueba:** partir un God Service en diez clases que lo delegan todo sigue siendo un God Service distribuido. Otro mal resultado: dos validadores distintos para la misma regla bajo nombres parecidos.

**Salida:** matriz `regla | dueño actual | dueño propuesto | consumidores | riesgo | seam | evidencia`, primer PR vertical reversible.
