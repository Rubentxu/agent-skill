# Doce dimensiones — extracción core MCP y alternativa CLI contrastada

**No depender de Explorer.** Los nombres CLI de la tabla son familias observadas en el código y deben confirmarse con `--help` y una ejecución en la versión instalada; NO se declara paridad con MCP por adelantado. Si una dimensión carece de herramienta core, usar inspección de fuente y un analizador externo autorizado y registrarlo como tal; jamás invocar una tool exclusiva de Explorer ni informar una dimensión como completa por disponer de un grafo.

| Dimensión | CogniCode core MCP | CLI (candidato, comprobar ayuda y ejecución) | Contraste y evidencia mínima |
|---|---|---|---|
| D01 Arquitectura y límites | `get_file_symbols`, `find_usages`, `go_to_definition`, `get_call_hierarchy`, `trace_path` | `index outline`, `graph hierarchy`, `graph trace-path` cuando figuren | Regla vigente + grafo de imports y dependencias reales de build + origen/destino; un ciclo de llamadas no equivale a inversión de dependencia. |
| D02 SOLID y tipado funcional | `get_symbol_code`, `get_file_symbols`, `find_references`, `get_complexity` | `index symbol-code`, `graph complexity`, `navigate references` | Contrato y consumidor reales, invariantes, tests de sustitución y compilador; tamaños y flags no prueban por sí mismos SRP/LSP. |
| D03 Connascence estática | `find_usages`, `find_references`, `get_symbol_code`, `go_to_definition` | `navigate references`, `index symbol-code` | Par de componentes cuyo cambio está vinculado por un contrato; prueba de ruptura/cambio conjunto; NO generar un índice SCIJ sin método validado. |
| D04 Duplicación, acoplamiento, cohesión y complejidad | `get_complexity`, `get_call_hierarchy`, `get_file_symbols`, `get_symbol_code` | `graph complexity`, `graph hierarchy` | Fragmentos y semántica, complejidad con parser válido, historiales de co-cambio contrastados; para duplicación usar comparador independiente si procede. |
| D05 Deuda técnica | `analyze_impact`, `find_usages`, `search_content` | `graph impact` | ADR, issues, diff Git y SHA actual; clasificar deuda previa frente a regresión nueva. |
| D06 Tests y cobertura | `analyze_impact`, `get_entry_points`, `trace_path` para **proponer** selección | `graph impact`, `graph entry-points` | Ejecutar los tests autorizados y registrar resultado, cobertura real/denominador, assertions y SHA. Grafo ≠ cobertura de tests. |
| D07 CI/CD | `read_file`, `search_content`, `analyze_impact` | `graph impact`, lectura de archivos local | Workflow y jobs **ejecutados** contra el SHA nuevo, exit codes, cancelaciones y matrices; YAML presente ≠ CI verde. |
| D08 Seguridad | `get_entry_points`, `find_usages`, `trace_path`, `get_symbol_code` | `graph trace-path`, `navigate references` | Fuente→validación/sanitización→sumidero y pruebas seguras/SAST externos; ruta estática ≠ explotación o flujo taint completo. |
| D09 Rendimiento | `get_hot_paths`, `get_complexity`, `trace_path` | `graph hot-paths`, `graph complexity` | Perfil/bench y workload reales; fan-in de llamadas no mide latencia. |
| D10 Dependencias/licencias | `read_file`, `search_content`, `find_usages` | Lectura local de manifests y lockfiles; no asumir comando de SBOM en CLI | Versiones concretas, licencias, advisory aplicable, SBOM/gestor, rutas realmente utilizadas. |
| D11 Documentación y mantenibilidad | `search_content`, `read_file`, `get_symbol_code` | Lectura de fuentes + `index symbol-code` | Especificación y ADR vigente frente al código/test del SHA; no confundir histórico con contrato vigente. |
| D12 Observabilidad | `get_entry_points`, `find_usages`, `search_content`, `trace_path` | `graph trace-path`, lectura local | Emisor→propagación→exportador/consumidor y prueba de ejecución si se afirma señal operativa; import OTel ≠ traza disponible. |

## Composiciones sin Explorer

- Arquitectura: `get_file_symbols` → `find_usages`/ `go_to_definition` → verificación del build/imports → test arquitectónico; con CLI utilizar los comandos semánticamente equivalentes solo tras compararlos sobre el mismo corpus.
- Impacto: diff de SHA → `analyze_impact` o `graph impact` → consumidores y contracts → tests focales → gates de integración/release exigidos.
- Seguridad: localización de fuente y sink → `trace_path` estático acotado → sanitizadores reales → prueba segura o SAST; no inventar `taint_flow` MCP.
- Deuda: corpus y tool/version iguales en dos revisiones → clasificar nuevos, resueltos y pendientes sin mezclar errores de ingest con cero incidencias.

## Selección de pruebas

Durante desarrollo, usar grafo como indicador de qué tests ejecutar, incluyendo rutas dinámicas y consumidores externos; para merge/release aplicar gates completos según el repositorio. La existencia de `cognicode` CLI no sustituye los tests del proyecto ni constituye una validación independiente del extractor MCP cuando ambos comparten core.
