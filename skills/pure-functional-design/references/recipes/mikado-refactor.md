# Receta: mikado-refactor

**Problema que atiende:** Cambio bloqueado por dependencias. No es una obligación estilística ni una acción automática.

## Precondiciones y decisión

Consultar `../recipe-registry.json`: `requires` deben estar observadas y ninguna condición de `blocks` puede estar presente. Si falta una precondición, `INSPECT_MORE`; ante una contraindicacion real, `BLOCKED` para esta receta. Comparar siempre `KEEP_AS_IS` y la extracción local más pequeña.

## Procedimiento reversible

1. Intentar cambio pequeño; si falla, identificar impedimento concreto; registrar grafo de prerequisitos; revertir intento; resolver hojas de forma individual con pruebas; reintentar el cambio inicial.
2. Documentar punto de reversión, versión del código y qué consumidor se migra primero. No borrar la ruta anterior antes de verificar.
3. Identificar garantías de errores, IO/orden, datos serializados, concurrencia y consumidores que deben permanecer idénticas.
4. Verificar con las pruebas selectivas adecuadas; coordinar con `delivery-first-testing` si está realmente disponible. Reportar `NOT_RUN` si falta ejecución.

## Contraindicaciones y no aplicabilidad

No intentar cadena irreversible sin poder revertir. No usar grafo estimado de ficheros como prueba de dependencia semántica.

## Criterio de cierre

Secuencia de cambios pequeños con dependencias reales resueltas y preservación de contrato. Nunca usar menos LOC ni más sintaxis Haskell como criterio suficiente.
