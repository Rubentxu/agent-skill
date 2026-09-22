# Evolución CogniCode: sacar partido del motor sin inventar APIs

## Foto técnica observada en el código público (22-09-2026)

**Alcance vigente de esta skill:** `cognicode-mcp` y `cognicode` CLI. El inventario PRF verificó 20 tools MCP core en v0.97.3 y comprobó las familias CLI existentes; la paridad semántica entre interfaces sigue pendiente de prueba por operación. `explorer-mcp` y `explorer-api` no forman parte de su gate: requieren adaptación independiente y no se utilizan como fallback.

**Piezas del core que sería valioso conectar tras confirmar disponibilidad y certificación**:

- `domain/evidence_kernel/{fact,evidence,snapshot}`: hechos ligados a snapshot y con productor de procedencia; la salida del LLM no puede crear un `Fact` extraído (restricción de tipo).
- `domain/findings/{finding,verifier,quality_projection}`: `Finding` contiene detector ejecutado, cadena causal y evidencia; `FindingVerifier` distingue evidencias resolubles y autoridad para gate. La proyección legacy `QualityIssue` tiene evidencia vacía y no puede bloquear por sí sola.
- `application/findings/{grounded_finding_flow,m5_dataflow_backend}`: vertical de grounding de Rust y backend de taint estático con límite explícito de precisión; **no** suponer soporte genérico multilenguaje ni exportación MCP actual.
- `application/architecture/control_query`: consulta read-only de restricciones admitidas con estado `Evaluated/Incomplete`; parser de imports Rust `use`. No asumir evaluación hexagonal multi-lenguaje general.
- `application/evidence_bundle/producer`: traduce fallos de productores a `Failed/Missing/Unknown` y no los convierte en PASS; el productor estático de pruebas no demuestra por sí mismo integración real con todos los runners.
- `application/shadow_evaluation/compare`: emparejamiento por case-id y deltas descriptivos sin reinterpretar incompletos como cero; útil para comparar nuevos detectores, no implica un endpoint estable.
- `application/services/analytics_oracle_harness`: su código dice expresamente que es un **stub** que compara JSON ya pasado, no que consulta Neo4j realmente. No recomendar añadir Neo4j como requisito del auditor.
- `docs/parked-crates/cognicode-axiom`: código histórico de reglas (incluye `connascence` y `solid`) **fuera del workspace Cargo activo**. Usarlo como referencia de diseño, no llamarlo funcionalidad de producción.

Fuentes:

- https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/crates/cognicode-core/src/domain/evidence_kernel/fact.rs
- https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/crates/cognicode-core/src/domain/findings/finding.rs
- https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/crates/cognicode-core/src/domain/findings/verifier.rs
- https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/crates/cognicode-core/src/domain/findings/quality_projection.rs
- https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/crates/cognicode-core/src/application/findings/grounded_finding_flow.rs
- https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/crates/cognicode-core/src/application/findings/m5_dataflow_backend.rs
- https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/crates/cognicode-core/src/application/evidence_bundle/producer.rs
- https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/crates/cognicode-core/src/application/shadow_evaluation/compare.rs
- https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/crates/cognicode-core/src/application/services/analytics_oracle_harness.rs

## Diseño incremental y puertas de salida

### S0 — Skill independiente, sin cambios en CogniCode (primera entrega)

MCP core read-only + CLI `cognicode` cuando se demuestre la operación, Git+fuente+tests/CI ya existentes. Cada operación documenta su estado y la paridad pendiente. Herramientas exclusivas de Explorer no se simulan ni bloquean S0. Demostración: un corpus sintético con 1 ciclo intencional de *calls*, 1 import prohibido verificado por build, 1 export externo sin llamadas locales, 1 fallo de parser, 1 fichero modificado manteniendo mtime/tamaño, y un test de CI de un SHA antiguo. Esperado: el auditor distingue cada caso y no falsea PASS.

### S1 — Productores externos reproducibles, sin acoplarlos al core

