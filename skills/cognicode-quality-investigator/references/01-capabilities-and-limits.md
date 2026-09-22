# Capacidades disponibles: CogniCode core (sin Explorer)

**Baseline documental:** `Rubentxu/CogniCode@5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f` (22-09-2026). El inventario PRF ejecutó `cognicode-mcp` 0.97.3 en su entorno, observando `initialize`, `tools/list` (20) y `tools/call read_file`. Esto **acredita esas operaciones en aquel entorno**, no la UAT de nuestra skill ni el estado de otro binario instalado.

## Procedimiento por consumidor

1. `git rev-parse HEAD`; `git status --porcelain=v1`; identificar exclusiones, permisos y configuración.
2. Comprobar `cognicode-mcp --version` y `cognicode --version`; obtener `cognicode --help`, `graph --help`, `index --help`, `navigate --help` cuando existan. Conectar MCP por stdio `--cwd` a workspace correcto, capturar `initialize`, `tools/list` completo (con paginación si se anuncia) y `inputSchema`. No construir tool calls con argumentos supuestos.
3. Invocar operaciones read-only con un corpus independiente, capturar `exit code`/resultado, servidor, versión, workspace, scope, cobertura, límites, errores y digest de entrada. Si la herramienta anunciada falla por backend, idioma o configuración, es `UNAVAILABLE`/ `PARTIAL`, no verificada.
4. La alternativa CLI se consulta en `references/05-cli-mcp-parity-and-certification.md`; el mismo nombre o un `--help` válido no prueban semántica compartida.

## Inventario PRF de `cognicode-mcp` (20 herramientas observadas en v0.97.3)

`analyze_impact`, `build_call_subgraph`, `build_graph`, `export_mermaid`, `find_references`, `find_usages`, `get_call_hierarchy`, `get_complexity`, `get_entry_points`, `get_file_symbols`, `get_hot_paths`, `get_leaf_functions`, `get_per_file_graph`, `get_symbol_code`, `go_to_definition`, `hover`, `query_symbol_index`, `read_file`, `search_content`, `trace_path`.

**Alcance:** únicamente estas herramientas *si figuran en el servidor real*. En la implementación del CLI hay familias `index`, `graph` y `navigate` junto a `analyze`, pero no todos sus argumentos, semánticas, estados ni formatos coinciden con MCP. Ver `references/05-cli-mcp-parity-and-certification.md`.

**No incluidos en el gate de esta skill:** `explorer-mcp` (aunque el recibo PRF enumere 55 herramientas adicionales), `explorer-api`, `explorer_query_moldql`, `graph_communities`, `quality_gate`, `find_dead_code_v2`, `detect_architecture_drift`, `analytics_run` y cualquier consulta que dependa de Explorer/Ladybug. No instalarlos ni invocarlos para completar una auditoría. Tampoco asumir `solid_audit`, `check_architecture`, `get_imports`, `taint_flow` o `cfg_per_function` solo porque aparecen en otras fuentes o código interno.

## Límites de evidencia del core

- `build_graph` puede devolver un grafo servido desde caché; `skipped_files=null` significa que no se hizo un nuevo walk, NO que todo se procesó. El código inspeccionado incluye caminos de caché con `mtime+size`; si se conservan ambos valores tras cambiar bytes, el análisis puede quedar obsoleto. Usar hash de contenido o una reconstrucción autorizada para conclusiones negativas.
- Un AST puede omitir archivos por error o resolver incorrectamente homónimos/llamadas dinámicas. `trace_path` es conectividad estática y no ejecución. `get_entry_points` y `get_leaf_functions` reflejan únicamente aristas observadas.
- `get_complexity` puede retornar valores por defecto si falla el parser; antes de concluir, comprobar sintaxis, límites de función y errores. `get_hot_paths` mide fan-in estático, no rendimiento.
- Los crates históricos `cognicode-axiom`/`cognicode-quality` están aparcados; no contar sus analizadores como producto en ejecución. Los tipos internos `Finding`/`Evidence` no constituyen por sí solos API MCP pública.

## Fuentes fijadas a la revisión investigada

- [Recibo de binarios y tools PRF](https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/docs/prf/evidence/F0-W1-inventory.md).
- [Contrato MCP](https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/docs/prf/specs/SPEC-MCP.md) y [contrato CLI](https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/docs/prf/specs/SPEC-CLI.md).
- [CLI command enum](https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/crates/cognicode-core/src/interface/cli/commands.rs).
- [AnalysisService](https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/crates/cognicode-core/src/application/services/analysis_service.rs) y [handler MCP](https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/crates/cognicode-core/src/interface/mcp/handlers/mod.rs).
