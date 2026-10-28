---
name: pure-functional-design
description: "Diseña y refactoriza código Rust/Kotlin hacia un núcleo funcional puro: descubre dominio, modela ADTs, invariantes y estados, separa efectos, selecciona algoritmos, define vertical slices y verifica propiedades. Diagnóstico por problemas y refactors reversibles con recetas, lentes contextuales, autodetección de capacidades y opción KEEP_AS_IS; sin reescrituras masivas automáticas."
---

# Pure Functional Design — una entrada, lentes de dominio y de lenguaje

**Propósito:** ofrecer procedimientos genéricos reutilizables para cualquier aplicación compatible, sin vincular el catálogo a proyectos concretos. Lograr lógica sustituible, comprobable y fácil de entender, sin copiar mecánicamente la sintaxis o abstracciones de Haskell. Preferir la solución **más simple que preserve las invariantes**. La pureza se evalúa en el contrato observable de cada función, no contando instrucciones `mut` o `var` locales. Es UNA skill portable; ni framework propio, ni linter de código, ni motor CI.

## Ontología y restricciones

- **Hecho observado**: respaldado por fuente/código y revisión concreta. **Hipótesis**: inferencia sin confirmación; no se materializa como nombre o regla de dominio hasta contrastarla.
- **Concepto**: término del lenguaje ubicuo. **Invariante**: condición que siempre debe cumplirse para un estado válido. **ADT**: producto (campos simultáneos) o suma (alternativas excluyentes), con constructores validados y estados inalcanzables cuando sea viable.
- **Caso de uso**: cambio de estado o consulta relevante para un actor. **Slice**: código end-to-end necesario para un solo caso de uso; NO sinónimo de un módulo por capa técnica.
- **Función pura**: para la misma entrada explícita devuelve el mismo resultado y no causa efectos observables. Captura tiempo, azar, identidad y configuración como datos; interpreta IO en la frontera.
- **Error de dominio**: fallo esperado y tipado. **Efecto**: operación de IO, reloj, red, disco, BD, logging, mutación observable. **Comando/plan de efectos**: dato producido por el núcleo para ser interpretado en un borde.
- **Lente**: guía de diagnóstico y decisión para el agente; NO una `Lens<S,A>` de óptica funcional. Las ópticas se tratan aparte, solo si simplifican modificaciones inmutables profundas.
- **Garantía**: propiedad de negocio que debe conservarse; los tests son una forma de comprobarla, no su identidad.

## Router: observar → descubrir → decidir → aplicar → verificar