Crear adaptadores **fuera de CogniCode** que consuman artefactos reales: JUnit, cobertura, SARIF, SBOM, resultados de build, CI, métricas runtime. Entregan la estructura lógica del ledger; se ejecutan únicamente con permisos y versiones fijadas. No escribir `QualityStore` automáticamente ni convertir SARIF a fact canónico sin validación. UAT: un productor ausente devuelve `NO_EJECUTADO/UNKNOWN`, no `PASS`; dos extractores correlacionados no cuentan como fuentes independientes.

### S2 — Capacidad de exportación de hechos/evidencias desde CogniCode (evolutivo separado)

**Condición de apertura**: PRF C7 verificado en binarios publicados y un consumidor real que necesite más que S0/S1. Proponer un port de aplicación read-only `AnalysisEvidenceQuery` (nombre tentativo, NO API existente) con un DTO versionado y sin exponer el almacén canónico directamente:

```text
AnalysisBasis(workspace, git_sha?, dirty?, manifest/config_digest,
              graph_revision, engine_version, tool_schema,
              requested_scope, observed_scope, skipped/unresolved,
              status: Complete|Partial|Unknown|Unsupported|Failed)
    └─ EvidenceEnvelope(fact_ref?, source_anchor, provenance, producer,
                        extraction_status, typed_relation, confidence?)
        └─ FindingProjection(finding_ref?, origin, detector_execution,
                             causal_chain, verifier_status, explanation)
```

Desarrollar primero como composición read-only in-process de `FactStore`, `EvidenceStore` y `FindingVerifier` vigentes; después exponer un **único** adaptador MCP o CLI siguiendo `SPEC-MCP` y tests cliente antiguo/nuevo. Reutilizar puertos y persistencia del core, sin segundo grafo, sin crear un `QualityIssue` incompatible ni prometer que `evidence_class=A` equivale a explotación. La extensión deberá ser aprobada en el roadmap del producto, no como requisito para instalar esta skill.

UAT contractual: entradas idénticas generan mismas identidades y relaciones; cada finding expone ids/paths resolubles; `Partial`/`Unknown` no retornan clean; un LLM no crea hechos extraídos; un quality issue legacy sin evidencia no es bloqueante; export respetará permisos/limitaciones.

### S3 — Deltas, observación dinámica y pruebas causales

El mismo ledger admite comparación por base/identidad de símbolo y replay con corpus independiente. Incorporar Chronos u otras fuentes runtime **solo si** proporcionan correspondencia verificable `(execution_id, build_sha, source_map, symbol_id, time, environment)`; observación runtime de una llamada puede corroborar una arista estática, pero la ausencia de evento no demuestra ausencia de ejecución si hay muestreo/huecos. Los spans permiten reportar latencia o errores *observados* solo con workload y trazabilidad. Proteger capturas sensibles y rechazar comparaciones entre versiones/muestras incompatibles.

## Impacto sobre PRF

El README vigente de PRF restringe su programa a estabilizar CLI/MCP; la evolución `POST-PRF-EVOLUTION.md` condiciona nuevas piezas LSI a consumidores, UAT y certificación posterior. Mantener **S0/S1 en `Rubentxu/agent-skill`**, sin tocar `Rubentxu/CogniCode`; proponer S2/S3 como cambios separados, no como requisito de esta skill.

- https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/docs/prf/README.md
- https://github.com/Rubentxu/CogniCode/blob/5b96db4343d82c02e6a1c2bf855fe13c0e13ec9f/docs/prf/POST-PRF-EVOLUTION.md
## Adaptación de Explorer, fuera de alcance

Un evolutivo futuro podría exponer comunidades, MoldQL y findings mediante un port read-only con semántica, basis, permisos y tests old-client/new-client. Abrirlo solo con consumidor real y UAT propia; jamás exigir Explorer para certificar `cognicode-mcp` o la alternativa CLI de esta skill. Mantener identidades de fuente y separar aristas de llamadas, imports y datos runtime.
