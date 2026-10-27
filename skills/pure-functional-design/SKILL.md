---
name: pure-functional-design
description: "Diseña y refactoriza código Rust/Kotlin hacia un núcleo funcional puro: descubre dominio, modela ADTs, invariantes y estados, separa efectos, selecciona algoritmos, define vertical slices y verifica propiedades. Router con lentes bajo demanda, sin reescrituras masivas automáticas."
---

# Pure Functional Design — una entrada, lentes de dominio y de lenguaje

**Propósito:** lograr lógica sustituible, comprobable y fácil de entender, sin copiar mecánicamente la sintaxis o abstracciones de Haskell. Preferir la solución **más simple que preserve las invariantes**. La pureza se evalúa en el contrato observable de cada función, no contando instrucciones `mut` o `var` locales. Es UNA skill portable; ni framework propio, ni linter de código, ni motor CI.

## Ontología y restricciones

- **Hecho observado**: respaldado por fuente/código y revisión concreta. **Hipótesis**: inferencia sin confirmación; no se materializa como nombre o regla de dominio hasta contrastarla.
- **Concepto**: término del lenguaje ubicuo. **Invariante**: condición que siempre debe cumplirse para un estado válido. **ADT**: producto (campos simultáneos) o suma (alternativas excluyentes), con constructores validados y estados inalcanzables cuando sea viable.
- **Caso de uso**: cambio de estado o consulta relevante para un actor. **Slice**: código end-to-end necesario para un solo caso de uso; NO sinónimo de un módulo por capa técnica.
- **Función pura**: para la misma entrada explícita devuelve el mismo resultado y no causa efectos observables. Captura tiempo, azar, identidad y configuración como datos; interpreta IO en la frontera.
- **Error de dominio**: fallo esperado y tipado. **Efecto**: operación de IO, reloj, red, disco, BD, logging, mutación observable. **Comando/plan de efectos**: dato producido por el núcleo para ser interpretado en un borde.
- **Lente**: guía de diagnóstico y decisión para el agente; NO una `Lens<S,A>` de óptica funcional. Las ópticas se tratan aparte, solo si simplifican modificaciones inmutables profundas.
- **Garantía**: propiedad de negocio que debe conservarse; los tests son una forma de comprobarla, no su identidad.

## Router: observar → descubrir → decidir → aplicar → verificar

1. Identificar la tarea `discovery|design|implementation|refactor|review|catalog`, lenguaje real `rust|kotlin|unknown|other`, señales y restricciones del repositorio. Partir de código productivo, firmas, entradas y salidas reales; documentación es contexto, no evidencia de implementación. Fijar revisión o reconocer `unknown/stale`. No inventar instrumentos ni archivos.
2. Consultar `references/lens-registry.json` y `references/navigation.md`. Seleccionar **1–3 lentes metodológicas** relevantes más, si procede, **una lente de lenguaje**. Respetar `ready`/`planned` y precondiciones. `scripts/affordances.py` es un selector **puro opcional** que calcula enlaces locales y nunca lee un repo ajeno ni lo modifica.
3. Para descubrimiento: extraer actores, verbos, eventos, términos, invariantes, fronteras de contexto, vacíos y contradicciones a partir de código/contratos observables. El nombre sugerido es hipótesis hasta validación. No llamar “ontología verificada” a una taxonomía inferida de nombres de ficheros.
4. Antes de modificar código: proponer contratos de entrada/salida, ADTs, errores esperados y transiciones válidas. Dibujar flujo con Mermaid **solo si resuelve ambigüedad**. Distinguir modelos compartibles de traducciones entre bounded contexts.
5. Situar `decide(input, state, context) -> Result<Decision, DomainError>` o equivalente dentro de un slice. Decisión pura, intérpretes de efectos en el borde; persistencia/HTTP/CLI no se filtran al dominio. Si ya existe un seam claro, **no forzar refactor** por patrón.
6. Seleccionar implementaciones nativas: Rust `enum`, `Option`, `Result`, `?`, pattern matching, iteradores, ownership; Kotlin `sealed interface`, `data class`, `copy`, `Result` o Arrow `Raise/Either` según dependencia existente. Evitar HKT/monads/free-monads/optics como requisito general. Estimar clones, asignaciones, almacenamiento persistente, interoperabilidad Java y degradación de rendimiento antes de adoptar abstracciones.
7. Ejecutar refactors por **slices verticales**, con seam reversible y sin congelar detalles privados. Distinguir semántica preservada de cambios de contrato. Evitar deuda de adaptadores duplicados, coordinadores enormes y modelos "God"; mantener un único propietario de cada regla.
8. Verificar las invariantes con tests unitarios mínimos, ejemplos de frontera y propiedades algebraicas cuando aporten valor. Delegar selección/ejecución de tests, UAT efímeros, gates y releases a `delivery-first-testing` si está disponible; nunca declararlos `PASS` sin ejecución y artefacto observado. Prohibido tomar decisiones de borrado solo por cobertura de líneas.
9. Informar: `evidencia | decisión propuesta | regla/invariante | slice afectado | equivalencia semántica | coste/beneficio | pruebas ejecutadas o NOT_RUN | riesgos restantes`. Una hipótesis no se presenta como hecho. Ningún commit, publicación, instalación o borrado sin autorización.