1. Identificar la tarea `discovery|design|implementation|refactor|review|catalog`, fase `diagnose|plan|verify`, lenguaje real `rust|kotlin|unknown|other`, señales y restricciones del repositorio. Partir de código productivo, firmas, entradas y salidas reales; documentación es contexto, no evidencia de implementación. Fijar revisión o reconocer `unknown/stale`. No inventar instrumentos ni archivos.
2. Consultar [navigation](references/navigation.md), [problemas](references/problems.json), [recetas](references/recipe-registry.json) y [lens-registry](references/lens-registry.json). Diagnosticar **síntoma, mecanismo causal, evidencia, alternativa y contraindicación**, sin asumir que un patrón equivale a una mejora. El router `scripts/affordances.py` solo recomienda y anuncia rutas locales, nunca lee repos externos ni cambia código. Seleccionar **como máximo 1–3 lentes metodológicas** y adaptar por lenguaje en fase de planificación, no cargar todo el catálogo.
3. Para descubrimiento: comenzar por [problem-diagnosis](references/lenses/problem-diagnosis.md) cuando el problema no esté confirmado. Extraer actores, verbos, eventos, términos, invariantes, fronteras de contexto, vacíos y contradicciones a partir de código/contratos observables. El nombre sugerido es hipótesis hasta validación. No llamar “ontología verificada” a una taxonomía inferida de nombres de ficheros.
4. Antes de modificar código: proponer contratos de entrada/salida, ADTs, errores esperados y transiciones válidas. Dibujar flujo con Mermaid **solo si resuelve ambigüedad**. Distinguir modelos compartibles de traducciones entre bounded contexts.
5. Situar `decide(input, state, context) -> Result<Decision, DomainError>` o equivalente dentro de un slice. Decisión pura, intérpretes de efectos en el borde; persistencia/HTTP/CLI no se filtran al dominio. Si ya existe un seam claro, **no forzar refactor** por patrón.
6. Seleccionar implementaciones nativas: Rust `enum`, `Option`, `Result`, `?`, pattern matching, iteradores, ownership; Kotlin `sealed interface`, `data class`, `copy`, `Result` o Arrow `Raise/Either` según dependencia existente. Evitar HKT/monads/free-monads/optics como requisito general. Estimar clones, asignaciones, almacenamiento persistente, interoperabilidad Java y degradación de rendimiento antes de adoptar abstracciones.
7. Antes de actuar, comparar explícitamente `KEEP_AS_IS`, extracción local y [recetas incrementales](references/recipes/legacy-seam.md). Validar `requires` y `blocks` del catálogo. Una recomendación `APPLY` autoriza **proponer** un cambio, no ejecutarlo ni declararlo validado. `INSPECT_MORE` exige evidencia, `BLOCKED` impide la receta contraindicada. Ejecutar refactors por **slices verticales**, con seam reversible y sin congelar detalles privados. Distinguir semántica preservada de cambios de contrato. Evitar deuda de adaptadores duplicados, coordinadores enormes y modelos "God"; mantener un único propietario de cada regla.
8. Verificar las invariantes con tests unitarios mínimos, ejemplos de frontera y propiedades algebraicas cuando aporten valor. En una migración de legado, caracterizar primero el comportamiento observable, preservar orden de efectos, transacciones, compatibilidad wire/datos, cancelación y concurrencia. Delegar selección/ejecución de tests, UAT efímeros, gates y releases a `delivery-first-testing` si está disponible; nunca declararlos `PASS` sin ejecución y artefacto observado. Prohibido tomar decisiones de borrado solo por cobertura de líneas.
9. Informar: `problema | evidencia OBSERVED/INFERRED | alternativas (incluida KEEP_AS_IS) | decisión | precondiciones/contraindicaciones | regla/invariante | slice | equivalencia | coste/beneficio | pruebas reales o NOT_RUN | riesgos`. Una hipótesis no se presenta como hecho. Ningún commit, publicación, instalación o borrado sin autorización.

## Políticas irrenunciables

- Preservar contratos públicos, compatibilidad, semántica de errores, persistencia, concurrencia, cancelación y orden de efectos. Si cambia alguno, exigir aprobación como **cambio funcional**, no etiquetarlo refactor.
- No introducir mutabilidad compartida donde antes no existía. **Mutabilidad local encapsulada** es admisible si conserva equivalencia observacional y reduce coste; en Rust usar un `Vec` construido localmente puede ser mejor que clonar estructuras en cada `fold`.
- `val List<T>` en Kotlin no prueba inmutabilidad profunda. `suspend` y `Flow` tampoco implican pureza; `Future`, `async` o `Arc` de Rust tampoco.
- Las invariantes reales deben estar respaldadas por términos/casos de uso, no por preferencias estéticas del agente. Evitar estados ilegales en la API pública cuando su coste sea razonable.
- Sin refactor horizontal de todos los módulos, sin cambio de librería por defecto, sin reorganizar carpetas solo por apariencia, sin crear un segundo harness CI.
- Si un módulo utiliza CogniCode con restricciones de lectura, usar exclusivamente sus capacidades permitidas y sus precondiciones; no afirmar que existe un grafo si no se ha obtenido.
- En `unknown` o `stale`: inspeccionar, marcar `BLOCKED` o limitar recomendaciones; jamás aprobar implementación imaginaria.

## Autodescubrimiento y activación por conversación

