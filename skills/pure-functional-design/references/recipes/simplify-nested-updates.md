# Receta: simplify-nested-updates

**Problema que atiende:** Copias anidadas repetidas y fricción de actualización. No es una obligación estilística ni una acción automática.

## Precondiciones y decisión

Consultar `../recipe-registry.json`: `requires` deben estar observadas y ninguna condición de `blocks` puede estar presente. Si falta una precondición, `INSPECT_MORE`; ante una contraindicacion real, `BLOCKED` para esta receta. Comparar siempre `KEEP_AS_IS` y la extracción local más pequeña.

## Procedimiento reversible

1. Inventariar updates y aliasing; comparar `copy` directo, optics si existentes, estructuras persistentes o `mut` local encapsulado; elegir mínimo según frecuencia/volumen; verificar equivalencia.
2. Documentar punto de reversión, versión del código y qué consumidor se migra primero. No borrar la ruta anterior antes de verificar.
3. Identificar garantías de errores, IO/orden, datos serializados, concurrencia y consumidores que deben permanecer idénticas.
4. Verificar con las pruebas selectivas adecuadas; coordinar con `delivery-first-testing` si está realmente disponible. Reportar `NOT_RUN` si falta ejecución.

## Contraindicaciones y no aplicabilidad

No añadir Arrow optics o una nueva crate por una sola actualización; Kotlin List read-only no implica inmutabilidad profunda.

## Criterio de cierre

Menos lógica repetida sin regresión de coste ni mutabilidad compartida. Nunca usar menos LOC ni más sintaxis Haskell como criterio suficiente.
