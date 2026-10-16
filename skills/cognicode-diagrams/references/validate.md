# Validación: sintaxis ≠ evidencia ≠ ejecución

1. **Sintaxis**: usar Mermaid, Structurizr, LikeC4 o Kroki solo sobre fuentes derivadas del workspace; ejecutar el validador únicamente cuando esté disponible/autorizado. Si no, `NOT_RUN`, nunca `VALID`.
2. **Semántica de lente**: IDs, relaciones dirigidas, jerarquías C1/C2/C3, fronteras y formato correcto. No transformar call graph en secuencia runtime ni inferir protocolo o despliegue.
3. **Fidelidad a implementación**: contrastar todos los claims factuales contra consultas y **fragmentos de código suministrados por CogniCode**. No leer código, docs, ADR, manifiestos, tests o trazas por otra interfaz; documentos no acreditan implementación aunque CogniCode los encuentre.
4. **Entre salidas**: comparar entidades/aristas del ledger y representaciones generadas; identificar diferencias de adaptación.
5. **Cobertura y actualidad**: si CogniCode no garantiza alcance/snapshot o informó omisiones, la fidelidad queda `PARTIAL`; sintaxis/render pueden verificarse independientemente.
6. **Mayor detalle**: exigir nuevas consultas y nuevos `query_id`. Sin CogniCode, bloquear actualización; sin evidencia suficiente, declarar desconocido.

## Negative UAT

- CogniCode inaccesible ⇒ `BLOCKED` sin escanear con otra herramienta.
- Documentación contradice código ⇒ el documento no modifica el modelo; solo pruebas de CogniCode.
- Subagente intenta explorar repo ⇒ denegar tarea.
- Proyector intenta montar checkout ⇒ rechazo.
- Validador ausente ⇒ formato `NOT_RUN`, vista `PARTIAL`.
- Grafo vacío, incompleto o solo contadores ⇒ no `IMPLEMENTATION_GROUNDED`.
- Sin evidencia de runtime/despliegue ⇒ `UNKNOWN`, no secuencias ni contenedores supuestos.

Mermaid/Kroki/LikeC4/Structurizr verifican **solo proyección/sintaxis**, no la verdad del código. [Contrato](investigation-contract.md).
