# Lente: actualización inmutable, optics y estructuras persistentes

**Pregunta:** ¿cómo se modifica un estado profundo sin introducir aliasing ni complejidad innecesaria? **Señales:** `nested-data`, `side-effects`.

## Selección

1. Si la actualización es superficial y escasa, Rust construir/copiar/mover structs; Kotlin `data.copy`. No añadir optics.
2. Si hay muchas actualizaciones profundas repetitivas, valorar `Lens`, `Prism`, `Optional`, `Traversal` y sus leyes (`get-set`, `set-get`, `set-set`) **después** de confirmar bibliotecas actuales y rendimiento.
3. Si se necesita compartir versiones de grandes colecciones, considerar estructura persistente; comparar memoria y complejidad frente a copia completa o in-place builder local.
4. Kotlin: `List<T>` es interfaz de solo lectura, pero un alias mutable puede alterar elementos; `val` no inmuniza referencias anidadas. Arrow Optics y `kotlinx.collections.immutable` son opciones, no requisitos.
5. Rust: ownership, préstamos inmutables y movimientos proporcionan muchas garantías sin librería optics; `Arc` comparte, pero `Mutex` permite mutación observable y no hace pura una función.
6. Medir asignaciones, acceso, serialización y costes de adopción antes de un refactor transversal.

**Cierre:** alternativa más simple que conserva invariantes, coste de cambio justificado, no alias mutable inadvertido. **Antipatrón:** introducir una lens library para modificar dos campos.
