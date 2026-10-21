# Lente: mutation testing selectivo — calidad de la señal

**Pregunta:** ¿las aserciones que permanecerán detectan una implementación plausiblemente incorrecta?

1. Seleccionar un **seam crítico o modificado** (permisos, persistencia, orden de eventos, protocolos, identidad) o el test sustituto tras una consolidación. Fijar HEAD, comando y presupuesto temporal explícito; no ejecutar un sweep global en cada feature.
2. Exigir una baseline verde y un oráculo que observe salida/comportamiento. Ejecutar solo mutantes relevantes del módulo/fuente o el diff, usando el runner del proyecto. Si faltan herramientas, `NOT_RUN`, sin instalarlas en silencio.
3. Clasificar `KILLED` (test detecta defecto), `SURVIVED` (investigar debilidad), `TIMEOUT`, `NO_COVERAGE`, `EQUIVALENT/INVALID`. Un mutante superviviente **no prueba automáticamente un defecto** y un score alto no garantiza calidad.
4. Para sobrevivientes útiles, escribir o afinar la aserción más barata; reejecutar solo lo afectado. Si el mutante es equivalente/inviable, documentarlo y excluirlo de conclusiones. No inventar porcentajes ni gates globales.
5. Detenerse ante presupuesto consumido, coste desproporcionado o falta de beneficio. Priorizar mutantes de comparadores, validaciones, condiciones, serialización y transiciones de estado, no cambios cosméticos.

**Herramientas opcionales por stack:** [PIT JVM](https://pitest.org/), [cargo-mutants](https://github.com/sourcefrog/cargo-mutants), [Stryker JS/TS](https://stryker-mutator.io/), [mutmut Python](https://mutmut.readthedocs.io/).

**Cierre:** código/artefacto, subconjunto mutado, mutantes útiles eliminados/supervivientes, anomalías de ejecución, decisión para mejorar tests y coste observado. No modificar producto para satisfacer mutantes, ni prometer que un score sustituye una aceptación real.
