# Verification y cierre — comprobar antes de marcar

1. Consultar `backlog instructions task-finalization` y `backlog task view <id> --json`; inspeccionar `acceptanceCriteria`/`definitionOfDone` y comprobar los índices reales de cada ítem.
2. Verificar AC por comportamiento y artefacto observado. Un test no ejecutado es `NOT_RUN`, no `PASS`; usar `delivery-first-testing` sólo cuando esté confirmado disponible.
3. Marcar individualmente con `backlog task edit <id> --check-ac <índice>` y `--check-dod <índice>` **únicamente** si son reales y hay autorización de actualización.
4. Escribir `backlog task edit <id> --final-summary "..."` con cambios, evidencia y límites; si existe un resumen anterior, distinguir reemplazo de `--append-final-summary`.
5. Cambiar al estado final configurado (`backlog task edit <id> -s "<estado-final>"`) **solo después** de validar DoD/AC, respetando callback `onStatusChange` y efectos Git.
6. No archivar al cerrar automáticamente. Archivar exige operación de mantenimiento independiente; nunca borrar por inercia.

**Anti-patrón:** marcar todas las casillas cuando «parece terminado». **Resultado:** cierre sustentado o `BLOCKED` con lo pendiente.
