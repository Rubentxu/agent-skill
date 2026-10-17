# Navegación HATEOAS-like: sesión como recurso, playbooks como enlaces

**Política heredada obligatoria:** toda investigación arquitectónica, incluido el trabajo de subagentes, se realiza exclusivamente mediante CogniCode CLI/MCP. El router opera sobre estados declarados, pero **no atestigua** que una observación provenga de CogniCode: el agente debe conservar queries/claims verificables bajo HOME. [Contrato](investigation-contract.md).

No hay API HTTP, servidor, router de comandos, base de datos ni extensión de CogniCode. Los artefactos de proyecto viven únicamente en el [workspace externo](workspace.md) `~/.cognicode-diagrams`. Antes de cualquier operación que escriba, resolver `workspace=ready`. El agente observa la sesión y elige solo la acción cuyo requisito está acreditado. `rel` expresa intención, `href` referencia una guía local; no equivale a haber ejecutado la acción. El helper puro opcional `scripts/affordances.py` calcula ejemplos de enlaces sin ejecutar tareas.

## Estado efímero de entrada

```json
{
  "workspace": "ready",
  "intent": "create",
  "lens": "c4",
  "formats": ["mermaid", "structurizr"],
  "environment": "mcp_ready",
  "evidence": "graph_ready",
  "evidence_origin": "cognicode",
  "claim_coverage": "partial",
  "detail_requested": false,
  "evidence_insufficient": false,
  "basis": "current",
  "model": "absent",
  "has_input_diagram": false,
  "reconciled": false,
  "artifacts": {"mermaid": "absent", "structurizr": "absent"},
  "validators": {"mermaid": "available", "structurizr": "missing"},
  "approval": {"install": false, "write_project": false}
}
```

- `workspace`: `unknown|absent|incomplete|ready|invalid`. `unknown` ofrece `inspect-workspace`; `absent|incomplete` ofrece `init-workspace`; `invalid` bloquea. Ver [workspace.md](workspace.md). `catalog` y `setup` quedan exentos.
- `intent`: `catalog|setup|scan|discover|create|interpret|translate|review|update|validate|preview|atlas|editorial`.
- `lens`: `id` del registro de lentes. Para `catalog` puede omitirse; las lentes `planned` no se ofrecen para ejecución.
- `environment`: `unknown|missing|cli_ready|mcp_ready|both_ready`. La observación se toma de comandos/calls, nunca de memoria.
- `evidence`: `absent|symbols_ready|graph_ready|partial|stale`; un grafo READY exige consulta posterior que confirme su disponibilidad, no solo un stdout exit 0.
- `basis`: `unknown|current|stale`, **obtenido solo de CogniCode**. Sin él, `unknown`; no usar `git status` ni lectura del checkout.
- `evidence_origin`: `cognicode|unknown|other`. La evidencia ajena a CogniCode no habilita arquitectura.
- `claim_coverage`: `unknown|partial|verified`. `verified` solo tras enlazar **todos** los elementos/aristas con consultas y contrastes de código vía CogniCode.
- `detail_requested` o `evidence_insufficient`: verdadero ⇒ la siguiente affordance de investigación es `query-cognicode` con consulta **nueva**; nunca re-renderizar como sustituto.
- `model`: `absent|draft|reviewed`; `reviewed` significa que el agente comprobó la coherencia indicada, no que el software se haya certificado por magia.
- `artifacts`: por formato `absent|draft|valid|invalid`. `valid` significa que el validador requerido fue realmente ejecutado y pasó.
- `validators`: por formato `available|missing`, comprobado en el sistema actual.
- `approval`: booleans de instalación y escritura; no autoriza por sí sola cambios a CogniCode.

## Previsualización independiente (`intent=preview`)

Ejemplo de estado observado, con imagen pendiente y gateway de Kroki disponible (pero sin Mermaid):

```json
{
  "workspace": "ready",
  "intent": "preview", "lens": "c4", "formats": ["structurizr", "mermaid"],
  "environment": "missing", "evidence": "absent", "basis": "unknown", "model": "absent",
  "artifacts": {"structurizr": "valid", "mermaid": "draft"},
  "validators": {"structurizr": "available", "mermaid": "missing"},
  "kroki": "gateway_ready", "previews": {"structurizr": "absent", "mermaid": "absent"},
  "approval": {"start_kroki": false}
}
```

`kroki=unknown|missing|gateway_ready|full_ready` describe comprobaciones reales. `gateway_ready` permite Structurizr, **no Mermaid**. `full_ready` exige render real de Mermaid+Structurizr. `previews.<formato>=absent|rendered|failed|stale`: se actualiza solamente tras observar resultados. `approval.start_kroki` **no** equivale a autorización para eliminar otro contenedor ni conectar a un servidor público. Ver [kroki.md](kroki.md). El estado `VERIFIED` en esta ruta significa *render local de artefactos sintácticamente validados*, no verificación semántica.

## Atlas transversal (`intent=atlas`)

