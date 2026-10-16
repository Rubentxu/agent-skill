---
name: cognicode-diagrams
description: "Investiga la arquitectura implementada con CogniCode CLI/MCP mediante preguntas, pruebas de capacidades por lenguaje y evidencia estructurada; produce Mermaid, Structurizr, LikeC4 y atlas en workspace externo."
---

# CogniCode Diagrams — decisiones verificables

**Regla principal:** investigar exclusivamente mediante capacidades **estructuradas** de CogniCode CLI/MCP orientadas a símbolos, relaciones y contexto de código. **No sustituir** una capacidad pertinente por búsquedas textuales o lecturas completas por comodidad. **No usar documentación** del repositorio como evidencia arquitectónica, aunque CogniCode la encuentre. El diagrama refleja **código implementado**, no README, ADR, propuestas ni roadmaps.

## Límites obligatorios

- Ni agente ni **SUBAGENTES** pueden leer, listar, buscar o ejecutar directamente archivos del checkout (código, configuración, manifiestos, tests, ADR, documentación) con shell, Git, editor, GitHub, otro indexador o un agente explorador. Solo **CogniCode CLI/MCP** investiga la implementación.
- **PROYECTORES** Mermaid, Kroki, Structurizr, LikeC4 y Markmap consumen únicamente artefactos derivados bajo `~/.cognicode-diagrams/`. Nunca montan o investigan el repositorio.
- `read_file(raw)` y `search_content` **no pueden reconstruir arquitectura** cuando falle el análisis estructurado. La búsqueda textual solo localiza candidatos que requieren confirmación estructurada; solicitar código **por símbolo** cuando sea posible. Investigación textual alternativa expresamente autorizada = **otro modo**, sin declarar `IMPLEMENTATION_GROUNDED`.
- Sin CogniCode: `BLOCKED`; sin evidencia suficiente: `PARTIAL/UNKNOWN`. No suplir con lectura directa, documentos ni inferencias convertidas en hechos. No modificar CogniCode.

## Protocolo de decisión, obligatorio antes de modelar

1. **Pregunta concreta** con símbolo o ámbito, lenguaje y plano: ¿entrada ejecutable, responsabilidad, colaborador, interacción, almacenamiento o frontera?
2. **Descubrimiento real**: ayuda/capabilities si el CLI instalado las admite o MCP `initialize` + `tools/list` paginado y schemas. **Anunciada ≠ funcional**.
3. **Comprobación por lenguaje sobre símbolo real**: índice, identidad, ubicación, contexto, relación pertinente y cobertura/limitaciones. Guardar resultado por **capacidad + lenguaje**. El fallo del grafo general no significa «Kotlin incompatible».
4. **Elección de una capacidad pertinente** según [research-protocol.md](references/research-protocol.md), sin invocarlas todas. Preferir respuestas estructuradas; usar lo ya obtenido si basta.
5. **Evidencia antes de dibujar**: cada elemento/arista vincula pregunta, consulta-respuesta CogniCode, símbolos, relación, plano y limitaciones. El agente interpreta pero nunca eleva inferencias a hechos.
6. **Fin acotado**: si no hay progreso, probar otra capacidad estructurada relevante o cerrar pregunta `PARTIAL/UNKNOWN`. Más detalle = nueva pregunta y consultas concretas; jamás bucles sin valor.

`scripts/affordances.py` aplica las decisiones puras de `scripts/research_protocol.py`: un `graph_ready`/`claim_coverage=verified` declarado **no** permite saltarse el registro verificable de la pregunta. El helper no ejecuta CogniCode ni certifica autenticidad de sus respuestas.

## Navegación y salidas

- Investigación: [protocolo](references/research-protocol.md) → [consulta](references/scan.md) → [trazabilidad](references/evidence.md) → [lente C4](references/lenses/c4.md) → formato elegido.
- [Registro de lentes](references/lens-registry.json): `c4` está `ready`; `class`, `use-case` y `vertical-slice` siguen `planned`. [Extensión](references/extend-lenses.md).
- [Workspace externo](references/workspace.md), [validación](references/validate.md), [proyectores](references/projectors.md), [navegación](references/navigation.md) y [bootstrap autorizado](references/bootstrap.md). Traducción/preview/atlas **no** verifican arquitectura.
- [Contrato vinculante](references/investigation-contract.md); [evaluaciones](tests/skill-evals.md) y [tests](tests/test_research_protocol.py).

`VERIFIED` solo en el alcance realmente comprobado; de lo contrario `PARTIAL`, `BLOCKED`, `FAILED` o `UNSUPPORTED`. Las pruebas puras no equivalen a UAT con un agente real y CogniCode conectado.
