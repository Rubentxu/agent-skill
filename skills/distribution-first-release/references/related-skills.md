# Delegación por skills realmente disponibles

Leer `skill-registry.json` cuando aparezca una necesidad especializada. El catálogo **no** prueba que otra skill esté instalada: `available_skills` debe venir de la inspección real del agente. Delegar solo si coincide intención + señal. No invocar comandos imaginarios y no transferir credenciales ni artefactos privados a terceros.

- `delivery-first-testing`: aceptación efímera e integración funcional, no suplantar la prueba de instalación del paquete real.
- `pipelinek-local-ci`: autoridad local de CI, run de gates y pipeline de release/publish cuando la instalación/DSL lo soporta. La skill de distribución decide **qué** es producto y **dónde**; PipelineK ejecuta tareas reales comprobadas, nunca define un segundo inventario. Consultar [publishing-pipelinek](lenses/publishing-pipelinek.md).
- `code-quality-evidence-review`: informe de bugs de publicación con evidencia reproducible.
- `retrospective-cycle-audit`: reconciliar provenance de versiones antiguas, logs y recibos sin declarar PASS.

Si la skill secundaria no existe, la principal puede planificar adaptadores/conductores de publicación pero no atribuirse ejecución.
