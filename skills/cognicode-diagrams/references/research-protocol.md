# Pregunta → capacidad → evidencia — protocolo ejecutable

**No usar todas las herramientas.** Elegir la capacidad más barata y pertinente para la pregunta actual, siempre del runtime real.

## Tabla de orientación (roles, NO comandos)

| Pregunta | Roles candidatos, por prioridad | Hecho requerido |
|---|---|---|
| Localizar responsabilidades | `symbol_index`, `intent_search`, `symbol_context` | identidad y ubicación de símbolo |
| Entender símbolo | `symbol_context`, `members`, `type_references` | código por símbolo, tipos y miembros |
| Identificar colaboradores | `references`, `implementors`, `call_hierarchy` | extremos y relación |
| Seguir interacción | `subgraph`, `trace_path` | camino estático acotado |
| Organizar vista | `communities`, `graph_query` | grupos y subgrafos |
| Analizar impacto de cambio | `impact_analysis`, `call_hierarchy`, `references`, `graph_query` | recorrido dirigido, origen, alcance y dirección de dependencias |
| Investigar estructura de dependencias | `communities`, `graph_query`, `references`, `symbol_index` | entidades y aristas probadas en un alcance delimitado |
| Descomponer bloques trazables | `symbol_context`, `members`, `type_references`, `graph_query` | identidad de cada bloque y relación respaldada por CogniCode |

Los roles son ontología **de la skill**, no nombres invocables. El agente asocia cada rol exclusivamente con una operación **anunciada por CogniCode real** y su schema observado. Candidatas posibles incluyen `query_symbol_index`, `get_symbol_code`, `find_references`, `get_implementors`, `get_call_hierarchy`, `trace_path`, `graph_communities`, **solo si se descubren**. No inventar comandos, no requerir todas las candidatas.

## Sondeo acotado por capacidad + lenguaje

Tomar un **símbolo real devuelto por CogniCode**, nunca deducido de README/ADR. Para cada operación pertinente registrar:

- ¿El índice puede localizarlo? ¿Se devuelven símbolo inequívoco y ubicación?
- ¿Se obtiene contexto de implementación, preferentemente por símbolo?
- ¿Resuelve la relación solicitada o informa ausencia/limitación?
- ¿Cuál es la cobertura y precisión observada? `complete|partial|unknown` y omisiones.

Cada capacidad tiene un mapa `probes` indexado **por lenguaje del proyecto**. El resultado por lenguaje tiene `status=untried|usable|partial|failed|unsupported`, `query_id`, `symbol_id`, `location`, `context=present|missing|unknown`, `relations=present|missing|unknown`, `coverage`. Ningún resultado de una operación basta para afirmar incompatibilidad de todo un lenguaje. Si `build_graph` falla para Kotlin, probar otra consulta estructurada pertinente; no pasar a `read_file(raw)`.

## Contrato mínimo de sesión

Se trabaja **una pregunta concreta por sesión**; combinar luego claims contrastados de varias sesiones, nunca promesas o suposiciones. El router recibe `research` con:
- `catalog=unknown|observed`.
- `question={id,text,kind,language,target}`; kind: `responsibilities`, `understand_symbol`, `collaborators`, `interaction`, `view_grouping`, `change_impact`, `dependency_structure` o `traceable_decomposition`.
- `capabilities[]` con nombre/runtime, rol, lenguajes, `advertised`, `schema_observed` y `probes:{lenguaje:probe}`. Nunca usar el probe de Rust para certificar Kotlin.
- `queries[]` con `id`, `question_id`, `capability`, `target`, `mode=structured|symbol_context|text_candidate`, `status`, `coverage`, `symbol_ids`, `relation_ids` y `observation_plane`.
- `claims[]` con `id`, `question_id`, `kind=entity|relation`, `status=observed`, `plane`, `query_ids` y `symbol_id` o `from_symbol,to_symbol,relation_id`.
- `diagram_claim_ids[]` = exactamente las afirmaciones que se van a representar; `max_queries` por defecto 4 y como máximo 12.

Consultar [el ejemplo](../examples/session-c4.json), que es **sintético**, no evidencia de un repositorio real.

## Estados y acciones verificables

| Observación | Acción | Regla |
|---|---|---|
| No hay pregunta | `formulate-question` | no dibujar |
| Falta catálogo | `discover-capabilities` | usar CLI/MCP real |
| Herramienta pertinente aún no probada | `probe-capability` | símbolo real, por lenguaje |
| Herramienta probada y relevante | `query-structured` | respuesta estructurada y acotada |
| Claim del diagrama sin símbolo/arista apoyados | `justify-claims` | eliminarlo o recabar prueba, no dibujarlo como hecho |
| Claims trazados a consultas suficientes | `EVIDENCE_READY` | dejar de consultar; proyección autorizada |
| Capacidad agotada o presupuesto superado | `PARTIAL/UNKNOWN` | detenerse, nunca exploración alternativa |
| Lectura raw/repositorio u otro indexador usada | `BLOCKED` | no declarar exclusividad |

