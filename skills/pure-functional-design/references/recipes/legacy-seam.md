# Receta: legacy-seam

**Problema que atiende:** Comportamiento legado sin punto seguro de observación. No es una obligación estilística ni una acción automática.

## Precondiciones y decisión

Consultar `../recipe-registry.json`: `requires` deben estar observadas y ninguna condición de `blocks` puede estar presente. Si falta una precondición, `INSPECT_MORE`; ante una contraindicacion real, `BLOCKED` para esta receta. Comparar siempre `KEEP_AS_IS` y la extracción local más pequeña.

## Procedimiento reversible

1. Identificar un consumidor y observable crítico; protegerlo con caracterización discriminante; introducir seam mínimo a nivel de función/adaptador existente; conectar implementación nueva manteniendo antigua hasta demostrar paridad.
2. Documentar punto de reversión, versión del código y qué consumidor se migra primero. No borrar la ruta anterior antes de verificar.
3. Identificar garantías de errores, IO/orden, datos serializados, concurrencia y consumidores que deben permanecer idénticas.
4. Verificar con las pruebas selectivas adecuadas; coordinar con `delivery-first-testing` si está realmente disponible. Reportar `NOT_RUN` si falta ejecución.

## Contraindicaciones y no aplicabilidad

Evitar un sistema de mocks genérico y no construir abstracciones por defecto. Si el contrato no puede mantenerse, `BLOCKED`.

## Criterio de cierre

Seam temporal reversible, prueba significativa y mínima alteración pública. Nunca usar menos LOC ni más sintaxis Haskell como criterio suficiente.