Para indexar diagramas **ya presentes** en todas las lentes no se necesita un `lens` ni escanear CogniCode. Requiere workspace `ready`, `atlas_assets=present` observado y estados `atlas_source=absent|stale|ready`, `atlas_html=absent|stale|rendered|failed`, `markmap=unknown|missing|ready`, `visual_review=not_run|passed|failed`. Las affordances `build-atlas`, `inspect-markmap`, `render-atlas`, `open-atlas`, `review-atlas` y `finish` se ofrecen según ese estado, con guías en [Markmap](projectors/markmap.md). `atlas.py check` acredita actualización contra **artefactos locales**, no contra el código fuente. Un HTML creado no declara `VERIFIED` antes de una inspección visual real.

## Proyección editorial autodescubierta (`intent=editorial`)

Esta ruta está integrada en el **mismo** `scripts/affordances.py`; requiere `workspace=ready`, `lens=c4` activa y un informe existente de claims/queries CogniCode. La ruta no investiga ni monta el checkout. `prepared=ready` se declara **solo** tras `scripts/editorial.py --check` sobre vista/evidencia derivada, con origen `evidence_origin=cognicode` observado. Estado de ejemplo:

```json
{
  "intent":"editorial","workspace":"ready","lens":"c4",
  "evidence_origin":"cognicode","basis":"current","claim_coverage":"partial",
  "editorial":{
    "view":"context","question_kind":"dependency_structure","pattern":"auto",
    "profile":"default","prepared":"ready","render":"absent",
    "linked":false,"atlas_source":"stale","visual_review":"not_run"
  }
}
```

**Affordances:** `inspect-editorial-evidence` (preflight sin escribir), `render-editorial` (topology/dependencies/traceability, foco y perfil), `link-editorial-atlas` (enlaza los dos assets, sin retocar ledger), `build-atlas`, `open-editorial` (inspección real) y `finish`. Las acciones son **enlaces semánticos**, no comandos ejecutados por el router. Para `render-editorial` usar `scripts/editorial.py` y para `link-editorial-atlas` repetirlo con `--link-atlas` (idempotente). La salida incluye `certification=presentation-only`; `VERIFIED` solo con vista revisada, base actual y cobertura verificada **declaradas**, nunca como certificado que la imagen valide el código por sí sola.

`pattern=auto` selecciona presentación por `question_kind` sin inventar aristas: `dependency_structure/change_impact/collaborators` → `dependencies`; `traceable_decomposition` → `traceability`; el resto → `topology`. Los patrones tienen límites y semántica en [editorial](editorial.md). **No habilita las lentes planned ni nuevos parsers.** Si falta evidencia → solicitar investigación estructurada por CogniCode mediante el router de investigación; nunca usar `read_file(raw)`/GitHub/shell.

## Visores interactivos opcionales (`intent=preview`)

Para mostrar contenido que ya existe en el workspace externo, **sin activar CogniCode ni volver a escanear**, el agente puede elegir `projector=likec4-local` con `formats=["likec4"]` o `projector=structurizr-local` con `formats=["structurizr"]`. Campos observados adicionales:

```json
{
  "intent": "preview", "lens": "c4", "formats": ["likec4"],
  "workspace": "ready", "projector": "likec4-local",
  "projector_status": "ready", "visual_review": "not_run",
  "artifacts": {"likec4": "valid"}, "approval": {"start_projector": false},
  "environment": "missing", "evidence": "absent", "basis": "unknown",
  "model": "absent", "has_input_diagram": false, "reconciled": false
}
```

`projector_status=unknown|missing|stopped|running|ready|failed` sale de la inspección del contenedor y, para `ready`, del HTTP local comprobado. `visual_review=not_run|passed|failed` solo lo actualiza el agente **después de inspeccionar la vista**. `ready` sin revisión visual no cierra el ciclo; `start-projector` requiere `approval.start_projector=true`. `open-projector` solo ofrece una guía al agente; no afirma que el navegador se abrió realmente. La ruta anterior de Kroki se conserva como `projector=kroki-local` por defecto. No se soporta proyectar LikeC4 a través de Kroki. Ver [proyectores](projectors.md).

## Semántica de las acciones

`inspect-workspace`, `init-workspace`, `inspect-environment`, `install-cognicode`, `scan-symbols`, `build-graph`, `query-cognicode`, `interpret-input`, `discover-model`, `review-model`, `reconcile`, `render-mermaid`, `render-structurizr`, `validate`, `inspect-kroki`, `start-kroki`, `start-mermaid-companion`, `preview-mermaid`, `preview-structurizr`, `finish`, `inspect-projector`, `start-projector`, `open-projector`, `review-layout`, `build-atlas`, `inspect-markmap`, `render-atlas`, `open-atlas`, `review-atlas`, `inspect-editorial-evidence`, `render-editorial`, `link-editorial-atlas`, `open-editorial`, `review-editorial`. Para `catalog`, `list-lenses`. Para una lente no disponible, `UNSUPPORTED` con razón; no se suplanta por C4.