## Políticas irrenunciables

- Preservar contratos públicos, compatibilidad, semántica de errores, persistencia, concurrencia, cancelación y orden de efectos. Si cambia alguno, exigir aprobación como **cambio funcional**, no etiquetarlo refactor.
- No introducir mutabilidad compartida donde antes no existía. **Mutabilidad local encapsulada** es admisible si conserva equivalencia observacional y reduce coste; en Rust usar un `Vec` construido localmente puede ser mejor que clonar estructuras en cada `fold`.
- `val List<T>` en Kotlin no prueba inmutabilidad profunda. `suspend` y `Flow` tampoco implican pureza; `Future`, `async` o `Arc` de Rust tampoco.
- Las invariantes reales deben estar respaldadas por términos/casos de uso, no por preferencias estéticas del agente. Evitar estados ilegales en la API pública cuando su coste sea razonable.
- Sin refactor horizontal de todos los módulos, sin cambio de librería por defecto, sin reorganizar carpetas solo por apariencia, sin crear un segundo harness CI.
- Si un módulo utiliza CogniCode con restricciones de lectura, usar exclusivamente sus capacidades permitidas y sus precondiciones; no afirmar que existe un grafo si no se ha obtenido.
- En `unknown` o `stale`: inspeccionar, marcar `BLOCKED` o limitar recomendaciones; jamás aprobar implementación imaginaria.

## Navegación rápida

| Situación observada | Lente metodológica | Resultado buscado |
|---|---|---|
| Términos y responsabilidades ambiguas | [domain-discovery](references/lenses/domain-discovery.md) | mapa de lenguaje, invariantes y preguntas abiertas |
| Muchos `null`, booleanos y estados imposibles | [adt-invariants](references/lenses/adt-invariants.md) | tipos válidos y transiciones explícitas |
| Servicio con IO mezclado con reglas | [effects-and-core](references/lenses/effects-and-core.md) | núcleo puro + intérprete de efectos |
| Código horizontal/acoplado | [vertical-slices](references/lenses/vertical-slices.md) | un caso de uso end-to-end aislado |
| Clase/archivo gigante o lógica duplicada | [responsibility-refactor](references/lenses/responsibility-refactor.md) | dueño único de cada regla y seams correctos |
| Bucle/recursión/transformación compleja | [functional-algorithms](references/lenses/functional-algorithms.md) | algoritmo nativo eficiente + justificación |
| Garantías algebraicas y refactors arriesgados | [algebraic-laws](references/lenses/algebraic-laws.md) | leyes + contraejemplos discriminantes |
| Actualizaciones inmutables anidadas | [optics-persistent-data](references/lenses/optics-persistent-data.md) | decidir copy, optics, persistencia o mutación local |

**Lentes de lenguaje:** [Rust](references/languages/rust.md) · [Kotlin](references/languages/kotlin.md). Consultar [primitivas](references/primitives.md), [bibliografía](references/sources.md) y [extensión de lentes](references/extend-lenses.md) únicamente cuando proceda.

**Handoff testing:** la skill produce garantías + particiones + leyes; `delivery-first-testing` decide dónde ejecutarlas y qué evidencia conservar. Ejemplo de sesión en `examples/*.json`; pruebas propias del selector en `tests/`.
