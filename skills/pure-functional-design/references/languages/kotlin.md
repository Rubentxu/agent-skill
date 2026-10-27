# Lente Kotlin — pureza idiomática en el ecosistema JVM

**Alcance:** Kotlin/JVM, KMP si procede; imitar monad transformers de Haskell por sistema es antipatrón.

## Herramientas idiomáticas

- **Suma:** `sealed interface`/`sealed class`, `data object`; **producto:** `data class(val...)` y `copy`. Usar `when` exhaustivo SIN `else` que silencie nuevas variantes.
- `value class` para identificadores pequeños, smart constructors para validación, evitar `!!` y `require()` con excepción para rechazos esperados de dominio cuando un tipo de error comunica mejor.
- `T?` expresa ausencia; Kotlin `Result<T>` agrupa éxito/fallo con `Throwable` y **no tipa el error**. Para fallos de negocio: `sealed`/`Either<E,A>` o Arrow `Raise<E>` si existe la dependencia. Acumulación de errores independientes mediante Arrow cuando está instalado o diseño específico.
- `List<T>` es de solo lectura, no garantía de inmutabilidad profunda. `val` congela la referencia, no el objeto. Valorar `kotlinx.collections.immutable` para snapshots grandes con estructuras persistentes, tras revisar el estado experimental/compatibilidad.
- `map`, `flatMap`, `fold`, `associate`, `groupBy`, `Sequence` para flujos; no crear listas intermedias enormes o cadenas de secuencias sin medir.
- Arrow Optics (`Lens`, `Prism`, etc.) solo cuando actualización profunda repetida aporta una mejora clara sobre `copy` anidados.
- `suspend`, `Flow`, `CoroutineScope` no implican pureza; mover IO a los adaptadores y manejar cancelación estructurada sin `catch(Throwable)` que oculte `CancellationException`.
- Reducir interfaces automáticas en cada clase: parametrizar contextos explícitos y puertos mínimos existentes. Java APIs mutables y proxies ORM se mantienen fuera del core.

## Algoritmo del perfil

1. Confirmar versión Kotlin, target JVM/KMP, Arrow/serialization/coroutines y convenciones del proyecto sin instalar librerías.
2. Modelar estados con `sealed` y errores con tipo cerrado; smart constructors y `data.copy` para estados nuevos. Para inmutabilidad real, inspeccionar alias y colecciones.
3. Extraer `fun decide(state: State, cmd: Command, context: Context): DecisionResult` sin suspend ni clock global. Organizar handler `suspend` externo si usa adaptadores asíncronos.
4. Al refactorizar `flow`, asegurar que cancelación, orden, backpressure y propagación de errores no cambian accidentalmente.
5. Verificar compatibilidad con Java, serialización, reflection, JPA y APIs públicamente consumidas.
6. Usar suite afectada Gradle/Kotest/JUnit ya existente; no añadir runners ni dependencias por defecto.

## Ejemplo breve

```kotlin
sealed interface State { data object Draft : State; data class Published(val version: Long) : State }
sealed interface DomainError { data object AlreadyPublished : DomainError }
sealed interface DecisionResult {
    data class Ok(val state: State) : DecisionResult
    data class Rejected(val error: DomainError) : DecisionResult
}
fun publish(state: State): DecisionResult = when (state) {
    State.Draft -> DecisionResult.Ok(State.Published(1))
    is State.Published -> DecisionResult.Rejected(DomainError.AlreadyPublished)
}
```

**Sources:** [Kotlin sealed](https://kotlinlang.org/docs/sealed-classes.html), [Kotlin collections](https://kotlinlang.org/docs/collections-overview.html), [Arrow typed errors](https://arrow-kt.io/learn/typed-errors/), [Arrow lenses](https://arrow-kt.io/learn/immutable-data/lens/).
