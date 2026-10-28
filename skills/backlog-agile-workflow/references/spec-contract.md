# Contrato de conversión de especificaciones a Backlog.md

El paquete intermedio `spec-packet` es **efímero** y no pretende sustituir los documentos de proyecto ni Backlog.md. El agente lo produce tras inspeccionar documentos canónicos, no con un parser de encabezados. No se instala nada ni se escribe un estado persistente de importación.

## Campos de `schemaVersion=1`

- `kind=spec-packet`, `milestones[]`, `tasks[]`, `snapshotScope` (`unfiltered-visible-corpus` solo cuando el agente observó la lectura íntegra).
- Hito: `key`, `title`, `sourceRef`, `state`. `key` mantiene el ID existente, sin inventar numeración.
- Tarea: `key`, `milestone`, `sourceRef`, `title`, `outcome`, `acceptanceCriteria[]`, `definitionOfDone[]`, `dependsOn[]` (keys del paquete, **no** IDs CLI), `documentRefs[]` (ADR/SPEC), `evidenceRefs[]`, `state`, `priorityFactors` (`impact`, `urgency`, `risk`, `effort`) y gate opcional.
- `sourceRef`: exactamente `ruta/relativa.md#ID-estable`, sin traversal. Es identidad *propuesta*, no garantía de resolución por todas las versiones de la CLI.
- Estado documental: `planned|active|implemented|verified|closed|unknown`. No confundir con columnas configuradas del board ni con gate certificado.
- Prioridad: el scoring `3*impact + 2*urgency + risk - effort` propone `P0..P3` para orden de revisión. Las magnitudes se **aportan** por el analista y son ordinales, no medidas ni prioridad CLI. Configuración de prioridades por CLI antes de aplicar.

## Reconciliación

`spec_projection.py` acepta el paquete y opcionalmente salida completa de `backlog task list --json`, con `schemaVersion: 1`, `kind: task-list`, `tasks[]`. Coincidencia exacta de `references[]` con `sourceRef`. Una referencia duplicada o formato desconocido es un error, no una nueva tarea. Cuando falta corpus o hay título parecido no se propone creación inmediata; revisar tareas en otras ramas sigue siendo obligatorio aunque el corpus visible sea completo.

**Importante:** Backlog.md puede presentar referencias y esquemas distintos en versiones futuras. El helper no inventa conversiones ni ejecuta acciones. Si la estructura no coincide, inspeccionar `task view --json` y actualizar esta skill tras validar el contrato upstream.

## Ejemplo sintético

`examples/spec-packet.json` y `examples/spec-existing-tasks.json` no pertenecen a ningún producto real. Ejecutar el proyector devuelve `PRESERVE_ARCHIVED` para R0 ya archivado, `PROPOSE_CREATE` para R1.W1 (después de resolver R0) y espera a obtener el ID real de R1.W1 antes de proponer su dependiente R1.W2. El paquete es de demostración: ningún comando Backlog.md se ejecuta.
