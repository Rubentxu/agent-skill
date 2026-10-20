# Lente: baseline-and-preservation

En aplicación existente **leer código productivo y ejecutar la app si se dispone de entorno** antes de modificar; registrar el comportamiento contractual, controles, modos, colecciones de datos, listeners y almacenamiento. No deducir funcionamiento de nombres de handlers ni de capturas.

- Enumerar funcionalidades valiosas: modalidad diaria/libre, reintentar, reiniciar, navegación, exportación/importación, progreso, filtros, escenas y accesibilidad.
- Observar modelo de datos y su versión. Guardar copia/export antes de cambios destructivos. Aislar almacenamiento del navegador usado para UAT.
- Distinguir **informe de intención** vs implementación real. Un código legacy puede tener helpers muertos o duplicados; no conservar por inercia si su eliminación es autorizada.
- Declara invariantes por usuario, no DOM interno. Preparar un escenario positivo y uno negativo de riesgo.
- En creación, no exigir baseline ficticia. Al auditar, entregar observaciones y límites sin modificar HTML.
