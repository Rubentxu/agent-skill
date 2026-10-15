---
name: cognicode-diagrams
description: "Orquesta diagramas y vistas de código basados en CogniCode CLI/MCP: instala y verifica bajo autorización, prepara escaneos, interpreta evidencias y genera, revisa o traduce Mermaid y Structurizr DSL mediante lentes especializadas. C4 disponible; extensible a casos de uso, clases, vertical slices y futuras lentes sin modificar CogniCode. Navegación guiada por affordances tipo HATEOAS."
---

# CogniCode Diagrams — orquestación de lentes especializadas

**Límite innegociable:** NO modificar CogniCode (Rust, CLI, MCP, releases, API, pipelines ni Explorer). CogniCode es una herramienta externa: aporta inspección de símbolos, grafos y relaciones. El **agente** interpreta su respuesta, contrasta evidencias y genera los diagramas. Este paquete es UNA skill instalable y autocontenida, no un servidor REST ni una biblioteca de diagramas.

## Distinciones fundamentales

- **Lente** = pregunta y ontología que gobiernan el diagrama: `c4` ahora; más adelante `use-case`, `class`, `vertical-slice`, etc.
- **Formato** = lenguaje de representación: `mermaid` y `structurizr`. No todos los formatos expresan todas las lentes de manera equivalente.
- **Evidencia** = resultados reales de CLI/MCP + código, manifiestos, ADR, requisitos, tests o trazas. La mera existencia de un call graph no prueba despliegue, casos de uso ni orden runtime.
- **Workspace externo** = `~/.cognicode-diagrams/workspaces/<repo-name>--<id>/`; siempre fuera del repositorio Git, almacena fuentes, imágenes y evidencias derivadas sin duplicar índices de CogniCode.
- **Affordance** = acción posible según observación (`rel` + `href` local + precondiciones); no es una petición HTTP ni un comando inventado. El catálogo de acciones se deriva de la sesión actual; solo se ejecutan las útiles y autorizadas.

## Navegación orientada al objetivo (entrada única)

1. Entender la intención: `setup`, `scan`, `catalog`, `discover`, `create`, `interpret`, `translate`, `review`, `update`, `validate` o `preview`; lente y formato cuando sean necesarios. Si el usuario proporciona un diagrama para traducir, **no** instalar ni escanear por defecto.
2. Consultar [el catálogo declarativo](references/lens-registry.json). `status=ready` significa que hay procedimiento dentro del paquete; `planned` **no** significa implementado. Comprobar que la combinación lente/formato existe y su semántica (`native`, `adapted`, `unsupported`). No simular una lente inexistente.
3. Resolver **antes de escanear o generar archivos** [el workspace externo del proyecto](references/workspace.md) mediante `scripts/workspace.py inspect`; si está ausente, inicializarlo bajo `~/.cognicode-diagrams` y verificar `ready`. Si es inválido, bloquear escrituras. No guardar ningún artefacto en Git. Observar las capacidades y el estado real: CLI/MCP, ruta, revisión/dirty, índice/grafo y sus límites, archivos de entrada, validadores, permisos. Usar [navegación de sesión](references/navigation.md) para presentar solo acciones habilitadas. `scripts/affordances.py` es un ejemplo **puro, opcional** para comprobar el catálogo, nunca realiza acciones ni persiste estado.
4. Cargar solo la referencia indicada en la acción seleccionada: [instalación](references/bootstrap.md), [escaneo](references/scan.md), [lectura y evidencia](references/evidence.md), [lente seleccionada](references/lenses/c4.md) o [representación](references/formats/mermaid-c4.md), [Structurizr](references/formats/structurizr-c4.md). Reinspeccionar tras cada paso: nunca avanzar por mera suposición.
5. Para interpretar un diagrama existente usar [interpretación](references/interpret.md). Para revisar el modelo contra el código, contrastar cada relación por su fuente. Aplicar [validación](references/validate.md) a la representación y a la semántica por separado.
6. Si se solicita imagen o inspección visual, cargar [renderización local con Kroki](references/kroki.md). La intención `preview` utiliza los ficheros producidos sin requerir escanear CogniCode de nuevo; no arrancar contenedores sin autorización. Un SVG/PNG válido indica `RENDERED`, no verificación arquitectónica.
7. Entregar los artefactos solicitados con un informe de evidencias, avisos y estado `VERIFIED`, `PARTIAL`, `BLOCKED`, `FAILED` o `UNSUPPORTED`. Nunca presentar un test no ejecutado, una herramienta ausente o un grafo vacío como PASS.

