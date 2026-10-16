# Navegación HATEOAS-like (no HTTP)

El helper devuelve `recommended` y `_links[]` con rutas a playbooks **locales**. Nunca ejecuta un comando, modifica estado, certifica ni instala herramientas.

## Esquema observado

~~~json
{
  "intent": "release",
  "product": "application",
  "inventory": "ready",
  "git_artifacts": "clean",
  "archive_confusion": false,
  "asset_set": "complete",
  "package": "passed",
  "consumer": "passed",
  "integrity": "passed",
  "publication": "not_run",
  "basis": "current",
  "risk": "routine",
  "signals": ["release"],
  "available_skills": []
}
~~~

- `intent`: `catalog|audit|prepare|release|cleanup`.
- `product`: `unknown|application|cli|library|sdk|container|plugin`.
- `inventory`: `unknown|ready`. `basis`: `unknown|current|stale`.
- `git_artifacts`: `unknown|clean|bloated`. `archive_confusion`: boolean.
- `asset_set`: `unknown|incomplete|complete|unexpected`.
- `package,consumer,integrity,publication`: `not_run|passed|failed|blocked`. Omitir no equivale a `passed`.
- `risk`: `routine|high|critical`. `signals`: `release|git|archive|package|consumer|integrity|evidence|history|unknown`.
- `available_skills`: nombres observados realmente instalados, no sugerencias fingidas.
- `lens_gap`: boolean; nuevas lentes siempre requieren evaluación antes de activarse.

## Precedencia de acciones

1. `catalog`: solo listar lentes; no probar/publicar.
2. `inventory=unknown` o `product=unknown`: `inspect-product`.
3. `basis=stale|unknown`: `refresh-basis`, nunca confiar en resultados antiguos.
4. `git_artifacts=bloated`: `plan-git-hygiene`; **no borrar automáticamente**.
5. `archive_confusion=true`: `clarify-source-archives` (seguir trabajando después).
6. `asset_set=unexpected|incomplete`: `fix-asset-set` (incluso con checksums verdes).
7. `asset_set=unknown`: `inventory-assets`.
8. Fallos `package|consumer|integrity|publication=failed`: `investigate-failure`.
9. `package!=passed`: `inspect-package` (sólo un asset real).
10. `consumer!=passed`: `verify-consumer` (real, limpio).
11. `integrity!=passed`: `verify-integrity` (digest/provenance).
12. `publication!=passed`: `publish-or-check-release` (si hay autorización).
13. Todo `passed` y asset set completo: `finish-release`. **Un router PASS no certifica nada**.

El estado de `cleanup` nunca autoriza `git filter-repo` ni `git push --force`; remite a análisis de riesgo y aprobación humana. `audit` informa hallazgos sin tocar archivos.

Lentes: se calculan a partir de señales reales e intención, nunca a partir de nombres inferidos del proyecto. Se publican `ready` y `planned`, pero solo las primeras generan acciones. Se permite una recomendación de lente futura (`lens_gap`) sin activarla.
