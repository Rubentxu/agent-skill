# Receta: domain-state-refactor

**Problema que atiende:** Estados inválidos construibles en el dominio. No es una obligación estilística ni una acción automática.

## Precondiciones y decisión

Consultar `../recipe-registry.json`: `requires` deben estar observadas y ninguna condición de `blocks` puede estar presente. Si falta una precondición, `INSPECT_MORE`; ante una contraindicacion real, `BLOCKED` para esta receta. Comparar siempre `KEEP_AS_IS` y la extracción local más pequeña.

## Procedimiento reversible

1. Mostrar un contraejemplo de estado inválido; distinguir protocolo/BD del dominio; diseñar ADT y smart constructors; planificar compatibilidad de variantes serializadas; migrar un caso de uso y consumidores.
2. Documentar punto de reversión, versión del código y qué consumidor se migra primero. No borrar la ruta anterior antes de verificar.
3. Identificar garantías de errores, IO/orden, datos serializados, concurrencia y consumidores que deben permanecer idénticas.
4. Verificar con las pruebas selectivas adecuadas; coordinar con `delivery-first-testing` si está realmente disponible. Reportar `NOT_RUN` si falta ejecución.

## Contraindicaciones y no aplicabilidad

No convertir el DTO de wire en un enum cerrado sin revisar schema evolution; no introducir typestate para estado persistido sin plan de restauración.

## Criterio de cierre

Invariante protegido en frontera del dominio, estados válidos representables, compatibilidad verificada. Nunca usar menos LOC ni más sintaxis Haskell como criterio suficiente.
