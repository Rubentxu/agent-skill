# Evidencia de relación por referencia — no equivale a arista de grafo

Un resultado de `find_usages` no aporta un `relation_id` canónico de grafo. El agente **no** inventa uno ni etiqueta la relación como `graph_edge`. Para diagramas admite una segunda procedencia: `reference_link`, condicionada a corroboración de identidad, extremos y localización.

Ejemplo **sintético**:

```json
{
  "claim": {
    "id":"R-7","kind":"relation","relation_source":"reference_link","relation_id":null,
    "plane":"static","from_symbol":"Caller::run","to_symbol":"Service::save",
    "reference":{"query_id":"Q-2","index":0,"path":"src/Caller.java","line":42},
    "query_ids":["Q-1","Q-2"]
  },
  "queries":[
    {"id":"Q-1","capability":"get_symbol_code","mode":"symbol_context","status":"ok",
     "symbol_ids":["Caller::run","Service::save"]},
    {"id":"Q-2","capability":"find_usages","mode":"structured","status":"ok",
     "symbol_ids":["Service::save"],
     "reference_hits":[{"index":0,"path":"src/Caller.java","line":42}]}
  ]
}
```

Validez: la referencia debe estar realmente en la respuesta estructurada y en `query.reference_hits`; el `query_id` debe existir, los extremos deben figurar en consultas estructuradas de esa pregunta, y la fila `index`/archivo/línea debe coincidir. La prueba por símbolo del caller debe permitir identificar el origen real; si se desconoce, no inventarlo. No equiparar `precision_floor=ast-heuristic` a LSP exacto. Un match textual aislado no funda `reference_link`.

Diferencias de procedencia:

| Clase | Identificador | Se puede afirmar |
|---|---|---|
| `graph_edge` | `relation_id` devuelto por operación del grafo | relación estática tipada observada según evidencia del grafo |
| `reference_link` | `query_id` + `index` + `path:line` | uso/referencia localizada y corroborada |
| `INFERRED` | hipótesis sin prueba estructurada | solo como incógnita fuera del modelo factual |

La existencia de un uso de símbolo **no demuestra** petición HTTP, llamada runtime ni despliegue; se representan como `static` con leyenda `reference-backed`. Si el tipo exacto no es demostrable, dibujar «referencia/usa» y no «invoca» ni «depende por API».
