# Lente: descubrimiento ontológico orientado al código

**Pregunta:** ¿qué conceptos, hechos, reglas y límites dan sentido al comportamiento implementado? **Señales:** `domain-ambiguity`, `cross-context`, `unknown`.

## Algoritmo

1. Elegir un caso de uso real (comando/endpoint/CLI) y observar input, salida, llamadas, invariantes ya aplicadas, datos persistidos y eventos. Anotar rutas/símbolos y revisión; si falta código, `BLOCKED`.
2. Extraer *hechos* (qué pasó, pasado: `OrderSubmitted`), *órdenes* (qué se solicita: `SubmitOrder`), *consultas* (`GetOrder`) y actores. Evitar confundir nombres técnicos (`OrderDTO`) con dominio.
3. Establecer secuencia `Actor → Command → Policy/Decision → Event/Rejected → Effects`, vinculando cada decisión a su implementación actual o a una hipótesis explícita.
4. Construir diccionario `término | significado | contexto | dueño | evidencia | conflicto`; buscar homónimos entre contextos. Identificar subdominio y bounded contexts solo donde las reglas divergen.
5. Formular invariantes con condiciones refutables: `CannotPublishDraft`, `NoDuplicateRunId`, `TotalNonNegative`; separar validación de formato, validación contextual e integridad transaccional.
6. Detectar duplicaciones semánticas: la misma regla aplicada en controlador y repositorio, cambios de nombres entre CLI y API, mapeos inconsistentes, estados que no son verdaderos estados.
7. Proponer un ADT y un flujo para el slice concreto, **no** una ontología global compartida. Indicar dudas que necesita resolver alguien conocedor del dominio.

**Contrapruebas:** no inventar `SagaCompleted` por encontrar una clase `SagaManager`; un enum transportado por JSON puede ser vocabulario de protocolo y no verdad del dominio. Un DB schema puede representar legado, no modelo conceptual deseable.

**Salida mínima:** 5–15 términos relevantes, 1–5 invariantes, dueño de cada decisión, mapa de contexto del slice, hechos vs hipótesis, primer seam barato. Referencias: Wlaschin *Domain Modeling Made Functional*, Fowler *Bounded Context*, EventStorming.
