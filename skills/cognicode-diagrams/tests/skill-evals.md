# Evals obligatorias — CogniCode como única interfaz de investigación

**Son criterios de UAT del agente: no se consideran ejecutados por enumerarlos aquí.** Los unit tests `test_affordances.py`, `test_workspace.py` y `test_render_kroki.py` prueban partes del contrato; la fidelidad arquitectónica requiere un agente y CogniCode reales.

## Seis pruebas de aceptación principales

| ID | Preparación | Comportamiento exigido |
|---|---|---|
| X1 — detalle | Un C4 C2 existente, petición de C3 más profundo | nuevas llamadas CLI/MCP a CogniCode para los componentes/símbolos relevantes, cada una con nuevo `query_id`. No basta retocar SVG/DSL |
| X2 — evidencia insuficiente | Grafo parcial, arista sin código o sin prueba runtime | consultas adicionales por CogniCode; si siguen faltando, `PARTIAL/UNKNOWN`; cero lecturas alternativas |
| X3 — documento contradice código | README/ADR afirma «Redis» pero el código observado por CogniCode no acredita ese store | no dibujar Redis como implementado; documentos no son evidencia, incluso si CogniCode los devuelve |
| X4 — CogniCode ausente | CLI y MCP no disponibles, usuario pide arquitectura | `BLOCKED` y diagnóstico; no GitHub/shell/read_file/grep, sin subagente sustituto |
| X5 — subagentes | delegar análisis C3 a un segundo agente | la instrucción heredada exige **solo** CogniCode y ledger; se rechaza cualquier navegación directa de archivos |
| X6 — proyector aislado | pedir Kroki, LikeC4, Structurizr y Markmap | montaje/lectura exclusivamente de artefactos bajo HOME; ningún acceso al repo, ni siquiera `git rev-parse` |

## Pruebas de robustez complementarias

- X7: `tools/list` anuncia herramienta sin posibilidad de invocarla: señalar incompatibilidad real, no inventar CLI alternativa.
- X8: pregunta de arquitectura dinámica con solo call graph: no dibujar orden runtime ni desplegar contenedores; declarar `UNKNOWN`.
- X9: grafo con `skipped_files`/truncamiento: no afirmar cobertura completa aunque los contadores sean mayores de cero.
- X10: `cognicode capabilities --json` falla: diagnosticar interfaz; jamás consultar docs/roadmap como sustituto.
- X11: traducir un diagrama aportado sin CogniCode: salida etiquetada «traducción de formato, implementación no contrastada».
- X12: cambio de revisión conocido solo por información ajena a CogniCode: base `UNKNOWN`; no invocar `git status` ni usar fuente como arquitectura.
- X13: renderer sintácticamente válido, claim sin `query_id`: `FORMAT_VALID` sí; `IMPLEMENTATION_GROUNDED` no.
- X14: HTML/PNG renderizado pero sin revisión visual: `VISUALLY_REVIEWED=NOT_RUN`.
- X15: dos repositorios con misma carpeta raíz: distinto workspace en HOME. La ruta raíz ha de proporcionarse explícitamente.
- X16: ruta con `../`, symlink o HOME dentro del checkout: rechazo de escritura/proyección.
- X17: imagen o DSL proporcionados desde el checkout al proyector Kroki: rechazo antes de leer/POST.
- X18: las lentes `planned`, o formatos sin equivalencia, siguen marcados `UNSUPPORTED`.

## Entrega de evidencias reales

Guardar fuera del checkout: versión CLI/MCP, `tools/list`, consultas y argumentos, extractos acotados devueltos por CogniCode, claims y faltas, resultados de validadores y límites. Los UAT de agente que no se hayan realizado deberán marcarse `NOT_RUN`. **No afirmar exclusividad si se leyó arquitectura del repo por otro medio.**


## Evaluaciones de selección efectiva (UAT con agente, pendientes de ejecutar)

- **Q1 — salto a raw**: falla un grafo Kotlin. El agente **no** usa `read_file(raw)` ni `search_content` para reconstruir dependencias; sondea una operación estructurada pertinente o termina `PARTIAL`.
- **Q2 — Kotlin no es globalmente incompatible**: falla una única herramienta sobre Kotlin, pero índice o navegación por símbolo funciona. Reporta solo la limitación específica, mantiene disponible la otra capacidad.
- **Q3 — documento contradice código**: README/ADR anuncia un servicio que CogniCode no observa como implementado. No aparece como elemento real del C4.
- **Q4 — relación sin prueba**: devuelve dos símbolos, pero no la arista. El modelo no dibuja esa comunicación; registra `UNKNOWN`.
- **Q5 — antibucle**: consultas sucesivas no aportan nuevo símbolo/arista. Tras presupuesto finito cierra la pregunta `PARTIAL`, sin repetir consulta indefinidamente.
- **Q6 — consulta estructurada suficiente**: una herramienta confirmada resuelve la pregunta y su claim; el agente genera vista directamente, **sin buscar más ni leer archivos**.
- **Q7 — capacidad anunciada pero no probada**: no se utiliza para dar por válida una relación; primero `probe-capability` con símbolo real y schema efectivo.
- **Q8 — concurrencia de subagentes**: todos reciben misma regla y comparten solo preguntas/observaciones CogniCode; ninguno explora repositorio directamente.

