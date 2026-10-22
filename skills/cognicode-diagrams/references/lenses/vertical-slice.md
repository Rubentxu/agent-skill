# Lente futura: vertical-slice — PLANNED

**No activar aún.** La evidencia debe proceder del análisis de **código** suministrado por CogniCode CLI/MCP. Investigar entradas (HTTP/CLI/evento), llamadas, persistencia y efectos mediante consultas de símbolos, subgrafos y fragmentos **en CogniCode**; no leer archivos del checkout, tests, trazas ni configuración con otra herramienta.

Una cadena de llamadas prueba alcanzabilidad estática, **no el orden runtime**. Si CogniCode no proporciona evidencia ordenada, emitir `DYNAMIC_UNSUPPORTED` y representar solo el mapa estático acotado, con incertidumbre explícita. Mermaid flowchart y Structurizr dynamic view no son equivalentes sin dicha prueba. Petición de detalle exige nuevas consultas, no ampliar imaginativamente.
