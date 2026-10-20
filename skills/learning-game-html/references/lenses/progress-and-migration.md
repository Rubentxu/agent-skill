# Lente: persistencia y migración

Persistir localmente por **ID estable de contenido**, no por posición de array. JSON versionado `{schemaVersion,contentVersion,itemStates,missions,preferences}`; `itemStates` distingue `attempts`, `missed`, `marked`, `recovery`, `mastery`, `due` (solo memoria), ayudas y último evento relevante.

Reglas:

1. `load`: validar esquema, permitir modo temporal si storage denegado y no sobreescribir datos corruptos de inmediato.
2. `migrate`: versiones conocidas, idempotencia, campos por defecto conservadores. Copia de seguridad antes de migraciones de riesgo.
3. `save`: idempotente por evento, fallo informativo, sin pérdida silenciosa. Usar `localStorage` para casos pequeños; IndexedDB solo cuando tamaño/consulta lo justifique.
4. `resetSession`: efímero; `resetProgress`: confirmación explícita; `import`: validar origen y tamaño, resolver colisiones conscientemente.
5. Exportar/importar progreso con fecha/versión. Informar límites si el usuario cambia navegador o esquema `file://`.

**UAT:** crear progreso → reabrir → validar → modo libre → reiniciar → no pierde mastery; importar backup antiguo. La compatibilidad observada sobre un solo navegador no certifica todos los entornos.