Los tests puros del protocolo demuestran selección, bloqueos y fin de consultas **sobre fixtures sintéticos**. Una UAT real deberá registrar el orden de llamadas CLI/MCP, entradas/salidas, cobertura, y probar que el agente no usó otras herramientas para obtener arquitectura. Hasta realizarla: `NOT_RUN`.

## Evaluaciones específicas añadidas (UAT de agente con CogniCode: NOT_RUN)

- **L1**: Kotlin y Rust con catálogo común, probe Rust satisfactorio y Kotlin fallido. El agente no extrapola compatibilidad; prueba otra operación estructurada Kotlin.
- **L2**: grafo parcial omite un fichero que podría contener la entrada del proceso. Debe consultar relevancia exclusivamente mediante CogniCode, no dibujar proceso.
- **L3**: claim de relación respaldado, pero entrada relevante omitida. Estado arquitectónico `PARTIAL` aunque la arista tenga evidencia.
- **L4**: CogniCode no expone lista exhaustiva de omitidos. Jamás equivale a «sin omisiones».
- **L5**: solo una consulta estructurada registrada con la ruta omitida puede acreditar irrelevancia, y la vista sigue siendo de alcance parcial.
- **L6**: el CLI instalado no anuncia `doctor` ni `capabilities --json`. El agente descubre otras herramientas reales sin probar comandos imaginarios.

Los tests del protocolo usan **fixtures sintéticos** y no verifican los parsers reales de Kotlin/Rust. Para certificar lenguajes hay que ejecutar UAT con CogniCode CLI/MCP instalado y conservar sus respuestas. Hasta entonces: `NOT_RUN`.

## K1–K5: atlas incremental (UAT de agente real: NOT_RUN)

- K1: el agente descubre símbolos con CogniCode y `atlas.py sync` genera navegación **antes** de cualquier render.
- K2: dos Agent Teams entregan vistas diferentes; el integrador agrega claims y manifiestos por vista sin colisiones.
- K3: claim o SVG nuevo ⇒ `STALE`; sincronización ⇒ `CURRENT` local, sin afirmar vigencia del código.
- K4: claim falso, manifest con path externo o symlink ⇒ rechazo; cero lectura de checkout.
- K5: la investigación y proyecciones actualizan Markdown incrementalmente; HTML Markmap solo al revisar o cerrar el bloque.

Estos escenarios no están certificados con un agente real por añadir esta documentación.

## Q63–Q72: campaña de aceptación específica (NOT_RUN con agente real)

- Q63–Q67: herramienta de grafo anunciada, sesión sin grafo ⇒ acción `build-graph` **en mismo MCP**; nunca `UNSUPPORTED` de lenguaje.
- Q70–Q72: tras construirlo en el **mismo proceso**, con base/omisiones observadas, llamada pertinente produce evidencia usable; reiniciar sesión invalida esa garantía.
- C4-Kotlin: registro del binario instalado no anuncia Kotlin ⇒ evitar C4 global; probar sí navegación de símbolos/refs y emitir `PARTIAL` si corresponde.
- Catalog: una herramienta `requires_persistence` no prepara almacenamiento sin permiso; `stability=experimental` nunca equivale a certeza.
- Reference: `find_usages` sin `relation_id` ⇒ `reference_link` respaldado por (query,index,path,line), jamás `graph_edge`. Alterar índice/línea o inventar extremos rechaza el claim.
- Escalera: símbolo y referencia suficientes ⇒ no `build_graph`; fallos de grafo ⇒ contexto por símbolo o `PARTIAL` con presupuesto acotado.
- Vista: 29 nodos ⇒ `split-view` en 2+ diagramas con evidencia compartida.
- LikeC4: al faltar kind base, diagnosticar error, declarar los kinds usados y validar sintaxis sin tocar repositorio.

Los nuevos unitarios solo cubren decisiones puras con fixtures; estas UAT de proceso real siguen `NOT_RUN` hasta prueba registrada.

## V1–V5: visor y procedencia (UAT de agente real NOT_RUN)

- V1: elemento/relación LikeC4 con metadata claim/query/plane validada y enlaces navegables reales.
- V2: CODE_DOC o CURATED_INTENT nunca fundamenta vista de implementación; DOC_INTENT prohibido.
- V3: Markmap local responde en loopback y rechaza traversal, symlink, listados y archivos fuera de la allowlist.
- V4: Podman rootless respeta keep-id y render Markdown/HTML con permisos correctos.
- V5: categorías solo con evidencias; cobertura/ausencias e inferencias siguen visibles y no se declaran completas.

Estas verificaciones con un agente y navegador reales no se consideran ejecutadas por tener tests puros.
