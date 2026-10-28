# Trazabilidad del trabajo sin versionar documentos de gestión

## Identidades y autoridad

- **Backlog.md** es la autoridad para `TASK-42`, dependencias, prioridades, estado, AC y DoD.
- **Roadmap/spec/ADR privados** son autoridad sobre `H2.W1`, `SPEC-023`, `ADR-0012`, gates y restricciones. Reutilizar sus IDs, nunca renumerarlos por conveniencia.
- **Git** es evidencia de **qué código se cambió**; un commit no prueba que la tarea esté Done ni que un release haya sido publicado.
- **Skills de verificación** aportan observaciones `PASS/FAIL/NOT_RUN` con instrumentos reales; no inventar receipts.

Para evitar colisiones, preferir identidades calificadas cuando haga falta: `docs/ROADMAP.md#H2.W1`, `docs/adr/ADR-0012.md#ADR-0012`. Estas rutas son **identificadores lógicos locales privados**, no URLs de GitHub ni promesas de disponibilidad remota. Un archivo ignorado puede seguir sirviendo como referencia local.

## Plantilla de mensaje de commit

```text
refactor(runtime): separar decisión de recuperación del adaptador

Preserva el resultado y el orden de efectos; extrae el decisor puro
y deja IO/retención en el intérprete existente.

Backlog-Task: TASK-42
Roadmap-Block: docs/ROADMAP.md#H2.W1
ADR-Ref: docs/adr/ADR-0012.md#ADR-0012
Spec-Ref: docs/specs/SPEC-023.md#SPEC-023
Implementation: decisor puro y seam de ejecución separados, sin cambiar API
Verification: unit tests del slice PASS; integración NOT_RUN
```

Admitir varias referencias con **trailers repetidos**, no con arrays/cadenas ambiguas. `Backlog-Task` usa el prefijo real del proyecto, nunca `TASK` por defecto. `Implementation` y `Verification` describen hechos observables; no incluir secretos, material privado ni texto de los documentos. Para cambios que aún no implementan, distinguir `Partial` o `NOT_RUN` de completado. El mensaje real debe respetar las reglas de Git/Conventional Commits del proyecto.

## Reconciliación y prevención de duplicados

1. Inspeccionar corpus de Backlog.md, incluidos tasks archivados, drafts, worktrees/ramas según capacidades reales; un `task list --json` no contiene necesariamente todas las referencias de tareas archivadas. Si no hay corpus completo, no crear por ausencia.
2. Resolver `sourceRef` y `documentRefs` de cada objetivo con IDs exactos. Si una tarea existente comparte ID/documento, revisar el detalle; no crear otra por cambio de título o localización.
3. Consultar historial de commits y sus trailers **solo si el operador autoriza la inspección**. Si hay implementación con el ID sin tarea asociada, marcar `REVIEW_IMPLEMENTATION` antes de proponer nueva tarea. No asumir que el código sigue ahí ni que el gate pasó.
4. `commit_trace.py` recibe un JSON de commits (SHAs y mensajes) ya inspeccionados y un `spec-packet` temporal. Produce un índice **solo de revisión**. `spec_projection.py` puede consumirlo opcionalmente; no ejecutan Git ni Backlog.md.
5. Si dos tareas, ADR, bloques o commits reclaman la misma identidad, declarar `IDENTITY_CONFLICT` y pedir reconciliación. No resolver ambigüedad mediante fuzzy matching.
6. Al finalizar una tarea, registrar el commit SHA, las referencias documentales y la evidencia en Backlog.md mediante CLI oficial, preservando notas previas; el mensaje Git sigue siendo rastreable aunque los documentos privados no estén en Git.

## Formato de entrada para el índice

```json
{
  "schemaVersion": 1,
  "kind": "commit-messages",
  "commits": [
    {
      "sha": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "message": "feat: example\\n\\nRoadmap-Block: H2.W1\\nImplementation: behavior change\\nVerification: unit tests PASS"
    }
  ]
}
```

El ejemplo es ficticio. Para producirlo, el agente puede utilizar Git de forma **solo lectura** y curar los resultados en un archivo temporal privado. No almacenar estos JSON en el repositorio, ni introducir un índice persistente adicional a Backlog.md.

## Identificadores Groma como pistas adicionales

Cuando Groma ha observado un componente C4, añadir su ID como `--add-ref` a Backlog.md **solo** si el cambio planificado lo requiere y no queda cubierto por `modifiedFiles`. Los IDs de Groma pueden ser sustituidos por operaciones combine/rename; sus reemplazos no generan alias persistentes. Conservar referencias originales ROADMAP/ADR/SPEC y commit SHA. El trailer adicional `Groma-Component:` es opcional y solo informativo, no prueba de ownership permanente; no sustituye TASK/ADR/SPEC ni evidencia de tests.
