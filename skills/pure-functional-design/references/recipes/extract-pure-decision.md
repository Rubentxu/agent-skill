# Receta: extract-pure-decision

**Problema que atiende:** Reglas mezcladas con IO. No es una obligación estilística ni una acción automática.

## Precondiciones y decisión

Consultar `../recipe-registry.json`: `requires` deben estar observadas y ninguna condición de `blocks` puede estar presente. Si falta una precondición, `INSPECT_MORE`; ante una contraindicacion real, `BLOCKED` para esta receta. Comparar siempre `KEEP_AS_IS` y la extracción local más pequeña.

## Procedimiento reversible

1. Localizar una decisión de negocio repetible; documentar inputs/outputs y efectos observables; caracterizarla; extraer `decide(state, cmd, context)`; dejar IO en el intérprete existente; migrar un consumidor.
2. Documentar punto de reversión, versión del código y qué consumidor se migra primero. No borrar la ruta anterior antes de verificar.
3. Identificar garantías de errores, IO/orden, datos serializados, concurrencia y consumidores que deben permanecer idénticas.
4. Verificar con las pruebas selectivas adecuadas; coordinar con `delivery-first-testing` si está realmente disponible. Reportar `NOT_RUN` si falta ejecución.

## Contraindicaciones y no aplicabilidad

No extraer si cambia atomización de una transacción, orden de efectos o fallos. Si faltan datos de la frontera transaccional, `INSPECT_MORE`.

## Criterio de cierre

Un caso conserva errores, persistencia, cancelación, orden de eventos y presenta lógica determinista aislada. Nunca usar menos LOC ni más sintaxis Haskell como criterio suficiente.
