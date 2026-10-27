# Receta: algorithm-substitution

**Problema que atiende:** Complejidad/coste de algoritmo injustificado. No es una obligación estilística ni una acción automática.

## Precondiciones y decisión

Consultar `../recipe-registry.json`: `requires` deben estar observadas y ninguna condición de `blocks` puede estar presente. Si falta una precondición, `INSPECT_MORE`; ante una contraindicacion real, `BLOCKED` para esta receta. Comparar siempre `KEEP_AS_IS` y la extracción local más pequeña.

## Procedimiento reversible

1. Establecer oráculo, semántica de orden y volumen; comparar bucle actual, transformación funcional y algoritmo especializado; estimar O(T,M); aplicar candidato más claro que no empeora coste; medir hot path si relevante.
2. Documentar punto de reversión, versión del código y qué consumidor se migra primero. No borrar la ruta anterior antes de verificar.
3. Identificar garantías de errores, IO/orden, datos serializados, concurrencia y consumidores que deben permanecer idénticas.
4. Verificar con las pruebas selectivas adecuadas; coordinar con `delivery-first-testing` si está realmente disponible. Reportar `NOT_RUN` si falta ejecución.

## Contraindicaciones y no aplicabilidad

No sustituir `for` por `fold` con clones cuadráticos ni greedy sin prueba de optimalidad. Si el bucle ya es claro, `KEEP_AS_IS`.

## Criterio de cierre

Propiedades semánticas preservadas, complejidad explicada y coste real justificado. Nunca usar menos LOC ni más sintaxis Haskell como criterio suficiente.
