# Evidencias exclusivamente de CogniCode

**Fuente arquitectónica única: respuestas de CogniCode CLI/MCP sobre código implementado.** No citar como prueba README/ADR/roadmaps/tests/manifiestos, ni aunque CogniCode los localice; no abrir por shell/GitHub/ruta. Los diagramas del usuario son `CURATED` para traducción, nunca prueba de implementación.

## Ledger derivado mínimo

Conservar en `~/.cognicode-diagrams/workspaces/<id>/evidence/` un `queries.json` y `claims.json` (o informe equivalente), con metadatos mínimos:

- `query_id`, interfaz `cli|mcp`, versión y operación **descubierta**, argumentos/scope, resultado observado, error, cobertura y omisiones.
- `basis`: workspace/revisión/dirty/snapshot **solo cuando CogniCode lo comunique**; `UNKNOWN` en caso contrario. No consultar Git por separado.
- `claim_id`, tipo `entity|relation`, `symbol_ids` o arista, referencia archivo:línea **devuelta por CogniCode** y `query_ids` concretos.
- `plane` = `static|runtime|deployment`; `status` = `OBSERVED_CODE|INFERRED|UNKNOWN`; limitación explícita y cobertura del claim.
- `next_question` si falta un extremo, precisión, storage, protocolo o distinción entre biblioteca/proceso.

La misma consulta CLI y MCP al mismo backend no equivale a corroboración independiente. Código mostrado por CogniCode puede respaldar una afirmación **solo en el plano que realmente demuestra**. Una inferencia debe indicarse como tal, no etiquetarse `OBSERVED_CODE`.

## Contrato de suficiencia

- Toda entidad y relación factual de un diagrama debe enlazar a claim y consulta(s). Sin ello, quitarla o representarla expresamente como hipótesis en informe, nunca como estructura implementada.
- Grafo vacío, escaneo parcial, truncado, cobertura desconocida o símbolo no resuelto ⇒ no afirmar completitud.
- Call graph solo ⇒ no inferir ejecutables, redes, protocolos, base de datos ni orden temporal.
- Solicitud de más detalle ⇒ nueva consulta CogniCode con más precisión y registro adicional; no generar contenido supuesto.
- CogniCode ausente o sin capacidad suficiente ⇒ `BLOCKED` o `PARTIAL`; se prohíbe abrir archivos objetivo por otra vía.

Para los límites de identidad y el significado de `VERIFIED`, consultar [investigation-contract.md](investigation-contract.md).
