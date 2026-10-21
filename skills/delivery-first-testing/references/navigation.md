# Navegación de acciones HATEOAS-like (sin HTTP)

El agente observa estado del proyecto y construye **enlaces a procedimientos**, no endpoints ejecutables. Cada `_links[]` tiene `rel` (verbo/decisión), `href` (playbook existente) y `why`. El recomendador no cambia archivos ni ejecuta procesos.

## Forma de entrada

```json
{
  "intent": "feature",
  "inventory": "ready",
  "impact": "known",
  "basis": "current",
  "changed": ["ui", "domain"],
  "risk": "routine",
  "affected": "passed",
  "uat": "passed",
  "regression": "pending"
}
```

Tipos:
- `intent`: `catalog|feature|merge|integration|release|audit`.
- `inventory`: `unknown|ready`; `impact`: `unknown|known|none`.
- `basis`: `unknown|current|stale`; `risk`: `routine|high|critical`.
- `changed`: tipos observados `ui|domain|api|security|persistence|protocol|ci|release|docs|harness|unknown`, sin inventar coincidencias.
- `affected`, `merge_checks`, `integration_checks`, `release_checks`: `not_run|passed|failed|blocked`.
- `uat`: `pending|passed|failed|not_needed`; `regression`: `pending|decided`.
- `artifact`: `unknown|ready|missing` para release; `evidence_commit`: SHA o identificador si existe, opcional.
- `uat_reason` requerido para `not_needed`; `regression_reason` requerido para `decided`. Los campos omitidos no equivalen a PASS.

## Señales complementarias de diseño

La recomendación de **lentes** filtra ahora por señales reales. Una lente sin señales es transversal, pero no se activan data-driven, mutation o UAT GUI por coincidencia de intención cuando el cambio no las justifica. Data-driven orienta diseño de casos; mutation-guidance guía una comprobación bajo demanda o en auditoría, **no** añade un gate global al router. La selección real y el criterio de cierre de pruebas permanecen bajo el ejecutor del proyecto.

## Prioridad y acciones

1. **catalog**: descubrir lentes; sin comandos de construcción.
2. **inventory unknown**: `inspect-project` antes de decidir tests.
3. **basis stale|unknown**: `refresh-basis` antes de acreditar un resultado.
4. **impact unknown** (feature/merge): `resolve-impact`, sin asumir que no existe impacto.
5. **fallo observado**: `classify-failure` antes de repetir/verdes.
6. **feature**: `run-affected` si falta; `explore-uat` si procede; `decide-regression`; `finish-feature`. Para ausencia de UAT, exigir motivo; no omitir UAT que cubre riesgo crítico.
7. **merge**: `run-merge` y `finish-merge` únicamente tras PASS observado.
8. **integration**: `run-integration` y `finish-integration` únicamente tras PASS observado.
9. **release**: `inspect-artifact` hasta identidad lista; `run-release` y `finish-release` tras PASS observado sobre el artefacto real.
10. **audit**: `audit-portfolio` a partir de inventario; entregar recomendaciones sin borrar nada.

Las lentes recomendadas se infieren de `changed`, `risk`, `intent` y estado observable; deben tener `status=ready`. `planned` informa posibilidad futura, nunca procedimiento habilitado.

## Transiciones de evidencia

- `NOT_RUN`: no existe una ejecución del alcance solicitado.
- `PASSED`: salida, artefacto, revisión y cobertura observados para ese alcance (el helper solo recibe ese estado, no lo certifica).
- `FAILED`: fallo causal observado; no se puede sustituir por una nueva ejecución que no cubre el mismo contrato.
- `BLOCKED`: falta herramienta, permisos, identidad o artefacto; registrar carencia.
- `STALE`: cambia código/artefacto/contexto: recalcular antes de reutilizar.

**Importante:** un resultado de script de affordances nunca es una certificación. Para tests de credenciales/seguridad, si un resultado `passed` es incompatibile con la evidencia real, reportar falso verde y no continuar.

## Descubrimiento de skills y propuestas de lentes

`available_skills`: nombres reales observados por el agente/cliente, nunca inferidos por presencia de una URL. `related_skills` ofrece posibles delegaciones sin instalarlas. `lens_gap=true` permite proponer una lente, pero exige validar contraejemplos antes de activarla. Ver [skill-discovery](related-skills.md).
