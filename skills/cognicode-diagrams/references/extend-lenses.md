# Extender lentes sin romper exclusividad

La lente solo define pregunta, ontología, criterios de evidencia y representación; **jamás abre el código objetivo**. Los medios de investigación se limitan a **CogniCode CLI/MCP**, con capacidades y esquemas descubiertos en su versión ejecutada. Los subagentes heredan idéntica prohibición de leer repo/README/ADR/manifiestos/pruebas. [Contrato](investigation-contract.md).

1. Definir preguntas observables sobre la **implementación** y los conceptos que precisa (tipos, entradas, actores demostrados por código, secuencias demostradas por código).
2. Escribir `references/lenses/<id>.md` con el flujo de consultas **a través de CogniCode**: descubrimiento, preguntas, profundización por símbolo, solicitud de fragmentos, trazabilidad, límites, estados de cobertura y fallos cerrados. Nada de «leer archivos para verificar».
3. Añadir `references/lens-registry.json` como `planned`. Cambiar a `ready` solo tras validar que el runtime real expone las consultas necesarias y ejecutar evaluaciones con evidencia de código; no inventar comandos ni generar ontologías implementadas desde documentos.
4. Añadir guía de formato si es compatible y comprobar Mermaid/Structurizr/LikeC4 con artefactos **derivados**. El proyector no es analizador.
5. Añadir pruebas de ausencia de CogniCode, consulta de mayor detalle, documentos contradictorios, evidencia parcial y aislamiento de subagentes/proyectores.
6. Conservar el workspace externo. No crear otro motor de grafos o agente explorador.

Matriz vigente: `c4` = `ready` (Mermaid, Structurizr, LikeC4); `class`, `use-case`, `vertical-slice` = `planned`. `class` no tiene equivalencia nativa UML en Structurizr. La autoridad de estado es el JSON, no esta síntesis.
