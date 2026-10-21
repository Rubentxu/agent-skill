# Lente: promoción, sustitución y retirada de regresiones

**Pregunta:** ¿cuál es la menor protección duradera que habría detectado el fallo relevante?

Por cada UAT o test candidato: identificar garantía, fallo sensible, nivel adecuado (unitario, propiedad, contrato, integración, smoke real), coste y protección existente. Decidir `PROMOTE` (mínimo permanente), `REPLACE` (seam más barato), `RETIRE` (exploratorio o redundante) o `DEFER` (riesgo sin resolver).

**Regla de seguridad de retirada:** no borrar una prueba por tener el mismo nombre/fixture que otra. Demostrar equivalencia de garantía con un caso rojo discriminante, una variación dirigida o mutación focalizada, preferiblemente sobre el test que permanecerá. Si el test original ve un riesgo que la sustituta no detecta, conservarlo hasta cerrar el hueco. La cobertura por líneas nunca demuestra esta equivalencia.

Agrupar variaciones homogéneas en data-driven con límites representativos, conservando identificadores y mensajes por caso. Usar propiedades para reglas generales y contracts para fronteras. No promocionar automáticamente un E2E efímero: registrar aceptación y eliminar el escenario tras decidir. No cambiar producción para que pase un test acoplado a internos.

**Cierre:** `garantía | original | sustituto o justificación | evidencia | decisión | coste | riesgo`, resultado asociado a artefacto/HEAD vigente. Si falta herramienta/evidencia → `DEFER` o `BLOCKED`, nunca `RETIRE` silencioso.
