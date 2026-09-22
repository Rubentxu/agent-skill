# Descubrimiento de CogniCode: qué existe y qué se puede ejecutar

**Base examinada**: `Rubentxu/CogniCode@5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f` (rama pública `main`, consulta 22-09-2026). No se ejecutó binario real durante esta investigación. El inventario PRF del 21-09-2026 declara una prueba runtime sobre su propio checkout y versión 0.97.3: **20 tools `cognicode-mcp` + 55 tools `explorer-mcp`**. No traslades esa cifra a otra instalación sin comprobar sus `tools/list` y su esquema.

## Inicio reproducible, por consumidor

1. Obtener `git rev-parse HEAD`, `git status --porcelain=v1`, `git diff --name-only BASE...HEAD` y lista de exclusiones; comprobar que CogniCode se inicia con `--cwd` apuntando al workspace correcto. No ejecutar scripts desconocidos del repo.
2. Leer `cognicode-mcp --version`, `explorer-mcp --version` y, cuando exista, `cogh doctor`. Conectar cada servidor como MCP stdio **por separado**, capturar `initialize`, `tools/list` paginado completo y sus `inputSchema`; no enviar logs a stdout. Si solo uno funciona, limitar la auditoría a sus tools. Ver `docs/prf/specs/SPEC-MCP.md`.
3. Comprobar precondiciones por tool: index/graph construido, tipo de grafo, workspace, provider, BD Explorer poblada; consultar schema efectivo antes de construir argumentos. No inventar contratos JSON en la skill.
4. Anotar: `tool_name`, `server`, `version`, `schema_digest`, `scope`, `result`, `errors`, `coverage`, `revision`, `elapsed`; una tool presente pero sin provider o datos no constituye una capacidad operativa.
5. Clasificar `SUPPORTED_AND_VERIFIED`, `ADVERTISED_UNTESTED`, `ABSENT`, `UNAVAILABLE_BACKEND`, `UNSUPPORTED_LANGUAGE`. El resultado `[]` solo es negativo si el productor cubre el conjunto esperado y completó.

## Capacidad comprobada documentalmente en el inventario PRF (no prueba en este entorno)

- **`cognicode-mcp` (20)**: `analyze_impact`, `build_call_subgraph`, `build_graph`, `export_mermaid`, `find_references`, `find_usages`, `get_call_hierarchy`, `get_complexity`, `get_entry_points`, `get_file_symbols`, `get_hot_paths`, `get_leaf_functions`, `get_per_file_graph`, `get_symbol_code`, `go_to_definition`, `hover`, `query_symbol_index`, `read_file`, `search_content`, `trace_path`.
- **`explorer-mcp` (55)**: entre otras, `explorer_open_workspace`, `explorer_query_moldql`, `explorer_spotter_search`, `graph_explain`, `graph_communities`, `graph_pagerank`, `graph_surprising_connections`, `graph_feedback_arc_set`, `impact_radius`, `impact_detect_cycles`, `find_cycles`, `find_dead_code_v2`, `find_quality_issues`, `quality_gate`, `ingest_quality_issues`, `detect_architecture_drift`, `lens_hotspots`, `export_c4_mermaid`.
- **No presuponer disponible en esos 75**: `solid_audit`, `get_imports`, `check_architecture`, `analytics_run`, `taint_flow`, `cfg_per_function` o API pública de `FindingVerifier`. Algunos figuran en un catálogo diferente, en módulos internos o tienen codepaths no incorporados al inventario PRF; solo invocar si el `tools/list` real los anuncia.
- `docs/MCP-TOOLS.md` informa de 75 tools pero contiene nombres que no coinciden exactamente con el inventario runtime. La divergencia de catálogos es un motivo adicional para descubrir por `tools/list` antes de llamar.

## Límites demostrables por lectura del código

- `AnalysisService::build_project_graph` analiza AST de los archivos reconocidos y crea aristas; puede omitir errores y no resolver llamadas ambiguas. Las estrategias pueden diferir. En el código revisado, el cache del `AnalysisService` usa `mtime+size`, no digest completo para todo camino; archivos que cambian con mismo mtime y tamaño pueden servir relaciones obsoletas. Comparar cold/rebuild con una base de contenidos o marcar incertidumbre.
- `build_graph` puede servir un grafo guardado si el manifest considera que no está stale; registra `skipped_files` como `None` si se sirve desde caché (no equivale a cero). No dar por actualizado el grafo simplemente por un `success=true`.
- `get_complexity` depende de Tree-sitter; si falla `parse_tree`, la implementación observada devuelve números por defecto `(1,1,0,0,0)`. Inspeccionar errores de sintaxis, ámbito y símbolo antes de tratar el resultado como una medición fiable.
- `QualityIssue` legacy puede proyectarse a `Finding` con clase C y evidencia vacía: no equivale a finding verificado ni debe bloquear gates.
- `cognicode-axiom`, `cognicode-quality` y `cognicode-rule-test-harness` están **archivados fuera de los members activos** (`docs/parked-crates/`). Sus módulos históricos de connascence/SOLID/duplicación no son herramientas de producción habilitadas por su mera presencia en Git.
- `ControlQueryService` modela evaluación read-only de restricciones de arquitectura, pero su parser de imports usa `use` de Rust. No prometer que evalúe imports de Kotlin, TS o Python, ni que un consumidor MCP exponga ese servicio sin validación.
- La traza de M5 taint observada en el código ofrece semántica estática intraprocedural a nivel de statement en el backend correspondiente; un flujo hipotético no demuestra explotación, ni está garantizado como MCP stable.

## Fuentes de lectura, fijadas por SHA

- Inventario real anterior: https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/docs/prf/evidence/F0-W1-inventory.md
- Contratos de análisis: https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/docs/prf/specs/SPEC-ANALYSIS.md
- Contratos MCP: https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/docs/prf/specs/SPEC-MCP.md
- Catálogo en documentación: https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/docs/MCP-TOOLS.md
- Ingest real: https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/crates/cognicode-core/src/application/services/analysis_service.rs
- Handler MCP: https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/crates/cognicode-core/src/interface/mcp/handlers/mod.rs
- Archivado de Axiom: https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/Cargo.toml
- Protección de hallazgos legacy: https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/crates/cognicode-core/src/domain/findings/quality_projection.rs