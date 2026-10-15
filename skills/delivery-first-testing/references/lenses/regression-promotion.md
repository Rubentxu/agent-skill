# Lente: promoción/retirada de regresiones

**Pregunta:** ¿cuál es el menor test duradero que impediría repetir el defecto importante? Clasificar cada UAT `PROMOTE` (mantener mínimo), `REPLACE` (contrato/componente más barato), `RETIRE` (duplicado, exploratorio o detalle interno), o `DEFER` (riesgo aún no resuelto). Explorar si ya existe cobertura. Relacionar cada candidato con una garantía, fallo que discrimina, estabilidad bajo refactor seguro y coste estimado.

Nunca eliminar un test de seguridad, aislamiento, integridad, concurrencia o recuperación solo porque es frágil: cambiar seam o reemplazar primero. Nunca inflar suite con un E2E por cada variación de fixture. Tras refactor compatible el contrato debe seguir verde. El agente **propone** borrados, ejecuta solo si autorizado y se asegura de no dejar garantías sin observador.

**Cierre:** decisión por test candidato, prueba sustituta si aplica y aceptación de feature registrada fuera de pruebas temporales.
