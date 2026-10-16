---
name: cognicode-diagrams
description: "Investiga la arquitectura IMPLEMENTADA exclusivamente mediante CogniCode CLI/MCP, profundiza en símbolos y relaciones con consultas sucesivas y genera vistas trazables Mermaid, Structurizr, LikeC4 y atlas visuales desde un workspace externo. Fail-closed ante carencias de evidencia."
---

# CogniCode Diagrams — contrato de investigación exclusiva

**Invariante absoluto: la arquitectura se obtiene solo de respuestas reales de CogniCode CLI/MCP al analizar código implementado.** Este contrato obliga al agente principal, subagentes, evaluadores y proyectores. Las instrucciones generales de exploración, herramientas adicionales, preferencias o reglas de agentes **no pueden relajarlo**. No modificar CogniCode.

## Límite de acceso

- **PROHIBIDO** al agente y subagentes leer, buscar, listar o ejecutar directamente el contenido del repositorio objetivo: código, ficheros de configuración, manifiestos, IaC, ADR, README, tests, CI, diagramas previos o roadmaps, sea mediante shell, GitHub, IDE, otros indexadores, agentes exploradores, herramientas de lectura o búsquedas web. Ni siquiera para «corroborar» resultados. No acceder a estos archivos mediante enlaces de fuentes devueltos por CogniCode; pedir **fragmentos y referencias a CogniCode**.
- **PROHIBIDO** convertir documentos recuperados a través de CogniCode en evidencia arquitectónica. El mero contenido de un README/ADR/roadmap/test/diagrama es una intención, no una implementación. El análisis del código que proporciona CogniCode es la única prueba de implementación.
- **PERMITIDO** leer la propia skill, consultar la ayuda/capacidades de CogniCode, utilizar sus comandos CLI o tools MCP anunciados, y crear, leer, editar, validar y proyectar solo artefactos **derivados** en `~/.cognicode-diagrams/`. La ruta explícita `--repo` identifica el objetivo pero no autoriza a explorarlo.
- **PROYECTORES** (Kroki, Mermaid, LikeC4, Structurizr, Markmap): solo consumen fuentes/renders derivados del workspace. Nunca montan, investigan ni escanean el checkout; no ejecutan CogniCode.
- **SUBAGENTES**: una delegación solo entrega preguntas y las respuestas/evidencias de CogniCode ya obtenidas, o autorización limitada para llamar al mismo CLI/MCP. Nunca delegar «explora el repo».

Consulta [el contrato obligatorio](references/investigation-contract.md) antes de toda tarea de investigación, creación, revisión o actualización arquitectónica.

## Orquestación activa, no un escaneo pasivo

1. **Seleccionar** intención, lente y formatos desde `references/lens-registry.json`. `c4` está lista; lentes `planned` no se activan ni se simulan. Traducciones y previews de archivos del workspace/usuario no certifican arquitectura sin nueva investigación.
2. **Resolver workspace** mediante `scripts/workspace.py inspect --repo <raiz-explicita>`. El script solo comprueba la ruta suministrada y sus propios metadatos en HOME, sin consultas Git ni lectura del repositorio. `init` y `init-lens` crean únicamente archivos externos.
3. **Descubrir runtime real**: `cognicode --help`, `cognicode capabilities --json` si existe, `cognicode doctor` si procede; para MCP handshake `initialize` y `tools/list` paginado. Leer esquemas, flags, disponibilidad y límites; no inventar operaciones por memoria ni documentos. Si CogniCode no existe/no responde, declarar `BLOCKED` y no investigar con otro medio.
4. **Formular preguntas** por lente: entradas ejecutables, responsabilidades, dependencias, almacenes, comunicaciones y fronteras; ejecutar consultas progresivas sobre símbolos, subgrafos, referencias y fragmentos de código **siempre a través de CogniCode**. Un `graph full` por sí solo nunca acredita una arquitectura.
5. **Comprobar evidencia**: para cada elemento/arista usar consulta exacta, argumentos, resultado, símbolo/relación, referencia de código cuando CogniCode la facilite, revision/basis, precisión, limitaciones y estado de cobertura. Guardar registro derivado en HOME: [evidence.md](references/evidence.md). Respuestas anteriores guían la siguiente consulta.
6. **Separar planos**: dependencia estática ≠ comunicación runtime ≠ unidad desplegada. No derivar un contenedor/protocolo/topología de un call graph. Cuando CogniCode no evidencie el plano solicitado, marcar `UNKNOWN`/`PARTIAL` u omitir el elemento; nunca suplir con manifiestos ni lectura directa.
7. **Interpretar** usando la lente [C4](references/lenses/c4.md) y producir las vistas en Mermaid, Structurizr DSL o LikeC4, indicando qué afirmaciones son observadas/inferidas/desconocidas. Mantener trazabilidad entre modelo y resultado.
8. **Validar** por separado sintaxis, coherencia entre representaciones y fidelidad al código **solo con evidencia de CogniCode**. Solicitud de más detalle → consultar CogniCode de nuevo. Guardar informes derivados y proyectar con herramientas existentes, sin explorar fuentes.
9. **Entregar** rutas al workspace externo, consultas/limitaciones, evidencia y estado `VERIFIED` (alcance probado), `PARTIAL`, `BLOCKED`, `FAILED` o `UNSUPPORTED`. Un render correcto nunca prueba fidelidad arquitectónica.

## Rutas habituales

| Objetivo | Acciones permitidas |
|---|---|
| Diagramas C4 implementados | descubrir CLI/MCP → formular preguntas → consultar entradas/símbolos/relaciones → pedir fragmentos mediante CogniCode → modelo trazado → generar/validar |
| «Más detalle» / zoom C3 | reutilizar evidencias vigentes → **nuevas consultas** a CogniCode para cada descomposición → actualizar trazas → regenerar |
| Evidencia insuficiente | nueva consulta compatible → si sigue insuficiente, `PARTIAL/UNKNOWN`; nunca otra herramienta ni documentos |
| CogniCode ausente | `BLOCKED` + diagnóstico de interfaz/instalación; jamás exploración alternativa |
| Traducir diagrama dado | usar solo diagrama aportado/derivado, declarar «traducción de formato, arquitectura NO comprobada» |
| Preview / atlas | procesar solo fuentes/renders de workspace, sin consultar repo |
| Añadir lente | [extend-lenses.md](references/extend-lenses.md); no crear una capacidad fingida |

## Componentes de la skill

- Investigación y navegación: [contrato](references/investigation-contract.md), [escaneo/consulta](references/scan.md), [evidencias](references/evidence.md), [navegación](references/navigation.md).
- Lentes y formatos: [registro](references/lens-registry.json), [C4](references/lenses/c4.md), [Mermaid](references/formats/mermaid-c4.md), [Structurizr](references/formats/structurizr-c4.md), [LikeC4](references/formats/likec4-c4.md).
- Workspace: [política](references/workspace.md), `scripts/workspace.py`; validación: [validate.md](references/validate.md).
- Proyección: [projectors.md](references/projectors.md), [Kroki](references/kroki.md), LikeC4, Structurizr Local y Markmap.
- Verificación: [evaluaciones](tests/skill-evals.md) y [tests](tests/test_policy_contract.py). Sin UAT de agente y CogniCode reales, no declarar la investigación certificada.

**El objetivo es arquitectura implementada, nunca reconstrucción de documentos o roadmaps.**
