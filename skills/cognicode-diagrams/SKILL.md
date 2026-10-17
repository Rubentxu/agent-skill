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
2. **Descubrimiento real**: ayuda/capabilities si el CLI instalado las admite o MCP `initialize` + `tools/list` paginado y schemas. **Anunciada ≠ funcional**. Leer obligatoriamente metadatos `requires_graph`, `requires_persistence`, `stability`, prerequisites y limitations por tool.
3. **Preflight por lenguaje y sesión**, antes de prometer C4: contrastar registro de la versión instalada; comprobar identidad del proceso MCP y base del grafo. `No graph available` = precondición no satisfecha, **no** lenguaje/tool unsupported. [Procedimiento](references/session-preflight.md).
4. **Comprobación por lenguaje sobre símbolo real**: índice, identidad, ubicación, contexto, relación pertinente y cobertura/limitaciones. Guardar `probes[lenguaje]` por cada capacidad: un éxito de Rust no certifica Kotlin. El fallo del grafo general no significa «Kotlin incompatible».
5. **Elección de una capacidad pertinente** según [research-protocol.md](references/research-protocol.md), sin invocarlas todas. Preferir respuestas estructuradas; usar lo ya obtenido si basta.
6. **Evidencia y cobertura antes de dibujar**: cada elemento/arista vincula pregunta, consulta-respuesta CogniCode, símbolos, relación, plano y limitaciones. Comprobar con CogniCode los **archivos omitidos** y su relevancia para la vista; si son esenciales o desconocidos, `PARTIAL/UNKNOWN`. El agente interpreta pero no eleva inferencias a hechos.
7. **Fin acotado**: si no hay progreso, probar otra capacidad estructurada relevante o cerrar pregunta `PARTIAL/UNKNOWN`. Más detalle = nueva pregunta y consultas concretas; jamás bucles sin valor.

`scripts/affordances.py` aplica las decisiones puras de `scripts/research_protocol.py`: un `graph_ready`/`claim_coverage=verified` declarado **no** permite saltarse el registro verificable de la pregunta. El helper no ejecuta CogniCode ni certifica autenticidad de sus respuestas.

## Navegación y salidas

- Investigación: [preflight de sesión](references/session-preflight.md) → [protocolo](references/research-protocol.md) → [consulta](references/scan.md) → [trazabilidad](references/evidence.md) → [lente C4](references/lenses/c4.md) → formato elegido.
- [Registro de lentes](references/lens-registry.json): `c4` está `ready`; `class`, `use-case` y `vertical-slice` siguen `planned`. [Extensión](references/extend-lenses.md).
- [Workspace externo](references/workspace.md), [validación](references/validate.md), [proyectores](references/projectors.md), [navegación](references/navigation.md) y [bootstrap autorizado](references/bootstrap.md). Traducción/preview/atlas **no** verifican arquitectura.
- [Contrato vinculante](references/investigation-contract.md); [evaluaciones](tests/skill-evals.md) y [tests](tests/test_research_protocol.py).

`VERIFIED` solo en el alcance realmente comprobado; de lo contrario `PARTIAL`, `BLOCKED`, `FAILED` o `UNSUPPORTED`. Las pruebas puras no equivalen a UAT con un agente real y CogniCode conectado.

## Proyección editorial opcional — criterios de diagram-design

Para explicar una topología C4 ya investigada con claridad visual, seleccionar **primero el significado**, después la representación. C4 técnico sigue siendo la autoridad de modelo; una vista editorial HTML/SVG es **otra proyección del mismo ledger**, no una nueva fuente de verdad. **No copiar 45 tipos, no releer checkout ni usar Mermaid como evidencia.**

