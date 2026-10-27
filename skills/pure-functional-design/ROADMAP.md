# Roadmap para integrar `pure-functional-design` en `Rubentxu/agent-skill`

**Estado:** primera versión subida en PR #43; evolución R1–R3 preparada en rama de la PR. No equivale a fusión en `main`. Enfoque delivery-first: un router instalable, lentes que deciden, herramientas existentes que ejecutan. No sumar runtimes, dependencias ni otro sistema CI.

## F0 — Contrato portable y bibliografía

**Entrega:** un SKILL.md con ontología, contrato de observación, policy `ready/planned`, precedencias y no-aplicabilidad. Lentes iniciales Rust/Kotlin, código fuente de las referencias enlaces.

**Gate:** catálogos válidos, rutas seguras, ejemplos trazables. Ninguna cita inventada ni capítulos de libros incluidos.

## F1 — Router, métodos y adaptación idiomática

**Entrega:** lentes de descubrimiento, ADT, pure core/effects, algoritmos, vertical slices, refactors, leyes, optics y perfiles Rust/Kotlin. Selector simple con señales verificadas y límite de 1–3 lentes metodológicas.

**Gate:** tests unitarios del router, selector puro, nunca READY para PLANNED, no ejecutar refactors por catálogo, no confundir idioma desconocido con Rust/Kotlin.

## F2 — Pilotos de dos slices reales (sin features nuevas)

**Entrega:** un refactor Rust y uno Kotlin, delimitados por un único caso de uso; primero descubrir dueños y reglas de forma trazable. La skill debe detectar al menos una hipótesis que **no** puede validar con el código disponible.

**Gate:** equivalencia de contrato, errores, orden/efectos, no crear interfaces/HKT gratuitos, complejidad y coste de feedback medidos. Evaluación con agente y referencias a rutas/símbolos reales.

## F3 — Colaboración con skills existentes

**Entrega:** interacción declarativa con `delivery-first-testing` (garantías + leyes, no ejecución duplicada) y `cognicode-diagrams` solo si están realmente disponibles y cumplen precondiciones. Los problemas de integración se clasifican como gaps, no se cubren inventando herramientas.

**Gate:** pruebas adversariales de elección, falso verde, `stale`, cambio de contrato, pruebas no ejecutadas, restricciones CogniCode. No crear un CI nuevo.

## F4 — Publicación y aprendizaje de uso

**Entrega:** PR a `Rubentxu/agent-skill`, README de instalación y 2–3 escenarios reales anonimizados. Activar nuevas lentes solo si resuelven una pregunta distinta en proyectos diferentes.

**Gate:** flujo local del repositorio, revisión, métricas de antes/después, autorización de merge/publicación; ninguna afirmación de release previa a ejecución.

## Métricas de calidad (no objetivos de cobertura)

- Disminución de ramas de dominio repartidas entre adaptadores y handlers.
- Eliminación de duplicaciones semánticas con dueño único.
- Número de estados ilegales construibles desde APIs públicas.
- Riesgos de efecto/transacción/serialización inadvertidos detectados.
- Tiempo de feedback de pruebas afectadas y total, observado (p50/p95 si existe histórico).
- Refactors revertibles entregados por slice frente a reorganizaciones horizontales.
- Falsos positivos en recomendaciones de lentes y abstenciones correctas.

Las métricas se usan comparativamente en proyectos concretos, no como metas numéricas arbitrarias.

## Evolución R1–R3 — Diagnóstico y refactorización por problemas

- **R1:** catálogo de síntomas/problemas con evidencia y abstención; selector por problema y alternativas. Validado mediante unit tests del router, no mediante agentes reales.
- **R2:** recetas incrementales de seam, Mikado, parallel-change, branch-by-abstraction, estados, algoritmos y extracción de core; incluye comparación con no cambiar.
- **R3:** navegación `diagnose|plan|verify`, `read-recipe` solo cuando procede y `delegate-skill` únicamente sobre `available_skills` confirmadas.
- **R4 pendiente:** ejecutar casos reales sobre un slice Rust y otro Kotlin y medir semántica, memoria/asignación y coste de feedback.
- **R5 pendiente:** evaluar falsos positivos, adaptar heurísticas y cerrar publicación e indexación después de los gates.

No confundir tests del selector con refactors verificados sobre aplicaciones.
