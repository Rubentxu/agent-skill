# Core MCP y CLI: paridad y certificación por operación

## Qué está probado y qué no

El recibo PRF de `CogniCode@5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f` registra en su entorno `cognicode-mcp` 0.97.3 (initialize, tools/list 20, tools/call read_file) y `cognicode` 0.97.3 (version/help/doctor). La enumeración `CliCommand` contiene `Analyze`, `Index`, `Graph`, `Navigate`, y subcomandos de grafos para entrada, leaf, trace, mermaid, hierarchy, complexity e impact. La coincidencia de nombres **no demuestra** que hagan idénticas consultas ni produzcan iguales resultados: algunos caminos de `AnalysisService` y `FullGraphStrategy` han diferido históricamente. Ver [inventario PRF](https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/docs/prf/evidence/F0-W1-inventory.md), [CLI](https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/crates/cognicode-core/src/interface/cli/commands.rs), [contrato CLI PRF-CLI-04](https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/docs/prf/specs/SPEC-CLI.md).

## Matriz de cobertura (hipótesis a verificar sobre el binario instalado)

| Operación core MCP | Candidato CLI | Criterio para afirmar equivalencia |
|---|---|---|
| `build_graph` | `cognicode graph full [ruta]` | Mismos archivos/bytes, configuración, símbolos y aristas FQN, cobertura y fallos informados; no comparar simplemente totales. |
| `get_per_file_graph` | `cognicode graph per-file [archivo]` si `--help` lo admite | Mismo archivo, resolución de aristas y explícita distinción intrafichero/transfichero. |
| `get_call_hierarchy` | `cognicode graph hierarchy` si existe | Identidad FQN y profundidad/dirección comparables; homónimos no se fusionan. |
| `get_hot_paths` | `cognicode graph hot-paths` | Fan-in del mismo grafo y filtros equivalentes, no métricas de latencia. |
| `trace_path` | `cognicode graph trace-path` | Misma ruta entre IDs no ambiguos, mismos límites, ausencia informada honestamente. |
| `get_complexity` | `cognicode graph complexity` | Misma función, parser y definición métrica; no aceptar defaults en errores. |
| `analyze_impact` | `cognicode graph impact` | Misma identidad de símbolo, depth y conjunto de dependencias/consumidores. |
| `query_symbol_index` | `cognicode index query` | Mismos símbolos, rutas/FQN, distinción de homónimos y exclusiones. |
| `get_symbol_code` | `cognicode index symbol-code` | Misma localización y cuerpo/linaje de fuente; normalizar solo formato, no información. |
| `go_to_definition`, `hover`, `find_references` | `cognicode navigate definition/hover/references` | Mismo file:line:column, mismo LSP disponible, mismo resultado y límites. |
| `get_file_symbols`, `find_usages`, `search_content`, `read_file`, `build_call_subgraph`, `export_mermaid`, `get_entry_points`, `get_leaf_functions` | Consultar `--help`; no asumir subcomando uno-a-uno | Declarar `CLI_UNMAPPED` si no se observa CLI equivalente o cambia el contrato; usar MCP + fuente independiente. |

## Gate mínimo para cada interfaz

**MCP_VERIFIED** requiere: binario+versión, workspace y SHA, handshake `initialize`, `tools/list` con schema real, invocación read-only contra un caso positivo y otro negativo que produzca errores tipados o vacío legítimo, salida y base de análisis registradas. Una tool anunciada sin `tools/call` es `ONLY_ADVERTISED`.

**CLI_VERIFIED** requiere: `cognicode --version`, `--help` del comando, argv real y entorno, stdout/stderr, exit code, caso positivo y negativo; un exit 0 con resultado silenciosamente incompleto **no** acredita éxito.

**PARITY_VERIFIED** requiere ambas interfaces verificadas para **la misma operación**, bytes y base iguales, normalización documentada de formatos, comparación de conjuntos de símbolos/aristas y estados, errores/limits compatibles, corpus de nombres duplicados y errores de parseo. Si faltan fields en uno, clasificar `PARITY_NOT_VERIFIED` con diferencia concreta y usar la interfaz que sí esté verificada, SIN presentarlas como equivalentes.

**SKILL_UAT_PASS** requiere ejecutar la skill mediante un agente en una fixture independiente de arquitectura/CI/caché/ambigüedad, registrar informe y comprobar que no fabrica hallazgos, severidades, pruebas ni herramientas. El CI que solo valida frontmatter, enlaces y scripts es `SKILL_STRUCTURE_PASS`, no UAT de CogniCode.

## Protocolo reproducible sin ejecutar código no confiable por defecto

1. Instalar/activar únicamente binarios de CogniCode autorizados y comprobar versión. No ejecutar scripts de terceros.
2. Crear corpus pequeño independiente en workspace aislado con 2 módulos, 1 llamada cross-file, 2 homónimos, 1 sintaxis inválida y 1 import intencionadamente prohibido por una regla del corpus. Registrar SHA o digest de archivos; incluir corpus negativo sin violación.
3. Registrar los `--help` del CLI y `tools/list` de MCP; sus parámetros reales gobiernan las invocaciones (no copiar un JSON-RPC ilustrativo de otra versión).
4. Ejecución fría y caliente con la misma base; comparar nombres fully-qualified, aristas tipadas, alcance, errores y salidas parciales. Ante cambio de contenido con mtime/tamaño preservados, exigir detección real o marcar stale.
5. Registrar un recibo **por operación**: `{version,sha,scope,tool+schema_or_cli_argv,inputs_digest,stdout/stderr_or_mcp_result,exit_or_error,normalized_diff,positive_case,negative_case,verdict}`.
6. No ejecutar Explorer para esta UAT ni usar su ausencia para bloquear la certificación core.

La comparación CLI/MCP no es corroboración independiente de un hallazgo si ambos comparten `AnalysisService`; contrastar con el código/build/test/CI o un segundo analizador de procedencia distinta cuando haga falta.
