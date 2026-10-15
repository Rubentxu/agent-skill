# Lente: release y artefacto consumible

**Pregunta:** ¿la distribución exacta se instala, arranca, actualiza y cumple el producto público? Exigir artefacto identificable (commit/digest), lista completa esperada de assets, integridad de checksums, instalación limpia, CLI/API real, upgrade/rollback cuando aplica, compatibilidad y seguridad relevante. Validez de checksums de lo publicado NO demuestra que falten cero assets: verificar completitud además de integridad.

La certificación puede ser exhaustiva, pero solo en la frontera RC/publicación, no tras cada pequeño refactor. Proteger las claims del consumidor; diferenciar test que ejecuta aplicación empacada vs test que solo llama clases desde src. No publicar si falta el artefacto, la procedencia o un escenario crítico.

**Cierre:** artefactos usados, prueba de consumidor, evidencia de cobertura, resultado y riesgos residuales. No proclamar GA a partir de tests de desarrollo.
