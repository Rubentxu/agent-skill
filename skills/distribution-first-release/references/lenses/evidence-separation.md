# Lente: separar producto, fuente y certificación

**Producto:** launcher/binario, libs, recursos, LICENSE/NOTICE y verificadores normativos.
**Fuente:** Git (código, contratos, specs, tests permanentes, scripts de build).
**Evidencia:** certifier/CI/object storage (handoffs, XML, logs, NDJSON, screenshots, inventarios, pruebas de sesión).

1. Inventariar ruta, autor, autoridad, tamaño, retención y hash. Un release asset debe tener un consumidor y propósito de distribución demostrado.
2. Guardar referencias estables + SHA/digest/resultado en recibos ligeros, no duplicar ZIP de 93 MB por cada RC dentro de `evidence/` versionado.
3. Al cerrar una feature, ejecutar UAT/E2E/AAT temporales, guardar evidencia, decidir promoción de contrato permanente y retirar solo archivos de sesión autorizados.
4. **No borrar** pruebas históricas de seguridad/recuperación/secrets sin equivalencia probada y autoridad normativa.
5. No mover SHA256SUMS, SBOM, licencia ni otros assets obligatorios a «interno» por ahorro cosmético.

**Salida:** ubicación exacta y decisión por clase de artefacto; migraciones comprobadas, no supuestas.