- Ejecutar `python3 scripts/editorial.py --repo <raíz explícita> --view <id>` **solo** para una vista C4 de implementación con entidades y `graph_edge` acreditadas por queries existentes; ninguna `reference_link` se eleva a arista.
- La proyección limita 2–9 nodos, 12 aristas y 5 conexiones por nodo; no omite elementos para caber, sino que rechaza selecciones demasiado grandes. `PARTIAL/UNKNOWN` se muestra si la cobertura no es completa.
- Añadir ambos resultados `*.editorial.svg` y `*.editorial.html` al `*.atlas.json` existente; sincronizar Markmap. El HTML se sirve aislado por CSP, no ejecuta JS ni requiere contenedor.
- Para dependencias, secuencias o UML cuyas lentes siguen `planned`, no prometer soporte. Si una tabla responde igual de bien, no dibujar.

[Router, contrato, límites y uso](references/editorial.md). La salida editorial no convierte `RENDERED` en `IMPLEMENTATION_GROUNDED`.

## Atlas incremental y visual thinking (obligatorio)

- **Durante** la investigación, consolidar claims/queries CogniCode en el ledger externo y sincronizar el atlas **tras cada observación útil**, antes de crear diagramas: `python3 scripts/atlas.py sync --repo <raiz>`.
- **Cada vista nueva** vincula `claim_ids` con sus fuentes y renders reales en `lenses/<lens>/reports/<vista>.atlas.json`; sincronizar de nuevo. Reutilizar todos los recursos generados sin duplicar ni reinterpretar conocimiento.
- En Agent Teams un integrador único consolida el ledger y actualiza el atlas mientras otros agentes investigan/renderizan vistas independientes. No hay escrituras simultáneas al mismo ledger ni una base de datos añadida.
- Renderizar HTML Markmap al revisar visualmente o al cerrar un bloque, **no en cada consulta**. El atlas ofrece navegación `símbolo → claim → evidencia → proyecciones`; no sustituye el grafo CogniCode ni certifica frescura del código. [Contrato operativo](references/knowledge-atlas.md).

## Procedencia visual, taxonomía y vistas honestas

La skill clasifica **solo conceptos respaldados** mediante `claim.category`: `system`, `module`, `surface`, `external`, `store`, `signal`, `coverage`, `glossary` o `symbol`. Estas categorías son opt-in, **no** nuevas consultas obligatorias ni inferencias a partir de archivos/renderers. Para cada entidad se conserva `claim_id`, `query_ids`, `plane=static|runtime|deployment` y `coverage=complete|partial|unknown`; un antiguo `observed` sin consulta acreditada queda como `UNKNOWN`.

La rama `intent` solo acepta `CODE_DOC` (docstring/KDoc extraído mediante CogniCode) o `CURATED_INTENT` (usuario/curador identificado). `DOC_INTENT` por lectura directa de documentación del checkout no se permite. La intención no justifica una vista `plane=implementation`; para vista curada usar `plane=intent`. El HTML de Markmap o un diagrama LikeC4 válido tampoco certifican arquitectura.

Las propiedades de relación `kind`, `technology`, `endpoint` y `order` se añaden solo desde resultados CogniCode, no por nombres de símbolos. Una composición declarada (`Mono.when`, `then`) podrá explicarse como **orden declarado en código**, no como comportamiento runtime observado. `find_usages` sigue siendo `reference_link`, no arista de grafo.

[Contrato y ejemplo LikeC4](references/visual-evidence.md). El agente incorpora automáticamente al atlas cada nueva consulta/vista **con valor**, pero no vuelve a escanear para completar ramas ni crea vistas redundantes.

## Antibloqueos operativos

- Escalera: **símbolo → referencia → grafo en el mismo proceso (si es necesario) → contexto por símbolo → PARTIAL**. No ejecutar `build_graph` por rutina.
- Una referencia de `find_usages` es `reference_link` con `query_id + index + path:line`, **no** una `graph_edge` con `relation_id` inventado. [Contrato](references/evidence-reference-links.md).
- Límite de vista: **15 nodos**; más requiere división por componente/bounded context, no texto pequeño. [C4](references/lenses/c4.md).
- Si el LikeC4 DSL falla por kinds, declarar los kinds base usados y validar en la versión local. [Guía](references/formats/likec4-kinds.md).
