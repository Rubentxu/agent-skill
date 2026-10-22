# Evidencias exclusivamente de CogniCode

**Fuente arquitectónica única: respuestas de CogniCode CLI/MCP sobre código implementado.** No citar como prueba README/ADR/roadmaps/tests/manifiestos, ni aunque CogniCode los localice; no abrir por shell/GitHub/ruta. Los diagramas del usuario son `CURATED` para traducción, nunca prueba de implementación.

## Utilización inmediata de las evidencias

Tras registrar cada observación útil, sincronizar el [atlas incremental](knowledge-atlas.md). Solo `claim_ids` respaldados por CogniCode se enlazan a renders y vistas; una imagen no añade prueba arquitectónica. Guardar fuentes en workspace externo, nunca en checkout.

## Ledger derivado mínimo

Conservar en `~/.cognicode-diagrams/workspaces/<id>/evidence/` un `queries.json` y `claims.json` (o informe equivalente), con metadatos mínimos:

- `query_id`, interfaz `cli|mcp`, versión y operación **descubierta**, `mode`, argumentos/scope, `symbol_ids` resueltos, resultado observado, error, cobertura y omisiones.
- `basis`: workspace/revisión/dirty/snapshot **solo cuando CogniCode lo comunique**; `UNKNOWN` en caso contrario. No consultar Git por separado.
- `claim_id`, tipo `entity|relation`, `symbol_id` o arista, referencia archivo:línea **devuelta por CogniCode** y `query_ids` concretos.
- `plane` = `static|runtime|deployment`; `provenance` = `OBSERVED_CODE|INFERRED|UNKNOWN`; limitación explícita y cobertura del claim.
- `next_question` si falta un extremo, precisión, storage, protocolo o distinción entre biblioteca/proceso.

### La forma, que es una sola

Los nombres de campo de arriba están escritos como los entiende el motor, no como los entiende el contrato. El contrato tiene una forma única, y el ledger debe usarla:

- Una **consulta** declara `query_id`, `mode` (`structured|symbol_context`), `status` (`ok|partial`), `source` (`cognicode`), `observation_plane` (`static`), `symbol_ids` con los símbolos que la respuesta resolvió, `relation_ids` cuando la respuesta trajo relaciones, y `reference_hits` con las filas de uso cuando la respuesta fue de usos.
- Una **afirmación** declara `claim_id`, `kind` (`entity|relation`), `provenance` (`OBSERVED_CODE|INFERRED|UNKNOWN|CODE_DOC|CURATED_INTENT`), `plane`, `coverage` (`complete|partial|unknown`) y `query_ids`. Si es una entidad, declara `symbol_id`; si es una relación, declara `relation_source` (`graph_edge|reference_link`), sus dos extremos y, según la procedencia, `relation_id` o `reference`.

Este es el ejemplo canónico. Las pruebas lo ejecutan: si el ejemplo y el contrato dejan de coincidir, la suite falla.

```json canonical
{
  "queries": [
    {"query_id": "Q-1", "mode": "structured", "status": "ok", "source": "cognicode",
     "observation_plane": "static", "symbol_ids": ["App::Entry", "App::Store"],
     "relation_ids": ["edge-1"]},
    {"query_id": "Q-2", "mode": "structured", "status": "ok", "source": "cognicode",
     "observation_plane": "static", "symbol_ids": ["App::Entry", "App::Store"],
     "reference_hits": [{"index": 0, "path": "src/entry.rs", "line": 42}]}
  ],
  "claims": [
    {"claim_id": "C-1", "kind": "entity", "provenance": "OBSERVED_CODE", "plane": "static",
     "coverage": "complete", "symbol_id": "App::Entry", "query_ids": ["Q-1"]},
    {"claim_id": "R-1", "kind": "relation", "provenance": "OBSERVED_CODE", "plane": "static",
     "coverage": "partial", "relation_source": "graph_edge", "relation_id": "edge-1",
     "from_symbol": "App::Entry", "to_symbol": "App::Store", "query_ids": ["Q-1"]},
    {"claim_id": "R-2", "kind": "relation", "provenance": "OBSERVED_CODE", "plane": "static",
     "coverage": "partial", "relation_source": "reference_link",
     "from_symbol": "App::Entry", "to_symbol": "App::Store",
     "reference": {"query_id": "Q-2", "index": 0, "path": "src/entry.rs", "line": 42},
     "query_ids": ["Q-1", "Q-2"]}
  ]
}
```

`python3 scripts/evidence.py --repo <raíz> --check` dice, afirmación por afirmación, qué sostiene la evidencia y qué falta para sostenerla más.

