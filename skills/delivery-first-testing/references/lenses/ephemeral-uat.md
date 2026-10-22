# Lente: UAT efímero de feature

**Pregunta:** ¿el consumidor puede usar ahora la feature? Definir escenarios observables a partir de criterios de aceptación; elegir CLI real, interacción de navegador, API o ejecución instalada según riesgo. Usar datos aislados, assert sobre resultado público, esperas por condición observable y límites de tiempo. Evitar `waitForTimeout` fijo, DOM de implementación, coordenadas sin justificación y suites históricas completas.

Crear scripts temporales en directorio efímero externo (`mktemp -d` o equivalente), salvo política del proyecto. Si hay que conservar para CI, dejar una prueba pequeña y estable en el componente que la mantiene. No borrar evidencia antes de registrarla; no copiar secretos ni difundirla.

**Cierre:** criterios ejecutados con PASS/FAIL individual, defectos y correcciones, versión/artefacto, lista de UAT retirables. Nunca traducir `no pude levantar navegador` a PASS. Un UAT que encuentra un defecto no se elimina hasta decidir cómo proteger la garantía real.
