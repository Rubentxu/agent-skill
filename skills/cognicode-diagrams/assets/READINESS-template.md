# CogniCode — ficha de preparación (solo resultados CLI/MCP)

- **Estado**: `READY_FOR_C4_DISCOVERY | PARTIAL | BLOCKED`
- **Workspace derivado**: `<ruta HOME>`
- **Ruta objetivo explícita**: `<ruta proporcionada; nunca explorada directamente>`
- **Identidad de análisis**: `<snapshot/revision/dirty emitidos por CogniCode o UNKNOWN>`
- **CLI/MCP comprobados**: `<versión real, interfaz, schema, perfil>`
- **Discovery ejecutado**: `<--help/capabilities/tools-list paginado y resultados>`
- **Consultas sobre código**: `<query_id, operación y argumentos reales>`
- **Cobertura**: `<estado, omisiones, truncamientos, desconocidos>`
- **Contrastes de implementación**: `<fragmentos de código devueltos por CogniCode y claim_ids>`
- **Fuentes alternativas leídas**: `NINGUNA; si existen, invalida declaración de exclusividad`

## Claims trazables

| Claim | Plano | Evidencia de CogniCode | Estado | Limitación |
|---|---|---|---|---|
| R-1 | static | query_id + símbolo/arista + referencia código devuelta | OBSERVED_CODE | alcance parcial |

## Próxima consulta

`<pregunta abierta, operación anunciada y ámbito>`

> Los documentos/ADR/README no acreditan arquitectura, aunque CogniCode los encuentre. Un reporte de escaneo no certifica cobertura completa. El proyector solo consume artefactos derivados.
