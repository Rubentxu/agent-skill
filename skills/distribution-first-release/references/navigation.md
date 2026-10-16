# Navegación HATEOAS-like (no HTTP)

El helper devuelve `recommended` y `_links[]` con rutas a playbooks **locales**. Nunca ejecuta un comando, modifica estado, certifica ni instala herramientas.

## Esquema observado

~~~json
{
  "intent": "release",
  "product": "portfolio",
  "inventory": "ready",
  "product_set": "complete",
  "route_set": "complete",
  "git_artifacts": "clean",
  "archive_confusion": false,
  "asset_set": "complete",
  "package": "passed",
  "consumer": "passed",
  "integrity": "passed",
  "publication": "not_run",
  "basis": "current",
  "risk": "routine",
  "signals": ["release", "discovery", "registry", "publish"],
  "available_skills": ["pipelinek-local-ci"]
}
~~~

- `intent`: `catalog|audit|prepare|release|cleanup`.
- `product`: `unknown|application|cli|library|sdk|container|plugin|portfolio`. `portfolio` significa varios productos y NO autoriza saltarse el inventario.
- `inventory`: `unknown|ready` de evidencia de repositorio; `basis`: `unknown|current|stale`.
- `product_set`: `unknown|incomplete|complete`: lista **exhaustiva** por módulo, consumidor y producto; `route_set`: igual, para canales obligatorios. `complete` es una afirmación a auditar, no la prueba de una publicación.
- `git_artifacts`: `unknown|clean|bloated`; `archive_confusion`: boolean.
- `asset_set`: `unknown|incomplete|complete|unexpected`, agregado de productos/canales obligatorios, **no únicamente GitHub Releases**.
- `package,consumer,integrity,publication`: `not_run|passed|failed|blocked`; solo `passed` si se comprobó cada producto/canal obligatorio desde remoto. Omitir no equivale a `passed`.
- `risk`: `routine|high|critical`; señales `release|git|archive|package|consumer|integrity|evidence|history|discovery|registry|publish|unknown`.
- `available_skills`: nombres observados realmente instalados, no sugerencias fingidas.
- `lens_gap`: boolean; nuevas lentes siempre requieren evaluación antes de activarse.

## Precedencia de acciones

1. `catalog`: solo listar lentes; no probar/publicar.
2. `inventory=unknown` o `product=unknown`: `inspect-product`.
3. `product_set!=complete`: `inventory-products` (faltantes explícitos → FAILED).
4. `route_set!=complete`: `route-channels` (canales omitidos → FAILED).
5. `basis=stale|unknown`: `refresh-basis`, no confiar en resultados antiguos.
6. `git_artifacts=bloated`: `plan-git-hygiene`; **no borrar automáticamente**.
7. `archive_confusion=true`: `clarify-source-archives` (seguir después).
8. `asset_set=unexpected|incomplete`: `fix-asset-set`, aunque checksums verdes.
9. `asset_set=unknown`: `inventory-assets`.
10. Fallos o bloqueos de `package|consumer|integrity|publication`: `investigate-failure`.
11. `package!=passed`: `inspect-package`; `consumer!=passed`: `verify-consumer`.
12. `integrity!=passed`: `verify-integrity`; `publication!=passed`: `publish-or-check-release`.
13. Todo completo/verde y remoto validado: `finish-release`. **Un router PASS no certifica nada**.

El estado de `cleanup` nunca autoriza `git filter-repo` ni `git push --force`; remite a análisis de riesgo y aprobación humana. `audit` informa hallazgos sin tocar archivos.

Lentes: se calculan a partir de señales reales e intención; solo `ready` genera acciones. `planned` no se ejecuta.
