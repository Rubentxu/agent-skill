# Catálogo de primitivas, patrones y algoritmos (idiomático, no calco Haskell)

| Idea Haskell/FP | Rust | Kotlin | Cuándo aplicar / cautela |
|---|---|---|---|
| `map`, `filter` | `Iterator::map/filter` | `map/filter`, `Sequence` | Transformaciones; medir asignaciones e iteración |
| `foldl`, `foldr` | `fold`, `try_fold`, `rfold` | `fold`, `foldRight` | Estado agregado; revisar orden/no asociatividad |
| `foldMap` | `map` + `fold` | `fold` + operación acumuladora | Reducción homomórfica; evitar clones por paso |
| `flatMap` | `flat_map` | `flatMap` | Composición de colecciones/resultados |
| `traverse/sequence` | `collect::<Result<Vec<_>,_>>()` | `map`+`sequence` Arrow o fold explícito | Convertir lista de resultados en resultado de lista |
| `Maybe` | `Option<T>` | `T?` / `Option` Arrow cuando aporta | Ausencia ≠ error; no anidar sin necesidad |
| `Either` | `Result<T,E>` | `Either<E,T>`, `Raise<E>`, `Result<T>` | Fallos de dominio explícitos; `Result` Kotlin no tipa `E` |
| `data A = X | Y` | `enum A { X, Y }` | `sealed interface A` | Alternativas cerradas y `match/when` exhaustivos |
| `newtype` | struct de un campo con campo privado | `@JvmInline value class`, validador | Evitar IDs/números intercambiables |
| `Reader` | parámetros de contexto y `&T` | parámetros/context receiver con criterio | Pasar entorno como dato; no esconder globales |
| `State` | `(State, Input)->(State,Output)` | `(State, Input)->Pair<State,Output>` | Reducers deterministas; no inyectar store global |
| `Writer` | valor + `Vec<Event>` | `Decision` + `List<Event>` | Producir intención, ejecutar posteriormente |
| `Semigroup/Monoid` | `combine` explícito y valor neutro | `combine` explícito | Solo abstracción común si existen varios usos y leyes |
| `Applicative` | validación acumulada escrita explícita | Arrow `zipOrAccumulate` | Errores independientes que deben acumularse |
| Optics `Lens/Prism` | actualización con `struct`/`enum`, match | `copy`, Arrow Optics | Solo para grafos de datos profundos/repetidos |
| `traverse` con IO | bucle controlado en boundary | `suspend`/coroutines en boundary | Nunca ocultar operación externa en el dominio |
| `Fix`/recursion schemes | tipos recursivos con `Box` si procede | sealed data recursiva | Árboles complejos, no generalizar por dos recursiones |
| Parser combinators | parsers existentes o composición manual | parsers existentes | Fronteras de entrada complejas, semántica documentada |
| Dynamic programming | iteración con tabla local o memo explícita | tabla mutable local encapsulada | Elegir por complejidad, no por “pureza” superficial |
| Divide-and-conquer | funciones y slices recursivos | recursión o iteración | Controlar stack y coste de copias |
| Greedy | iteración/fold con prueba de optimalidad | iteración/fold con prueba de optimalidad | No suponer que sirve si faltan hipótesis |
| Finite state machine | enum + transition/typestate selectivo | sealed state + reducer | Eventos y estados del dominio, no frameworks por defecto |
| Functional core/shell | domain crate/module + adapters | domain module + ports/adapters | Preferir seam útil, no carpetería ornamental |

## Reglas de elección

1. La transformación más simple que mantiene contrato e invariantes gana a una abstracción elegante.
2. `map` transforma, `flatMap` expande, `filter` selecciona, `fold` acumula; usar nombre correcto.
3. Evaluar coste temporal, espacial, asignaciones, efectos de orden e interrupciones antes de substituir un bucle.
4. La mutación local en un algoritmo de programación dinámica o una construcción de `Vec` **puede mantener una interfaz funcionalmente pura**.
5. Evitar dependencias de Arrow, im/persistent y crates de ópticas salvo necesidad observada y compatibilidad verificada.
