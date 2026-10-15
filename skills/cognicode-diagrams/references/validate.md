# Validación de cualquier lente: forma ≠ semántica ≠ realidad

1. **Formato**. Ejecutar un renderer/validador local solo si está instalado y el usuario autoriza sus efectos. Mermaid: CLI `mmdc` u otro renderer que acepte el dialecto concreto; Structurizr DSL: `structurizr validate -workspace <file>` según `structurizr help` en la versión instalada. Si faltan, `NOT_RUN` y artefacto `draft`, nunca `valid`.
2. **Lente**. Aplicar invariantes propios de `references/lenses/<lente>.md`. C4: C1/C2/C3 con fronteras adecuadas. Clases: tipos y herencia/composición verificados. Casos de uso: actores/objetivos. Vertical slice: distinguir dependencias estáticas de secuencia ordenada.
3. **Relaciones**. Revisar extremos existentes, IDs estables, cardinalidades cuando aplique, jerarquías, ámbito, direcciones y ausencia de inferencias tácitas. Emitir errores específicos ante pérdida de equivalencia.
4. **Corroboración**. Comparar las afirmaciones con código/manifiestos/docs/tests/trazas y límites del grafo. Evitar considerar CLI y MCP sobre el mismo grafo como dos fuentes independientes.
5. **Entre salidas**. Si ambas representan la misma lente, comprobar el conjunto de entidades y relaciones comunes, no la igualdad literal. Una adaptación de formato puede perder semántica: documentar el delta.

## Negative UAT

- Validador ausente => `PARTIAL`.
- JSON de comando inválido o grafo stale => no usarlo como evidencia completa.
- Lens `planned` => `UNSUPPORTED`.
- `class` + Structurizr => `UNSUPPORTED` para UML clases.
- `sequenceDiagram`/vista dinámica a partir de grafo estático => rechazar por ausencia de orden probado.
- Contenedor definido por una biblioteca de funciones => rechazar o etiquetar inferencia pendiente.

No llamar al estado `VERIFIED` sin especificar *qué* se verificó: sintaxis, estructura propia de la lente, equivalencia de formatos o fidelidad al código.

## Rendereo local con Kroki (opcional)

La guía [kroki.md](kroki.md) permite comprobar si Kroki **produce** SVG/PNG para una fuente, y observar errores del parser. Esa observación constituye evidencia de **renderización**, no de equivalencia semántica ni de fidelidad al código. La cobertura depende de versiones de los motores y de los companions instalados; distinguir `RENDERED`, `VISUAL_REVIEW_NOT_RUN` y validación semántica. Para múltiples vistas Structurizr, renderizar cada `view-key` relevante; no interpretar que un único `200 OK` las validó todas.

## LikeC4 y visualizadores interactivos

El agente genera y mantiene `.c4` en el workspace externo mediante [la receta LikeC4](formats/likec4-c4.md); la CLI de LikeC4 se emplea exclusivamente para `validate` del **protocolo** escrito. La UI LikeC4/Structurizr Local ofrece inspección del resultado, no una lectura de símbolos de código. Guardar estados independientes: `FORMAT_VALID`, `HTTP_READY`, `VISUALLY_REVIEWED`, `SEMANTICALLY_REVIEWED`. El router `preview` nunca afirma revisión visual por el simple HTTP 200. El agente solo declara fidelidad al código si previamente contrastó las entidades y relaciones con CogniCode y las fuentes necesarias, y la base continúa vigente.