### Lo que se escribe y lo que se deduce

`provenance` dice **qué se observó**. Es de quien investigó, y por eso lo escribe. Si lo que se observó fue una inferencia, se escribe `INFERRED`; si no se pudo observar, `UNKNOWN`. Una inferencia nunca se etiqueta `OBSERVED_CODE`.

La **corroboración** es otra cosa, y no la escribe nadie: la deducen las consultas. Una afirmación está corroborada cuando una consulta estructurada identifica lo que la afirmación sostiene: el símbolo, o el identificador de relación que devolvió el grafo, o la fila de uso con su sitio exacto en el disco. `python3 scripts/evidence.py --repo <raíz> --check` falla cuando una afirmación dice `OBSERVED_CODE` y ninguna consulta la corrobora, y dice qué falta.

Por eso una afirmación puede estar **observada y no corroborada**: se vio algo, pero lo que se vio no se puede volver a señalar con una consulta. Eso no es lo mismo que no haberlo visto, y no se confunde.

La misma consulta CLI y MCP al mismo backend no equivale a corroboración independiente. Código mostrado por CogniCode puede respaldar una afirmación **solo en el plano que realmente demuestra**. Una inferencia debe indicarse como tal, no etiquetarse `OBSERVED_CODE`.

## Contrato de suficiencia

- Toda entidad y relación factual de un diagrama debe enlazar a claim y consulta(s). Sin ello, quitarla o representarla expresamente como hipótesis en informe, nunca como estructura implementada.
- Grafo vacío, escaneo parcial, truncado, cobertura desconocida o símbolo no resuelto ⇒ no afirmar completitud.
- Call graph solo ⇒ no inferir ejecutables, redes, protocolos, base de datos ni orden temporal.
- Solicitud de más detalle ⇒ nueva consulta CogniCode con más precisión y registro adicional; no generar contenido supuesto.
- CogniCode ausente o sin capacidad suficiente ⇒ `BLOCKED` o `PARTIAL`; se prohíbe abrir archivos objetivo por otra vía.

Para los límites de identidad y el significado de `VERIFIED`, consultar [investigation-contract.md](investigation-contract.md).


## Comprobación estructurada por pregunta

Se exige el estado `research` del [protocolo de preguntas](research-protocol.md), además de los campos clásicos del ledger. Una consulta **anunciada** no acredita funcionalidad: almacenar sondeo por capacidad y lenguaje (símbolo real, ubicación, contexto, relaciones y cobertura), y después la operación productiva que soporta el claim.

- Un `query_id` que procede de `read_file(raw)`, del checkout, de otro indexador o únicamente de `search_content` **no respalda** una entidad/arista como implementada.
- Cada arista `graph_edge` factual incluye `from_symbol`, `to_symbol` y `relation_id` observado. Una relación `reference_link` usa **query_id + índice + archivo:línea**, no relation_id; consultar [contrato de referencias](evidence-reference-links.md). Ninguna acredita comunicación runtime/despliegue por sí misma.
- El cierre `EVIDENCE_READY` demuestra consistencia de **los claims declarados** para **esa pregunta**, no cobertura completa del lenguaje, ni autenticidad de las respuestas del agente.
- Si hay nueva petición de detalle, registrar nueva pregunta, capacidad seleccionada, pruebas y consultas. Si no hay progreso, terminar `PARTIAL/UNKNOWN`, sin repetir la misma operación hasta agotar contexto.
- Cuando la consulta estructurada ya es suficiente, evitar búsquedas y lecturas extra: no aportan valor ni elevan certificación.

## Evidencia sobre ficheros omitidos

Guardar `scope.report_id`, `scope.languages`, `scope.coverage`, `scope.omissions_complete` y por cada fichero excluido la ruta **devuelta por CogniCode**, la relevancia para la pregunta y las consultas estructuradas que fundamentan esa decisión. `omitted_files=[]` solo es concluyente cuando el propio análisis informa una lista completa. La identidad de símbolo y la verificación por lenguaje son requisitos distintos de la cobertura. No atribuir a Kotlin un probe observado únicamente en Rust.

## Procedencia del mapa

El atlas usa los campos opcionales `category`, `provenance`, `plane`, `coverage` y `attributes` sin alterar la autoridad de las observaciones CogniCode. `CODE_DOC` no prueba funcionalidad; `CURATED_INTENT` requiere curador; `DOC_INTENT` no está autorizado. No añadir una arista ni runtime desde un mero render. [Reglas](visual-evidence.md).