## Rutas por intención

| Petición | Ruta mínima (se omiten las acciones innecesarias) |
|---|---|
| "Instala/prepara CogniCode" | inspeccionar → instalar **solo si autorizado** → `doctor` + prueba MCP real |
| "Escanea este proyecto" | inspeccionar → índice/consultas mínimas → grafo si aporta → comprobar lectura real y cobertura |
| "Haz C4 del repositorio" | preparar evidencia → lente `c4` → modelo interpretado → Mermaid y/o Structurizr → validar |
| "Traduce este DSL a Mermaid" | leer diagrama → reconstruir semántica → comprobar compatibilidad → generar → validar. **No exige CogniCode** |
| "Previsualiza/visualiza los diagramas" | comprobar Kroki local → elegir gateway para Structurizr/companion para Mermaid → exportar SVG/PNG por POST → revisión visual; no rescanear por defecto |
| "Actualiza según el código" | interpretar diagrama → refrescar evidencia si está caducada → reconciliar → cambios mínimos → validar |
| "Quiero clases/vertical slices/casos de uso" | consultar catálogo; si `planned`, informar de la capacidad pendiente y remitir a [cómo añadir lentes](references/extend-lenses.md); no fingir soporte |

## Contratos de evidencia y ejecución

- Usar únicamente comandos y esquemas anunciados por el ejecutable actual (`--help`) y por `tools/list` del MCP. No confundir `cognicode-mcp` con `explorer-mcp`, que no es requisito ni está en la distribución estable de `cogh`.
- Lecturas y grafo pueden actualizar caches o índices; informar efectos y permisos. No instalar, cambiar IDE, ejecutar scripts ajenos ni transmitir código privado a servicios externos sin autorización.
- Diferenciar `OBSERVED`, `INFERRED`, `CURATED`, `UNKNOWN` por entidad/relación. Una declaración humana no equivale a una evidencia runtime. Versionar mentalmente toda afirmación: workspace, SHA, dirty y límites del análisis.
- Reutilizar CogniCode; no crear índices canónicos, bases de conocimiento duplicadas, motores de grafos ni un DSL universal propio. La representación conceptual vive en el contexto del agente o en un informe **derivado** opcional, no como nuevo sistema de registro.
- Si el formato solo ofrece una **adaptación**, comunicar qué se pierde. Ejemplo: Structurizr DSL no tiene un diagrama UML de clases nativo; el diagrama de clases Mermaid `classDiagram` no es lo mismo que una vista C4 de componentes.
- Una comprobación de sintaxis no acredita fidelidad arquitectónica. `VERIFIED` requiere alcance de verificaciones explicitado; sin herramienta de validación de sintaxis o sin cobertura suficiente, declarar `PARTIAL`.
- **Nunca escribir los assets de esta skill en el repositorio Git por defecto.** Ubicación obligatoria: `~/.cognicode-diagrams/workspaces/<repo-name>--<id>/`. Resolverla con `scripts/workspace.py`; no crear ficheros, carpetas auxiliares, `.gitignore` ni datos de sesión en la raíz Git. Si una excepción explícita requiere exportar al checkout, pedir permiso aparte. Ver [workspace.md](references/workspace.md).

## Referencias a cargar solo bajo demanda

- [Workspace externo obligatorio](references/workspace.md) y [resolver/crear workspace](scripts/workspace.py)
- [Navegación y contratos](references/navigation.md)
- [Registro de lentes](references/lens-registry.json), [añadir nuevas lentes](references/extend-lenses.md)
- [Instalación](references/bootstrap.md), [escaneos](references/scan.md), [evidencias](references/evidence.md)
- [Interpretación](references/interpret.md), [validación](references/validate.md), [previsualización local](references/kroki.md)
- [Lente C4](references/lenses/c4.md), [Mermaid C4](references/formats/mermaid-c4.md), [Structurizr C4](references/formats/structurizr-c4.md)
- [Evaluaciones](tests/skill-evals.md) y [contratos automatizados](tests/test_affordances.py)
