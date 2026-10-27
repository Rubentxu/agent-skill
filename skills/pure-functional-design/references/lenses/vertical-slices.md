# Lente: vertical slices funcionales y seams correctos

**Pregunta:** ¿qué código es dueño de cada capacidad completa? **Señales:** `large-service`, `cross-context`, `duplicate-logic`.

## Procedimiento

1. Enumerar verbos observables, consumidores y entradas reales, no carpetas. Seleccionar **un** use case de coste bajo/valor alto.
2. Mapear flujo de entrada→orquestación→decisión→efectos→salida: clases y funciones concretas; rastrear dependencias inversas.
3. Nombrar límites de la capacidad sin inventar otra ontología (`run.start`, `run.cancel`, `run.tail` son usos distintos si sus invariantes divergen).
4. Extraer primero modelos y decisiones puras del flujo, después puertos de efecto y adaptadores mínimos. Cada regla e invariante tiene dueño único; la infraestructura interpreta, no redefine.
5. Hacer dependencias hacia dentro: `adapter -> application -> domain` (sin dependencias del dominio en red/BD); permitir librerías compartidas **solo** para semánticas realmente comunes, no un `common` lleno de utilidades.
6. Conservar compatibilidad de API/binarios/config y pruebas de comportamiento; retirar adaptadores temporales una vez migrados los consumidores reales.
7. Parar al obtener un slice consumible; repetir en siguiente slice, en vez de proponer extracción de todos los módulos de golpe.

**Cierre:** único punto dueño de regla; entradas/salidas reales compatibles; señales de complejidad reducidas; cambios reversibles; evidencia de tests o `NOT_RUN` honesto.

**No aplica:** mover archivos si el seam ya es explícito; inventar múltiples crates Gradle modules sin capacidad compartible o coste justificado.
