# Evaluaciones portables de refactorización (fixtures sintéticas)

**Objetivo:** comprobar que la skill orienta a los agentes sin depender de repositorios concretos ni modificar aplicaciones. Las rutas siguientes pertenecen solo a esta skill. Las evidencias de las sesiones son declaraciones de ejemplo para ejercitar el router: no certifican contratos de productos.

## Caso A — Rust: reglas y efectos mezclados, sin caracterización

[Fixture Rust](../examples/fixtures/search_use_case.rs) · [Sesión JSON](../examples/diagnose-rust-uncharacterized.json)

`SearchUseCase::execute` valida entradas, llama a un puerto de búsqueda y publica métricas. La llamada a métricas puede fallar; por tanto, extraer validación o reorganizar IO requiere primero comprender la semántica de errores, compatibilidad y orden de los efectos. El router **debe responder `INSPECT_MORE`** y no presentar una receta como lista para ejecutar.

**Contraejemplo:** que la validación parezca una función pura no autoriza eliminar `MetricsPort::record` ni ignorar errores. El fixture no implica que el código deba ser refactorizado en ninguna aplicación.

## Caso B — Kotlin: recursión cohesionada

[Fixture Kotlin](../examples/fixtures/step_dispatch.kt) · [Sesión JSON](../examples/diagnose-kotlin-cohesive.json)

El método `dispatch` es recursivo, pero implementa una única capacidad: interpretar un árbol `Step` como una lista de acciones, sin efectos. No hay evidencia de responsabilidades divergentes. Ante una propuesta de fragmentación basada únicamente en longitud/recursión, el router debe responder **`KEEP_AS_IS`**.

**Contraejemplo:** convertir cada rama en una interfaz o usar una DSL funcional no aporta valor por sí mismo.

## Casos de transición y descubrimiento

El test `test_portable_scenarios.py` también verifica: un caso genérico que reúne precondiciones obtiene `APPLY` **solo como recomendación**; `diagnose` no publica receta, `plan` la publica y `verify` anuncia comprobaciones; un cambio a `stale` invalida la decisión; sin otra skill realmente disponible no hay delegación.

## Límites de evidencia

- Estas pruebas comprueban el **selector de la skill**, no que los fixtures compilen ni el resultado de una refactorización.
- No se usan rutas, SHA, credenciales ni herramientas de una aplicación real.
- El agente receptor debe inspeccionar su código, identificar contratos y utilizar la estrategia de testing que su proyecto haya autorizado. Sin ejecución, el estado es `NOT_RUN`.
- Un proyecto consumer puede adoptar o rechazar la receta, preservando errores, datos, rendimiento, concurrencia y orden de efectos.
