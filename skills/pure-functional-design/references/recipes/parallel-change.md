# Receta: parallel-change

**Problema que atiende:** Migración de contrato con consumidores simultáneos. No es una obligación estilística ni una acción automática.

## Precondiciones y decisión

Consultar `../recipe-registry.json`: `requires` deben estar observadas y ninguna condición de `blocks` puede estar presente. Si falta una precondición, `INSPECT_MORE`; ante una contraindicacion real, `BLOCKED` para esta receta. Comparar siempre `KEEP_AS_IS` y la extracción local más pequeña.

## Procedimiento reversible

1. Expand: admitir contrato anterior y nuevo; migrar cada consumidor/dato con compatibilidad medida; Contract: retirar compatibilidad al comprobar adopción. Versionar serialización y mantener rollback cuando corresponda.
2. Documentar punto de reversión, versión del código y qué consumidor se migra primero. No borrar la ruta anterior antes de verificar.
3. Identificar garantías de errores, IO/orden, datos serializados, concurrencia y consumidores que deben permanecer idénticas.
4. Verificar con las pruebas selectivas adecuadas; coordinar con `delivery-first-testing` si está realmente disponible. Reportar `NOT_RUN` si falta ejecución.

## Contraindicaciones y no aplicabilidad

No modificar esquemas durables sin plan de lectura de versiones, idempotencia y semántica transaccional. Para privado/atómico, cambio directo es preferible.

## Criterio de cierre

Consumidores migrados observados, compatibilidad preservada durante transición y código legado eliminado. Nunca usar menos LOC ni más sintaxis Haskell como criterio suficiente.