**`search_content` solo localiza candidatos** (`text_candidate`), confirmados después por operación estructurada; `read_file(raw)` nunca valida un claim. Un `relation` necesita sus dos símbolos y el `relation_id` de la respuesta. `runtime` o `deployment` necesitan evidencia del mismo plano, no una arista `static`. Los `code_refs` emitidos por CogniCode pueden citarse, **no** autorizan abrir rutas. Todos los IDs de consulta deben existir y pertenecer a la misma pregunta.

**Antibucle:** no repetir una capacidad sobre el mismo `target` cuando no hubo progreso; elegir otra capacidad de roles compatibles o terminar `PARTIAL`. Más detalle significa nueva pregunta/id/alcance. Una respuesta suficiente **elimina consultas adicionales**.

La decisión pura verifica consistencia de **datos declarados**, no autenticidad criptográfica de respuestas CLI/MCP. El agente debe registrar el resultado real y una UAT debe comprobar que no inventa observaciones. Esta skill **no ofrece ningún modo alternativo de lectura de código por el LLM**. Si el runtime CogniCode no acredita el dato, detenerse en `PARTIAL/UNKNOWN`; jamás usar `read_file(raw)`, shells, agentes exploradores o repositorios remotos para obtenerlo.

## Gate de omisiones antes de dibujar

El estado `research` requiere `scope`: `source=cognicode`, `report_id`, `languages` realmente observados, `coverage=complete|partial|unknown`, `omissions_complete` y `omitted_files[]`. Cada elemento omitido incluye `path`, `relevance=relevant|irrelevant|unknown` y `review_query_ids`. **Todos estos valores proceden de respuestas de CogniCode**, no de búsquedas directas.

- Si CogniCode no informa lista exhaustiva de omitidos, registrar `omissions_complete=false`; una lista vacía no significa «sin omisiones». Acción `assess-coverage`, después `PARTIAL` si sigue sin respuesta.
- Si hay omitidos con relevancia desconocida, acción `assess-omissions` mediante una capacidad **estructurada**; nunca leer el archivo omitido con shell, GitHub o `read_file(raw)`.
- Si un archivo omitido es relevante para una entrada/relación de la vista, terminar `PARTIAL` incluso cuando los claims ya registrados tengan símbolos.
- Para acreditar `irrelevant` se necesita `review_query_ids` referenciado a una consulta estructurada satisfactoria con la ruta explícita en `coverage_paths`. Si falta evidencia, `PARTIAL`.
- Si `scope.coverage=partial` y los omitidos son justificadamente irrelevantes, se puede generar una **vista acotada**, pero no etiquetarla como verificación global. `VERIFIED` exige cobertura `complete`.

La prueba de la capacidad se guarda en `capabilities[].probes[language]` sobre un símbolo real; la disponibilidad anunciada no equivale a prueba para cada lenguaje. Probar solo las capacidades pertinentes a la pregunta y detener las consultas cuando haya evidencia suficiente. Las pruebas puras del router no ejecutan los parsers Kotlin/Rust; UAT real con CogniCode sigue `NOT_RUN`.

## Contrato ampliado — sesión, catálogo y referencias (obligatorio)

Consultar [preflight por sesión y lenguaje](session-preflight.md) antes de C4. La tabla inicial es ontología, **no es un inventario de requisitos**: cada tool observada incorpora `requires_graph:boolean`, `requires_persistence:boolean`, `stability:stable|experimental|deprecated`, y `prerequisites`/limitaciones si se anuncian. El router puro exige `language_registry`, `session` y, para cierre, `view.node_count/max_nodes`.

Una relación tiene `relation_source=graph_edge|reference_link`. Solo `graph_edge` requiere `relation_id`; `reference_link` exige `query_id + index + path:line` y símbolos corroborados; ver [evidencia por referencias](evidence-reference-links.md). La ausencia de grafo se repara con `build-graph` en el mismo proceso o se evita con referencia, nunca se etiqueta `UNSUPPORTED`. La escalera es `symbol_index → references → graph/session → symbol_context → PARTIAL`, con corte temprano por suficiencia de evidencia.

Si `language_registry.support != supported`, un C4 global pasa a `PARTIAL`; se puede realizar un alcance acotado con `view_scope=bounded` pero su evidencia y cobertura siguen siendo limitadas. Si el grafo está marcado `current` sin `graph_owner == session.id` y base observada, no se acepta como listo. `reference_hits` se indexan desde **cero** según orden preservado de resultados; una tool que no preserve orden debe aportar identificador estable y adaptar el contrato explícitamente, nunca asignar índices al azar.

## Preguntas C4 y aprovechamiento del atlas

C1: fronteras y actores si están demostrados. C2: entradas ejecutables (no crates), clientes externos y stores. C3: colaboradores, miembros, tipos y relaciones. Flujo: secuencia **declarada en código**, etiquetada estática hasta observar ejecución. En todos: omisiones relevantes y presupuesto de consultas; no ejecutar categorías de conocimiento completas por rutina. Registrar cada resultado útil y sincronizar el atlas, sin consultas adicionales para decorarlo.
