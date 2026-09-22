# Contrastar candidatos y redactar hallazgos

## Unidad mínima de evidencia

Registrar **qué se comprobó** (afirmación falsable); **sobre qué base** (repositorio, SHA, diff y dirty status); **dónde** (archivo:líneas y símbolos de ambos extremos); **cómo** (consulta CogniCode o comando real, versión si importa, filtros y exclusiones); **qué devolvió** (fragmento verificable, salida/artefacto); **qué podría refutarlo**; **qué no cubre** (parsing, idioma, caché, código dinámico, tests no ejecutados).

Distinguir `EJECUTADO` (resultado observado), `CÓDIGO` (fuente/build inspeccionados), `DOCUMENTADO` (contrato o ADR), `HISTÓRICO` (otro SHA), `INFERIDO` (hipótesis) y `NO VERIFICADO` (falta de prueba). Una etiqueta no convierte una conclusión en verdadera.

Dos consultas del mismo grafo no son dos pruebas independientes. Contrasta cada afirmación con **la evidencia pertinente**, no necesariamente un segundo escáner: si el código importa directamente una implementación prohibida, localiza import, símbolo, regla y dependency del build; si se afirma fallo runtime, ejecuta test o aporta traza real.

## Falsos positivos frecuentes

- Grafo de llamadas ≠ dependencias de compilación; contrato por port puede ser correcto aunque existan llamadas entre capas.
- Ausencia de arista no demuestra ausencia universal: plugins, reflexión, DI, eventos, codegen, homónimos, lenguajes no soportados, errores y cachés.
- Centralidad ≠ rendimiento; cobertura de archivos del grafo ≠ cobertura de pruebas; test existente ≠ test pasado.
- Una convención de diseño no es automáticamente un requisito. No imponer arquitectura hexagonal, ADTs u OpenTelemetry si no corresponde.
- Vulnerabilidad de librería: comprobar paquete, versión y rango afectados, configuración y ruta de uso; no publicar secretos en bruto.

## Pruebas y gates

Para cambios en desarrollo: tests focales del código modificado y de sus consumidores/contratos; ampliar por riesgo. Para integración/release: ejecutar los gates completos exigidos por el repositorio y consultar los runs reales del **SHA que se integra**, no recibos anteriores. Registrar comando, entorno, resultado, tests y skips. Fallo, timeout, cancelación, no ejecutado y test omitido son estados distintos. Ejecutar tests/benchmarks o herramientas que descargan dependencias solo con autorización apropiada.

En seguridad dibujar `entrada → validación/sanitización → sink` y usar un escenario inerte para verificar límites sin intervenir servicios ajenos. En rendimiento comparar baseline/nuevo SHA bajo workload y entorno equivalentes. En dependencias contrastar lockfile/SBOM/artefacto real.

## Hallazgos: cinco campos en orden obligatorio

**Severidad:** BLOQUEANTE solo para gate obligatorio incumplido o fallo confirmado invalidante; ALTA/MEDIA/BAJA según impacto justificado; INFORMATIVA para observaciones y propuestas. Un gate NO EJECUTADO no es un test FALLA.

**Ubicación:** archivo/rango/símbolo y SHA; identificador de run/job si corresponde.

**Evidencia:** regla/contrato, código y consulta/comando ejecutado con resultado y alcance, corroboración o incertidumbre, pruebas a favor y en contra.

**Impacto:** mecanismo causal, consumidores afectados, observado o potencial (distinguir), límites.

**Recomendación:** cambio mínimo comprobable + prueba reproducible de cierre y momento de ejecución.

Mantener hipótesis y deuda histórica fuera de la sección de defectos confirmados. No fabricar hallazgos para completar una cuota. Un informe con cero defectos confirmados y límites explícitos es válido.
