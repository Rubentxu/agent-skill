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

Los roles son ontología **de la skill**, no nombres invocables. El agente asocia cada rol exclusivamente con una operación **anunciada por CogniCode real** y su schema observado. Candidatas posibles incluyen `query_symbol_index`, `get_symbol_code`, `find_references`, `get_implementors`, `get_call_hierarchy`, `trace_path`, `graph_communities`, **solo si se descubren**. No inventar comandos, no requerir todas las candidatas.

## Sondeo acotado por capacidad + lenguaje

Tomar un **símbolo real devuelto por CogniCode**, nunca deducido de README/ADR. Para cada operación pertinente registrar:

- ¿El índice puede localizarlo? ¿Se devuelven símbolo inequívoco y ubicación?
- ¿Se obtiene contexto de implementación, preferentemente por símbolo?
- ¿Resuelve la relación solicitada o informa ausencia/limitación?
- ¿Cuál es la cobertura y precisión observada? `complete|partial|unknown` y omisiones.

El registro `probe` tiene `status=untried|usable|partial|failed|unsupported`, `query_id`, `symbol_id`, `location`, `context=present|missing|unknown`, `relations=present|missing|unknown`, `coverage`. Ningún resultado de una operación basta para afirmar incompatibilidad de todo un lenguaje. Si `build_graph` falla para Kotlin, probar otra consulta estructurada pertinente; no pasar a `read_file(raw)`.

## Contrato mínimo de sesión

Se trabaja **una pregunta concreta por sesión**; combinar luego claims contrastados de varias sesiones, nunca promesas o suposiciones. El router recibe `research` con:
- `catalog=unknown|observed`.
- `question={id,text,kind,language,target}`; kind: `responsibilities`, `understand_symbol`, `collaborators`, `interaction` o `view_grouping`.
- `capabilities[]` con nombre/runtime, rol, lenguajes, `advertised`, `schema_observed` y `probe`.
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

La decisión pura verifica consistencia de **datos declarados**, no autenticidad criptográfica de respuestas CLI/MCP. El agente debe registrar el resultado real y una UAT debe comprobar que no inventa observaciones. Investigación textual alternativa autorizada es un **modo separado**, no `IMPLEMENTATION_GROUNDED` ni sustituto automático.
