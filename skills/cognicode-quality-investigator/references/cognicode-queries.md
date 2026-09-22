# CogniCode: seleccionar consultas que sirvan a la pregunta

La herramienta es **un medio de extracción, no una autoridad de calidad**. Usa el servidor MCP ya conectado o el binario `cognicode` existente. Para MCP consulta el catálogo de tools y el esquema real; para CLI usa `cognicode --help` y la ayuda del subcomando. Los nombres aquí son orientativos para la interfaz que los exponga: no inventes opciones ni fuerces correspondencias entre CLI y MCP.

## Ruta corta para investigar

1. **Situar el código:** `get_file_symbols`, `query_symbol_index`, `get_symbol_code`, `go_to_definition`, `read_file` o `search_content`. CLI: `cognicode index outline/query/symbol-code` o lectura directa, según la ayuda.
2. **Explorar relaciones:** `find_references`, `find_usages`, `get_call_hierarchy`, `build_call_subgraph`, `trace_path`. CLI: `cognicode navigate references`, `graph hierarchy/on-demand/trace-path`, cuando estén disponibles. Construir `build_graph` o `graph full` solo si se necesita la vista global y se permiten sus efectos.
3. **Acotar impacto y focos:** `analyze_impact`, `get_entry_points`, `get_leaf_functions`, `get_hot_paths`, `get_complexity`. CLI: `graph impact/entry-points/leaf-functions/hot-paths/complexity` si su ayuda los ofrece. Son **candidatos**, nunca hallazgos automáticos.
4. **Corroborar:** recuperar el código y contratos concretos de ambos extremos; contrastar con build, test, CI u otra observación pertinente. Guardar consulta real, resultado, alcance, omisiones y SHA.

Si la interfaz no ofrece una operación, usa otra fuente verificable para esa pregunta y registra la limitación. No hay obligación de invocar todas las operaciones.

## Recetas vinculadas a las doce dimensiones

| Dimensión original | Pregunta para CogniCode | Qué demuestra realmente / qué falta |
|---|---|---|
| D01 Arquitectura y límites | Localizar port/adapter, sus usos, llamadas y entradas (`get_file_symbols` → `find_usages` → `go_to_definition`). | El grafo de llamadas no es un grafo de imports de módulos. Contrasta build, código de ambos extremos, DI y regla vigente. |
| D02 SOLID y tipos funcionales | Buscar contrato, implementaciones, consumidores, ramas y código relevante (`get_symbol_code` + referencias). | Una clase grande o un valor nullable no prueba violación; verificar contrato, extensión y tests. |
| D03 Connascence | Encontrar declaración y todos sus consumidores; comparar acuerdos de tipos, parámetros, nombres, significados y algoritmos. | Identificar **dos elementos que deben cambiar juntos**, motivo, distancia y prueba de ruptura; no inventar SCIJ. |
| D04 Duplicación/acoplamiento/cohesión/complejidad | Examinar símbolos y cuerpos; usar `get_complexity`/jerarquía para seleccionar candidatos. | Validar semántica de duplicados y parser. Fan-in y tamaño no equivalen a baja cohesión. |
| D05 Deuda | Usar `analyze_impact` para consumidores de una deuda o zona modificada. | Contrastar con Git/ADR/issue y estado actual; distinguir preexistente de regresión. |
| D06 Tests/cobertura | Identificar rutas afectadas con `analyze_impact`, `find_usages` y entradas. | Ejecutar tests autorizados y leer resultados/cobertura reales; grafo no mide cobertura. |
| D07 CI/CD | Localizar workflows/scripts con `search_content`/`read_file`; analizar impacto del cambio. | Verificar runs y jobs del SHA exacto; configuración no es ejecución. |
| D08 Seguridad | Localizar entrada, validación, sink y llamadas con `get_entry_points`/`trace_path`/`get_symbol_code`. | Una ruta estática no prueba exploit ni dataflow completo; comprobar sanitizadores y contexto, aplicar pruebas seguras. |
| D09 Rendimiento | `get_hot_paths`, `trace_path` y complejidad para elegir dónde medir. | Confirmar con benchmark/perfil/traza en workload representativo. |
| D10 Dependencias/licencias | Leer manifests/lockfiles y localizar uso de APIs externas. | Versión resuelta, SBOM, licencia y advisory aplicable proceden del gestor/artefacto real, no del grafo solo. |
| D11 Documentación | Buscar afirmación y navegación a la implementación/código. | Contrastar vigencia de ADR/README/AGENTS con fuente y pruebas. |
| D12 Observabilidad | Buscar emisores, propagación y consumidores de eventos/logs/métricas; seguir llamadas. | Confirmar con ejecución real cuando se afirme que una señal llega a destino. |

## Límites para interpretar un resultado

- `build_graph` puede omitir archivos o servir caché; anota estado de lectura/parseo, archivos esperados, idioma, estrategia y aristas no resueltas si la salida los informa. Si no se puede comprobar vigencia, evita afirmaciones globales negativas.
- `get_entry_points` = sin aristas entrantes **en el grafo observado**, no «único punto de entrada en producción». `get_leaf_functions` = sin aristas salientes observadas, no código inactivo.
- `get_hot_paths` puede medir fan-in estático: no infieras latencia, frecuencia o p95. `trace_path` devuelve conectividad estática, no tiempo de ejecución.
- `get_complexity` depende de parser/función analizada: confirma que los valores son mediciones de fuente válida y no defaults por error.
- MCP y CLI pueden compartir extractor. Una discrepancia entre ambos se registra; una coincidencia no es evidencia independiente. No es necesario demostrar paridad general para realizar una auditoría.
