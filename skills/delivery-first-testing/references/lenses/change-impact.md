# Lente: impacto y selección mínima

**Pregunta:** ¿qué comportamientos y garantías podría alterar este cambio? Inspeccionar diff real, usos y consumidores, build graph, contratos públicos y datos persistidos. Prefiere capacidades y dependencias reales a listas de paths exactos. Un archivo renombrado sin cambio semántico no exige registrar una nueva capacidad; una nueva ruta pública sí.

Seleccionar tests por módulo/capacidad y dependencia inversa; añadir un smoke de frontera para cambio público. `unknown` o riesgo de infraselección se escala, no se convierte en selección vacía. Cambios de docs solo pueden ejecutar lint documental si no afectan código generado, release assets o documentación consumida como producto.

Si existen decenas de variantes de la misma regla, consultar [data-driven-design](data-driven-design.md): identificar particiones, límites e invariantes antes de crear más tests. En contratos costosos considerar un E2E efímero solo para la composición que no quede demostrada por contratos. Para seleccionar tests históricos, usar historial únicamente para **ampliar**, no estrechar, la selección estática hasta medir falsos negativos.

**Salida:** decisiones `run-affected`, `widen`, `defer-to-integration` con motivo, riesgo y comandos reales. No ejecutar por sí misma. Para cambios críticos (seguridad, durabilidad, artefactos, protocolo) mantener prueba discriminante en merge y RC según alcance. Contraprueba: introducir un consumidor nuevo no mapeado jamás debe producir PASS vacío.
