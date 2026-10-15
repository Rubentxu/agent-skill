# Extender lenses sin crear más skills ni runtime

Una lente es un playbook de decisión, no un agente autónomo ni subservicio. Nueva lente: definir una pregunta específica, señales observables, alcance, coste, riesgos de infraselección, cuándo se activa, criterios de no aplicabilidad, casos adversariales y `references/lenses/<id>.md`. Añadir registro con `id`, `status=planned` hasta tener playbook, tests y evaluación del agente. Solo marcar `ready` tras demostrar rutas y fallos; no ampliar el router por conveniencia de una feature.

## Descubrimiento a partir de evidencia

1. Detectar **situación sin resolver**: repetidos tests rotos, UAT caducado, selector subestimando dependencias, release no instalable, falsa señal verde.
2. Formular la pregunta que falta y verificar si una lente existente cubre el problema; preferir mejorarla antes que duplicar otra.
3. Probar en dos proyectos distintos y un contraejemplo donde no debe activarse. Medir si reduce tiempo de entrega/errores, no número de links.
4. Añadir evaluación manual del agente y al menos un test de router/catalogo, incluyendo que `planned` no se ofrece como activo.
5. Retirar la lente si deja de aportar una decisión nueva; no conservar catálogos históricos como obligación de release.

## Propuestas futuras (NO disponibles en el catálogo)

- `mutation-guidance`: recomendar mutantes sobre contratos críticos cuando evidencia de eficacia sea dudosa. No exigir mutation testing en cada feature.
- `historical-test-impact`: seleccionar por relación histórica entre cambios, tests y defectos; necesita repos suficientes y medición de falsos negativos.
- `cross-repo-consumer`: validar compatibilidad Fabric/PipelineK mediante consumidores reales; requiere versiones fijadas y matriz mínima.

Si una integración futura tiene coste operativo elevado, probar primero procedimiento manual; solo automatizar después de demostrar retorno.
