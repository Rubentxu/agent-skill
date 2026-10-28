# Lente: descomponer hitos en tareas de valor

**Pregunta:** ¿Qué tareas mínimas forman una entrega verificable sin duplicar reglas ni documentación?

1. Describir la **capacidad entregable del hito** y el contrato de su consumidor; si no existe entrega observable, es un tema de investigación, no 20 tareas hipotéticas.
2. Descomponer en cortes verticales por responsabilidad/caso de uso (contrato, decisión, adaptador, recorrido consumidor); priorizar el camino que da valor temprano, no tareas de capas horizontales ni refactors decorativos.
3. Escribir una tarea con: título concreto (verbo+resultado), resultado, evidencia/sourceRef, referencias ADR/SPEC, aceptación observable, límites/no-alcance, DoD/gate, dependencia genuinamente bloqueante, riesgo y esfuerzo comparativo. No sustituir AC por "implementar X", ni DoD por test que no ejecuta.
4. Distinguir prioridad **propuesta** P0–P3 de los labels configurados de Backlog.md (`priorities`). Impacto, urgencia, riesgo y esfuerzo son inputs declarados; el selector solo produce un **orden ordinal explicable**, nunca inventa puntuaciones observadas. No marcar "High" en Backlog sin leer prioridades permitidas.
5. Preferir bloques largos de valor como hitos, con tareas pequeñas y PRs revisables. Trabajo paralelizable sólo si no comparte el mismo propietario/archivo/gate y sus dependencias están cerradas; con agente único, seleccionar un objetivo READY cada vez.
6. Política de pruebas: aceptación antes de cambiar; pruebas unitarias selectivas, integración mínima, UAT/E2E efímeros si aportan valor. No duplicar `delivery-first-testing`. No mover certificación a implementación: merge, tag, release, artefactos y aceptación externa son gates separados cuando el proyecto realmente los exige.
7. La tarea no cierra hasta evidencia. Evidencias de SHA, test/revision, artefacto y gate se referencian, nunca se fabrican. `PAUSED/BLOCKED/OPEN` externos no se convierten directamente en columnas de Backlog.md.

**Contraprueba:** 60 tareas de componentes sin un flujo consumible y una tarea "certificar" marcada Done por pasar unos unit tests locales no significan un hito cerrado.
