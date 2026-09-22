# Evidencia contrastada y decisión reproducible

## 1. Unidad de auditoría (schema lógico, no API CogniCode existente)

```yaml
basis:
  repo: owner/name
  git_sha: <commit>
  dirty: false
  base_sha: <base-or-null>
  workspace: <workspace-id-or-local-path-redacted>
  source_manifest_digest: <digest-or-unknown>
  graph_revision: <id-or-unknown>
  graph_strategy: full
  language_support: [<languages actually supported>]
  tool_catalog: {server: cognicode-mcp, version: <version>, schema_digest: <sha256>}
  scope: {files_included: <N-or-unknown>, files_expected: <N-or-unknown>, exclusions: []}
  limitations: [<skipped/unresolved/truncated/cache-stale>]
claim:
  id: H-01
  proposition: "una dependencia declarada atraviesa un límite prohibido"
  criterion: <rule/ADR/contract actually adopted>
  alternatives: ["dependency only in test fixture", "type-only import", "port indirection"]
evidence:
  - id: E-01
    producer: cognicode-mcp.build_graph
    origin: graph_candidate
    source_revision: <basis.git_sha>
    subject: <fully-qualified-symbol-or-module>
    relation: <calls/imports/implements/etc>
    object: <target>
    result_state: COMPLETE
    location: <path:line-range>
    raw_output_ref: <secure-artifact-path/digest-or-none>
  - id: E-02
    producer: independent-build-check
    origin: executed_test
    command: <exact permitted command>
    exit_code: 1
    head_sha: <same git sha>
    observed: <actual error or assertion>
adjudication:
  state: CONFIRMADO
  severity: ALTA
  observed_or_potential_impact: observed
  falsification: <minimal controlled test that would refute the claim>
  closure: <test+expected-outcome on new sha>
```

Mantén esta estructura en el **informe de la skill**. No implica que `Finding`, `FactId`, `EvidenceClass`, `graph_revision` o `source_manifest_digest` estén disponibles como API en todos los servidores CogniCode. Las claves desconocidas quedan `unknown`, no se fabrican.

## 2. Tipos de evidencia y corroboración

- `SOURCE`: archivos y bytes del SHA, símbolos, APIs, configuración, líneas (lectura directa).
- `GRAPH`: arista/ausencia de arista y su procedencia+resolución; depende del extractor y de cobertura.
- `EXECUTION`: tests, compilador, ejecución runtime, benchmark o log con comando, entorno, SHA y salida real.
- `HISTORY`: commit/PR/tag/CI previos; informa contexto temporal, no valida automáticamente el SHA actual.
- `DOCUMENTED`: ADR/AGENTS/requisito/política, puede establecer un criterio pero no demostrar comportamiento.
- `HYPOTHESIS`: inferencia de agente/heurística/prompt, pendiente de falsación. Nunca eleva por sí misma un resultado a CONFIRMADO.

**Regla de independencia**: `get_call_hierarchy`, `analyze_impact` y `graph_explain` podrían ser tres perspectivas del mismo grafo: NO son tres fuentes independientes. El parser Tree-sitter consultado en `get_file_symbols` y el grafo generado desde ese mismo parser también pueden compartir errores. Contrasta con AST semántico del compilador, prueba de arquitectura/build, ejecución, fixtures independientes, o una implementación de análisis con distinta procedencia si la afirmación requiere corroboración.

**Regla negativa**: `0 hallazgos` solo significa que ninguna de las comprobaciones completadas reportó un hallazgo dentro del alcance verificado. No decir «no existen vulnerabilidades, deuda o violaciones». Si hay archivos omitidos, idioma no soportado, consulta truncada, caché no invalidada o grafo incompleto, la conclusión global es PARCIAL/UNKNOWN.

## 3. Proceso de contradicción antes de elevar un hallazgo

1. ¿La entidad está identificada de forma inequívoca? Verificar nombre homónimo, namespace, método dinámico y archivo real.
2. ¿La relación responde a la pregunta? Calls ≠ import; import ≠ dependencia transitiva; re-export ≠ ejecución.
3. ¿Comparación en la misma base? SHA, fuente, manifest, configuración, tool/schema y workspace; si difiere algo, no comparar como delta causal.
4. ¿Es requisito o preferencia? ADR vigente, contrato público, error reproducido, impacto plausible y justificado.
5. ¿Existe evidencia en contra? Inspeccionar guardas, sanidad, tests y excepciones; registrar desacuerdos de herramientas sin elegir el resultado favorable.
6. ¿Se ejecutó el test? `NOT_RUN` explícito hasta capturar output auténtico. No inferir PASS de una certificación antigua.
7. ¿Puede otro agente reproducir la afirmación? Guardar comando, entrada, salida, filtros, línea, SHA, falsificación y prueba de cierre.

## 4. Estados: no mezclar planos

| Plano | Valores | Significado |
|---|---|---|
| Estado del análisis | `CONFIRMADO`, `PARCIAL`, `HIPÓTESIS`, `DESCONOCIDO`, `NO_SOPORTADO`, `NO_EJECUTADO`, `NO_APLICA` | Grado y límite de comprobación; nunca equivalentes a severity. |
| Severidad del hallazgo | `BLOQUEANTE`, `ALTA`, `MEDIA`, `BAJA`, `INFORMATIVA` | Impacto técnico ligado al contexto y al criterio aplicado. No deriva automáticamente del PageRank ni de la clase A–D. |
| Gate de pruebas | `PASS`, `FAIL`, `NOT_RUN`, `BLOCKED`, `SKIP_NOT_APPLICABLE` | Salida observable y trazable de tests/CI/UAT, no interpretación de la presencia de un archivo. |
| Clase interna de evidencia CogniCode | `A`, `B`, `C`, `D` **solo si runtime y verificador lo devuelven** | Semántica propia de CogniCode; no autoasignar desde el informe humano. |

## 5. Política de falsos positivos y gasto

Para cada candidato, calcula el coste de verificación: inspección de 2 símbolos (barata), test focal (moderado), tests integrales o benchmark (costoso). Prioriza por riesgo del cambio y probabilidad de relación real, no únicamente por número de alertas. Conserva candidatos rechazados con motivo breve y deduplica por `(rule, symbol_identity, source_basis, causal_mechanism)`; evitar contar el mismo problema detectado por varios análisis como incidencias distintas.

No ejecutar herramientas de escritura ni ingerir código privado en cloud por defecto. Si se usan `find_quality_issues`/`quality_gate`, indicar explícitamente quién produjo esas issues, cuándo se ingestaron, para qué workspace y si hay evidencias actuales de respaldo; `ingest_quality_issues` requiere permiso explícito.