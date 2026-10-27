# Fuentes seleccionadas y aplicación en la skill

Revisión editorial: 2026-10-27. Lecturas externas enlazadas, no copiadas ni redistribuidas. El contenido de librerías/versions puede cambiar: consultar documentación oficial antes de proponer dependencias.

## Fundamentos Haskell (conceptos, no sintaxis obligatoria)

1. Graham Hutton, [*Programming in Haskell*, 2nd ed.](https://people.cs.nott.ac.uk/pszgmh/book.html) — tipos, funciones superiores, recursión, monads, folds y razonamiento ecuacional. Primera lectura metodológica.
2. Simon Marlow (ed.), [*Haskell 2010 Language Report*](https://www.haskell.org/onlinereport/haskell2010/) — definición formal de funciones, tipos algebraicos y patrones; referencia, no guía arquitectónica.
3. Richard Bird y Jeremy Gibbons, [*Algorithm Design with Haskell*](https://www.cs.ox.ac.uk/publications/books/adwh/) — divide-and-conquer, greedy, thinning, dynamic programming y búsqueda exhaustiva; base de la lente algorítmica.
4. Richard Bird, [*Pearls of Functional Algorithm Design*](https://www.cambridge.org/core/books/pearls-of-functional-algorithm-design/B0CF0AC5A205AF9491298684113B088F) — derivación ecuacional y pruebas de propiedades, para tareas avanzadas.
5. Rúnar Bjarnason, Paul Chiusano y Michael Pilquist, [*Functional Programming in Scala (2nd ed.)*](https://www.manning.com/books/functional-programming-in-scala-second-edition) — errores puros, state, parsers, applicative, traversable y efectos. Traducción conceptual.

## Modelo, diseño y arquitectura

6. Scott Wlaschin, [*Domain Modeling Made Functional*](https://pragprog.com/titles/swdddf/domain-modeling-made-functional/) + [código](https://github.com/swlaschin/DomainModelingMadeFunctional) — lenguaje ubicuo, eventos, workflows, bounded contexts, tipos/invariantes y separación de efectos. Primera lectura de dominio.
7. Alexander Granin, [*Functional Design and Architecture*](https://www.manning.com/books/functional-design-and-architecture) — control de complejidad, sistemas funcionales, efectos y patrones arquitectónicos. **No** implica usar free monads siempre.
8. Martin Fowler, [*Bounded Context*](https://martinfowler.com/bliki/BoundedContext.html) y [*Ubiquitous Language*](https://martinfowler.com/bliki/UbiquitousLanguage.html) — fronteras y ontología sin un modelo universal.
9. [EventStorming resources](https://www.eventstorming.com/resources/) — descubrir comandos, eventos, actores y contradicciones con expertos. La lectura de código por sí sola no verifica una ontología.

## Rust

10. [*The Rust Programming Language*](https://doc.rust-lang.org/book/) — enums, Option, Result, ownership, traits, pattern matching e iteradores.
11. [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/) — contratos idiomáticos y ergonomía de APIs.
12. [Rust Design Patterns — Functional](https://rust-unofficial.github.io/patterns/functional/) — FP sin abandonar los idioms de Rust.

## Kotlin

13. Marco Vermeulen, Rúnar Bjarnason y Paul Chiusano, [*Functional Programming in Kotlin*](https://www.manning.com/books/functional-programming-in-kotlin) — bibliografía prioritaria de traducción Haskell→Kotlin, errores, combinadores y state.
14. Pierre-Yves Saumont, [*The Joy of Kotlin*](https://www.manning.com/books/the-joy-of-kotlin) — manejo de errores, estado, funciones y lazy evaluation.
15. [Kotlin sealed classes](https://kotlinlang.org/docs/sealed-classes.html), [collections](https://kotlinlang.org/docs/collections-overview.html) — ADTs y diferencia lectura vs inmutabilidad real.
16. [Arrow typed errors](https://arrow-kt.io/learn/typed-errors/) y [Arrow Lenses](https://arrow-kt.io/learn/immutable-data/lens/) — `Raise`, `Either`, `Lens`, `Prism` cuando mejoran semántica y coste.
17. [kotlinx.collections.immutable](https://github.com/Kotlin/kotlinx.collections.immutable) — colecciones persistentes; revisar estabilidad y versión antes de introducirla.

**Uso académico y licencias:** crear procedimientos propios, referenciar fuentes y explicar conceptos; no empaquetar capítulos ni copiar ejemplos extensos de libros protegidos.