- `SKILL.md` describe **cuándo usar la skill**; la activación real depende de que el agente anfitrión la anuncie o permita encontrarla. Ninguna referencia a otra skill equivale a instalación.
- Descubrimiento progresivo: **(1)** detectar intención y problema, **(2)** seleccionar lentes `ready` por evidencia, **(3)** en `plan`, consultar solo la receta aplicable, **(4)** en `verify`, descubrir y delegar únicamente a skills incluidas en `available_skills` observadas.
- Recalcular decisiones después de cada nueva evidencia y cada cambio de objetivo; no retener lentes activadas como obligación de otros turnos. No guardar estado nuevo dentro del repositorio ni crear un daemon.
- La ayuda delegada mantiene fronteras: `cognicode-diagrams` observa código con sus precondiciones, `delivery-first-testing` selecciona y verifica garantías. Sin skill disponible: ofrecer inspección/proceso manual sin simular ejecución.

## Navegación rápida

| Situación observada | Lente metodológica | Resultado buscado |
|---|---|---|
| Diagnóstico sin causa confirmada | [problem-diagnosis](references/lenses/problem-diagnosis.md) | hipótesis, evidencia, alternativas y abstención |
| Aplicación legacy sin seam seguro | [legacy-refactoring](references/lenses/legacy-refactoring.md) | estrategia incremental reversible |
| Transformación con coste dudoso | [architectural-economics](references/lenses/architectural-economics.md) | comparar KEEP_AS_IS, riesgo y coste |
| Términos y responsabilidades ambiguas | [domain-discovery](references/lenses/domain-discovery.md) | mapa de lenguaje, invariantes y preguntas abiertas |
| Muchos `null`, booleanos y estados imposibles | [adt-invariants](references/lenses/adt-invariants.md) | tipos válidos y transiciones explícitas |
| Servicio con IO mezclado con reglas | [effects-and-core](references/lenses/effects-and-core.md) | núcleo puro + intérprete de efectos |
| Código horizontal/acoplado | [vertical-slices](references/lenses/vertical-slices.md) | un caso de uso end-to-end aislado |
| Clase/archivo gigante o lógica duplicada | [responsibility-refactor](references/lenses/responsibility-refactor.md) | dueño único de cada regla y seams correctos |
| Bucle/recursión/transformación compleja | [functional-algorithms](references/lenses/functional-algorithms.md) | algoritmo nativo eficiente + justificación |
| Garantías algebraicas y refactors arriesgados | [algebraic-laws](references/lenses/algebraic-laws.md) | leyes + contraejemplos discriminantes |
| Actualizaciones inmutables anidadas | [optics-persistent-data](references/lenses/optics-persistent-data.md) | decidir copy, optics, persistencia o mutación local |

**Lentes de lenguaje:** [Rust](references/languages/rust.md) · [Kotlin](references/languages/kotlin.md). Consultar [primitivas](references/primitives.md), [bibliografía](references/sources.md) y [extensión de lentes](references/extend-lenses.md) únicamente cuando proceda.

**Evaluación portable:** los ejemplos y tests de esta skill son sintéticos y prueban solo sus decisiones; no deben contener diagnósticos de repositorios consumidores ni presentarse como refactors reales. Ver [evaluaciones portables](references/portable-evaluations.md).

**Handoff testing:** la skill produce garantías + particiones + leyes; `delivery-first-testing` decide dónde ejecutarlas y qué evidencia conservar. Ejemplo de sesión en `examples/*.json`; pruebas propias del selector en `tests/`.

**Catálogo de recetas:** [extract-pure-decision](references/recipes/extract-pure-decision.md) · [legacy-seam](references/recipes/legacy-seam.md) · [mikado-refactor](references/recipes/mikado-refactor.md) · [parallel-change](references/recipes/parallel-change.md) · [branch-by-abstraction](references/recipes/branch-by-abstraction.md) · [domain-state-refactor](references/recipes/domain-state-refactor.md) · [algorithm-substitution](references/recipes/algorithm-substitution.md) · [simplify-nested-updates](references/recipes/simplify-nested-updates.md). Consultar solo la necesaria.