A continuación de cada acción, observar si ha funcionado y actualizar **en la conversación** los campos realmente cambiados. Evitar ejecutar el mismo paso sin que cambie alguna precondición. El agente puede saltarse el helper y aplicar estas normas directamente.

## Reglas de cierre

- `VERIFIED`: alcance comprobado; para fidelidad arquitectónica requiere claims contrastados con **CogniCode** y `claim_coverage=verified`. En `preview/translate` solo certifica el formato/visor, nunca la implementación.
- `PARTIAL`: diagrama entregable, pero falta revisión de modelo, validador o datos suficientes; no afirmar PASS.
- `BLOCKED`: hace falta instalación/permisos/entrada y no se dispone de ello.
- `FAILED`: un validador o contrato ha demostrado un fallo.
- `UNSUPPORTED`: lente deshabilitada o salida semántica imposible para el formato solicitado.

Para cambios de código o diagramas, no prometer equivalencia si el SHA o los archivos observados cambiaron desde el escaneo. En trabajos centrados exclusivamente en la traducción entre formatos, CogniCode puede no intervenir: identificar el alcance de esa validación.


## Gate de investigación por pregunta (precede a dibujar)

Para `intent=discover|create|review|update`, el estado incluye `research` con pregunta, catálogo observado, prueba por lenguaje, consultas y claims (ver [research-protocol.md](research-protocol.md)). Sin él, el router devuelve `formulate-question`; `graph_ready` y `claim_coverage=verified` no bastan.

`
formulate-question -> discover-capabilities -> probe-capability -> query-structured
                    -> justify-claims (solo si falta evidencia)
                    -> EVIDENCE_READY (sin más consultas) / PARTIAL (parar)
`

Son **acciones semánticas** que el agente implementa exclusivamente llamando a capacidades reales de CogniCode; no son nombres de comandos inventados. `probe-capability` prueba cada lenguaje sobre símbolo real. No seleccionar por conteo de herramientas. `read_file(raw)` como bypass bloquea la investigación; `search_content` solo puede ubicar candidatos, nunca fundar arquitectura. La proyección seguirá necesitando validación independiente de formato y plano.

## Preconditions del cierre arquitectónico

`research.scope` exige el inventario de omisiones de CogniCode y la matriz `capabilities[].probes[lenguaje]`. Los enlaces `assess-coverage` y `assess-omissions` solicitan acciones del runtime descubierto, **no comandos inventados**. Con ficheros omitidos relevantes/indeterminados no se habilita la vista como implementada. Una vista acotada con omisiones justificadas conserva el estado `PARTIAL` si `scope.coverage=partial`.

## Nuevas affordances del preflight

`preflight-language` consulta soporte en el runtime instalado antes de C4; `inspect-session` identifica grafo/proceso; `build-graph` se ofrece por requisito real `requires_graph`, nunca por ausencia global de capacidades; `plan-view` obliga a registrar cantidad de nodos y `split-view` evita diagramas ilegibles. El helper sigue siendo puro, no conecta a CogniCode.

## Report Thinking — ruta moldable disponible (`intent=report`)

El **mismo router** admite `intent=report` con `report.kind=term-card|symbol-passport` y requiere `workspace=ready`. Campos de identidad: `term-card` exige `context` y `term`; `symbol-passport` exige `symbol` y admite `context` opcional. Los estados se observan y actualizan tras acciones reales: `prepared=unknown|ready|missing|invalid`, `render=absent|ready|stale|invalid`, `atlas_source=absent|stale|ready` y `language_status=unknown|candidate|accepted|disputed|deprecated|unmapped`.

Affordances ejecutables: `inspect-report-evidence` → `render-report` → `build-atlas` → `finish`. El primer paso guía `scripts/report_thinking.py --check` (valida el ledger HOME, sin escrituras); el segundo produce JSON/Markdown; el tercero `scripts/atlas.py sync` registra las fichas en el atlas actual. Todo el proceso es exclusivamente una **proyección**, no una consulta autónoma a CogniCode ni una certificación de código. Procedencia ajena a CogniCode, workspace inseguro y falta de evidencia **bloquean**, sin fallback de lectura. [Ejemplos y contratos](report-thinking.md).

Las futuras `get-brief`, `inspect-evidence`, `expand-context`, `render-view` y `propose-term` pertenecen al roadmap [Moldable Knowledge](moldable-knowledge.md); **aún no figuran en `LINKS` ni están implementadas**.

## Navegación moldable por símbolo (`intent=moldable`, M3 disponible)

El router HATEOAS existente admite `intent=moldable` con `moldable.symbol` (identidad CogniCode) y `moldable.context` opcional. Pasos observables: `inspect-moldable` (`scripts/moldable_views.py --check`) → `render-moldable` (HTML/JSON contextual, solo HOME) → `build-atlas` → `open-moldable` → `finish`. No anuncia un diagrama no generado ni usa documentación, nombres o `grep` como evidencia. `prepared=ready` **no** suplanta la procedencia CogniCode, solo habilita la proyección. [Contrato M3](moldable-navigation.md).
