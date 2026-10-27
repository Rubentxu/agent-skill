# Receta: branch-by-abstraction

**Problema que atiende:** Sustitución gradual de implementación con consumidores compartidos. No es una obligación estilística ni una acción automática.

## Precondiciones y decisión

Consultar `../recipe-registry.json`: `requires` deben estar observadas y ninguna condición de `blocks` puede estar presente. Si falta una precondición, `INSPECT_MORE`; ante una contraindicacion real, `BLOCKED` para esta receta. Comparar siempre `KEEP_AS_IS` y la extracción local más pequeña.

## Procedimiento reversible

1. Identificar seam estable con significado único; introducir abstracción mínima; direccionar consumidor a implementación antigua; desarrollar sustituta; comparación/rollout gradual; eliminar rama antigua, flag y abstracción innecesaria al cerrar.
2. Documentar punto de reversión, versión del código y qué consumidor se migra primero. No borrar la ruta anterior antes de verificar.
3. Identificar garantías de errores, IO/orden, datos serializados, concurrencia y consumidores que deben permanecer idénticas.
4. Verificar con las pruebas selectivas adecuadas; coordinar con `delivery-first-testing` si está realmente disponible. Reportar `NOT_RUN` si falta ejecución.

## Contraindicaciones y no aplicabilidad

No confundir significados homónimos entre bounded contexts; no introducir dual writes sin semántica de consistencia. Un seam trivial no necesita segunda capa.

## Criterio de cierre

Una única implementación/autoridad final, cambio reversible durante migración y datos consistentes. Nunca usar menos LOC ni más sintaxis Haskell como criterio suficiente.
