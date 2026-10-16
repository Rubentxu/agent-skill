# Preflight de sesión, capacidades y lenguajes (CogniCode instalado)

## Orden obligatorio (antes de cada pregunta C4)

1. Identificar versión **instalada** de CogniCode y transport `mcp|cli` con `--help` real / `initialize` + `tools/list`. No usar el catálogo del repositorio como si fuera el runtime. Guardar proceso/sesión, perfil, argumentos y origen.
2. Consultar el registro real de lenguajes anunciado por la instalación (catálogo expuesto o producto instalado vía **CogniCode**, nunca abrir `product/languages.json` del checkout objetivo). Guardar lenguaje exacto, versión, soporte `supported|partial|unsupported|not_listed|unknown` para **cada lenguaje** y alcance prometido. Si Kotlin no está listado: no prometer C4 global. Sí puede hacerse una vista acotada con sondas Kotlin positivas y estado `PARTIAL`.
3. Leer campos observados del catálogo **por herramienta**: `requires_graph`, `requires_persistence`, `stability`, `prerequisites`, `limitations`, `public_profiles`, schema y versión. Los flags en `runtime_metadata` y `requirements` pueden diferir: detectar conflicto y tratarlo como `UNKNOWN` hasta medir, no elegir silenciosamente uno.
4. Si `requires_persistence=true`, verificar persistencia/permiso antes de elegirla; no crear base de datos automáticamente. Preferir una operación sin persistencia para responder.
5. Si `requires_graph=true`, validar que **el mismo proceso MCP vivo** tiene grafo del mismo workspace/base. El éxito de `build_graph` en una invocación CLI independiente **no acredita** el grafo de otra. Ejecutar `build_graph` en el proceso que realizará `get_call_hierarchy`, `graph_query`, etc., y registrar respuesta, base, cobertura, skipped_files y process/session id. Cualquier reinicio o cambio de revisión invalida la garantía. Solo permitir composición CLI atómica si la versión instalada documenta/ejecuta ambas operaciones dentro de un mismo proceso.
6. `No graph available` es **precondición insatisfecha**: se clasifica `NO_GRAPH_AVAILABLE`, se reconstruye una única vez en sesión si merece el coste, o se cambia a referencias estructuradas. Jamás inferir «herramienta/lenguaje no soportado».
7. Realizar una sonda por herramienta/lenguaje sobre un símbolo real; `stability=experimental` exige señalización y nunca puede elevar precisión o garantías. Tras resultado estructurado útil, parar.

## Matriz de orientación (verificar contra catálogo instalado)

| Capacidad/rol | Grafo | Persistencia | Preflight |
|---|---|---|---|
| `query_symbol_index`, `find_usages`, `find_references`, `get_symbol_code` | catálogo actual: no | catálogo actual: no | índice/símbolo/contexto y lenguaje |
| `get_call_hierarchy`, `trace_path`, `graph_query`, `graph_insights` | catálogo actual: sí | catálogo actual: no | `build_graph` en mismo proceso + base |
| `build_graph` | no (productor) | no | workspace, permisos, cobertura |
| `list_evidence`, `search_evidence`, `detect_drift` | comprobar tool | catálogo actual: sí | almacenamiento/permiso |

Esta tabla es orientativa y fue contrastada con `Rubentxu/CogniCode/product/tools.json` del 2026-10-17; **manda el catálogo de la instalación que corre**. `build_lightweight_index` puede tener semántica distinta de `build_graph`: no intercambiarlos sin confirmar requisitos reales.

## Estado de router sintético (no es prueba real)

```json
{
  "language_registry":{"source":"cognicode","version":"installed-version","language":"java","support":"supported"},
  "view_scope":"global",
  "session":{"id":"mcp-pid/session-id","transport":"mcp","graph_state":"absent","graph_owner":null,"graph_basis":null,"graph_attempts":0,"persistence":"absent"},
  "capabilities":[{"name":"find_usages","role":"references","languages":["java"],"advertised":true,"schema_observed":true,"requires_graph":false,"requires_persistence":false,"stability":"stable","probes":{"java":{"status":"untried"}}}],
  "view":{"node_count":10,"max_nodes":15}
}
```

El helper solo valida consistencia del estado **declarado**. No descubre catálogo, no construye grafos ni verifica que `id` sea un PID real. Evidencia de sesión y callbacks deben proceder de llamadas CogniCode observadas.

## Escalera de degradación

`símbolo inequívoco → referencias localizadas → grafo actual en sesión (si añade valor) → contexto por símbolo → PARTIAL/UNKNOWN`.

Para una relación `reference_link` nunca inventar `relation_id`: registrar localización `query_id + index + path:line`, símbolos de ambos extremos respaldados y precisión/proveedor. Es una dependencia **derivada de referencias**, no una `graph_edge`. Cualquier ambigüedad del origen o salida de una referencia impide representar una llamada directa; reducir granularidad (archivo/componente) o marcar parcial.

## Alcance y costes

Primero un C4 C2 pequeño y evidenciado; zoom a C3 por contenedor o bounded context. **Máximo recomendado: 15 nodos visibles por vista** (hard limit configurable entre 1 y 20 para las vistas generadas); 29 nodos exigen `split-view`, no reducir fuentes ni meter texto ilegible. Dividir por responsabilidad o actor; preservar vínculos cruzados en atlas/leyenda.

Referencias: [protocolo](research-protocol.md), [evidencia](evidence.md), [C4](lenses/c4.md), [navegación](navigation.md).

**Regla antibucle:** registrar `session.graph_attempts` y resultado real de cada intento. Tras un `build_graph` fallido, establecer `graph_state=failed`/`graph_attempts=1` y buscar `symbol_context` u otra vía; **no volver a emitir build-graph para la misma pregunta/sesión sin una condición nueva**. Registrar `language_registry.language` idéntico al lenguaje consultado, nunca heredar un preflight Rust para Kotlin.
