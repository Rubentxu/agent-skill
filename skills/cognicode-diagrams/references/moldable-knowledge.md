# Moldable Knowledge — lenguaje compartido para personas y agentes

> **Estado mixto:** M1 (Term Card) y M2 (Symbol Passport JSON/Markdown con router e integración al atlas) **implementados** en [Report Thinking MVP](report-thinking.md). La **navegación contextual por símbolo M3** ya está implementada en [moldable-navigation.md](moldable-navigation.md), con enlaces salientes a fichas y diagramas existentes. Los nodos SVG con ficha moldable actual ofrecen enlace inverso y etiqueta DDD contextual; sin ficha, no se inventa un enlace. Las búsquedas moldeables dinámicas y secuencias pedagógicas siguen **planificadas**. **M5 Context Capsules y handoff implementados** para traspaso compacto con revalidación CogniCode obligatoria, sin certificación de código real ([contrato M5](context-capsules.md)). **M4 Change Impact Brief ya está implementado** como proyección acotada de relaciones estáticas e hipótesis, no como evaluación runtime ni autorización de edición ([contrato M4](change-impact.md)). No anunciar como ejecutables enlaces `rel` futuros.

## Tesis: entender juntos el mismo objeto

Un agente y una persona deben poder examinar **el mismo objeto de conocimiento**, con la misma identidad de símbolo, evidencias, alcance, lenguaje de dominio y limitaciones; cada audiencia consume una presentación apropiada. La diferencia no reside en los hechos sino en su **representación** y en la profundidad de explicación.

- **CogniCode es el único lector/analizador del checkout.** El agente, subagentes, proyectores y scripts NO abren, recorren, buscan ni leen código, documentos, tests, config, Git o GitHub del proyecto objetivo. La ruta `--repo` se usa solo como identificador opaco del workspace.
- **Ledger único existente**: `evidence/queries.json` y `evidence/claims.json`, con identidades de revisión y cobertura cuando CogniCode las suministra. No crear otra base de datos, otro grafo, índices, embeddings ni daemon en esta skill.
- **Un objeto, varias proyecciones**: representación JSON compacta para el agente, ficha en lenguaje claro/Markdown para la persona, diagrama HTML/SVG/Markmap cuando el problema lo requiera. Ninguna vista se utiliza como evidencia de otra vista.
- **Pensamiento moldable**: al enfocar un símbolo, claim, informe, contexto o pregunta, mostrar solo las vistas, búsquedas y acciones que pueden responder a la necesidad actual. Si faltan datos, anunciar qué pregunta pertinente puede realizarse exclusivamente mediante CogniCode.

Inspiración: [Glamorous Toolkit y Moldable Development](https://gtoolkit.com/), sus patrones [Contextual View / Contextual Action / Contextual Search](https://book.gtoolkit.com/moldable-development-patterns-vuflnrgp5r5o4m1szatoo4e2) y el [Ubiquitous Language](https://martinfowler.com/bliki/UbiquitousLanguage.html) de DDD. No adoptar Smalltalk, GT, sus scripts, su agente ni un IDE nuevo: adaptar el **principio**, no copiar la plataforma.

## 1. Lenguaje ubicuo **por contexto**: la bisagra semántica

La ontología técnica y el lenguaje humano **no son equivalentes**. Un nombre de clase, un símbolo o una comunidad detectada por algoritmo no demuestran por sí solos un concepto de negocio ni un bounded context DDD. Un término puede tener significados distintos en contextos distintos; no aplanarlos en un glosario universal.

Modelo mínimo de una **ficha terminológica** (propuesta, no nuevo claim de implementación):

| Campo | Significado | Fuente / autoridad |
|---|---|---|
| `term_id` | Identificador estable del término **en un contexto** | Registro de vocabulario derivado |
| `context_id` | Frontera de lenguaje donde el término es válido | `proposed` por agente, `confirmed` por persona/evidencia pertinente; nunca deducir DDD de carpetas |
| `label` | Nombre en castellano sencillo, **sustantivo o verbo preciso** | Propuesta del agente o validación de usuario |
| `definition` | Qué significa, en una frase entendible sin conocimientos técnicos | Separar lo demostrado de interpretación |
| `not_this` | Qué **no** significa; evita homónimos y ambigüedad | Confirmado o propuesto con etiqueta |
| `aliases` | Denominaciones y traducciones permitidas en ese contexto | No fusionar significados distintos |
| `symbol_ids` | Identidades **exactas** dadas por CogniCode | `claim_ids` y `query_ids` que vinculan símbolos |
| `status` | `candidate | accepted | disputed | deprecated` | `accepted` requiere confirmación de un humano del dominio o autoridad identificada |
| `coverage` / `basis` | Alcance, omisiones y versión conocida | CogniCode; si falta, `UNKNOWN` |
| `curator` | Autor de aceptación/rechazo, sin información privada innecesaria | Solo cuando ha habido decisión explícita |

Ejemplo **sintético y no corroborado**: término `Ejecución de paso` en contexto `Orquestación`, propuesta para `StepExecutor`. Explicación para novatos: «coordina la ejecución de una tarea concreta»; detalle técnico opcional: símbolo completo, relaciones confirmadas y queries. Si `StepExecutor` únicamente es nombre de clase pero no se ha demostrado esa responsabilidad, registrar `definition_status=candidate` y **no** presentarla como hecho.

**Norma anti-falsa ubicuidad**: el agente sugiere, contrasta uso técnico **a través de CogniCode**, detecta ambigüedad y propone preguntas simples («¿Aquí “ejecución” significa iniciar una tarea o registrar su resultado?»). El experto/persona **decide** el significado del dominio. La aprobación cambia solo el vocabulario, no la realidad observada. No obligar a revisar cada nombre técnico para mostrar un primer informe; las propuestas quedan marcadas como provisionales.

No almacenar semántica de negocio como `OBSERVED_CODE` por el mero hecho de que una clase se llame parecido. Una definición curada ocupa plano `intent`; las identidades y relaciones técnicas pertenecen a `static`. La vista puede **enlazar** ambos planos con atribución, sin convertir uno en prueba del otro.

## 2. Gramática didáctica que usarán TODOS los informes y diagramas

Cada objeto importante ofrece, cuando existe evidencia, la misma **ficha de significado**:

1. **Cómo lo llamamos** — etiqueta ubicua y contexto; si es propuesta, mostrar «nombre pendiente de validar».
2. **Qué es** — una frase sencilla, sin jerga ni clase como definición.
3. **Para qué sirve / por qué importa aquí** — tarea o responsabilidad observada, o hipótesis marcada.
4. **Con qué se relaciona** — 1–3 relaciones importantes; etiqueta exacta del tipo de relación. Una llamada estática NO es ejecución temporal.
5. **Cómo lo sabemos** — `claim_ids`, `query_ids`, símbolo y cobertura; desplegables en UI, accesibles íntegros en JSON.
6. **Qué desconocemos** — una limitación, ausencia de runtime, omisiones o frescura `UNKNOWN`.
7. **Qué preguntar después** — affordances disponibles; si no hay más acciones seguras, `finish`.

Reglas editoriales: lenguaje castellano de España, frases cortas, metáforas solo si se aclaran sus límites, **un concepto por tarjeta**, glosario contextual al lado del contenido (no anexo gigante), acrónimos desarrollados en su primera aparición, distinción visible `HECHO / INTERPRETACIÓN / DESCONOCIDO`, no usar solo colores. El informe breve agente comparte la semántica pero evita prosa ornamental; la UI humana puede ampliar las mismas tarjetas.

El diagrama debe mostrar `label` amigable **y** permitir recuperar `symbol_id` exacto en metadatos; no renombrar realmente clases, paquetes o IDs. Si `context_id` no está confirmado, usar nombre técnico con explicación contextual provisional. Las etiquetas muy largas no obligan a introducir más nodos: reutilizar la regla de división de vistas.

## 3. Moldable Objects: contexto antes que catálogo de diagramas

| Objeto seleccionado | Pregunta frecuente | Vista contextual reutilizable | Acción contextual, solo si autorizada |
|---|---|---|---|
| **Aplicación / ámbito** | «¿Por dónde empezar?» | `Architecture Brief`, mapa de entradas y huecos | `explore-entry-points` |
| **Símbolo** | «¿Qué hace realmente?» | `Symbol Passport` + vecinos demostrados | `inspect-consumers`, `explain-claim` |
| **Término de dominio** | «¿Qué significa aquí?» | `Term Card`, alias y contextos con homónimos | `propose-definition`, `request-curator-review` |
| **Cambio pretendido** | «¿Qué puede romperse?» | `Change Impact Brief`, dependencias y riesgos pendientes | `query-impact`, `prepare-change` |
| **Afirmación (claim)** | «¿Por qué lo dice?» | Prueba, plano, operación CogniCode y límites | `inspect-evidence` |
| **Ausencia o contradicción** | «¿Qué falta por comprobar?» | `Knowledge Gaps` / `Evidence Reconciliation` | `refresh-evidence` o `finish-partial` |

**Moldable View** = una perspectiva barata del objeto. **Moldable Search** = una pregunta focalizada autorizada a CogniCode, no `grep`. **Moldable Action** = siguiente relación HATEOAS, no un ejecutor oculto de comandos. El router decide qué ofrecer **según estado y precondiciones reales**, no por hardcodear todos los comandos CogniCode ni activar miles de herramientas.

Una pregunta nueva sin instrumento pertinente no obliga a programar un proyector permanente: primero consulta existente → informe/tabla puntual → propuesta de `microview` efímera si facilita la decisión. **Promocionar** una microview a formato reusable solo si resuelve preguntas repetidas y tiene contrato mínimo. El agente no ejecuta código generado para investigar el checkout; cualquier herramienta contextual nueva solo interpreta **evidencias ya producidas por CogniCode**.

## 4. Report Thinking: contrato de proyección único

**Implementado en el MVP**: `intent=report` en el router puro existente; `report` es una **presentación**, no una nueva lente de análisis. La lente/tema de pregunta y la proyección son dimensiones independientes; una misma investigación puede ofrecer `brief.json`, `brief.md`, `diagram.svg`, `atlas.html`. Todos comparten `claim_ids`, `query_ids`, `term_ids` y versión de evidencia, sin duplicar los datos como autoridad nueva.

Esquema ilustrativo conceptual de futuras ampliaciones, **no equivale al contrato exacto implementado** (véase [report-thinking.md](report-thinking.md)):

```json
{
  "schema": "cognicode.report/v1",
  "kind": "symbol-passport",
  "target": {"symbol_id": "Example::StepExecutor"},
  "language": {
    "context_id": "orchestration",
    "term_id": "orchestration.step-execution",
    "label": "Ejecución de paso",
    "status": "candidate"
  },
  "explanation": {
    "what": "Coordina la ejecución de un paso (hipótesis pendiente)",
    "why": "Pendiente de confirmar mediante CogniCode",
    "knowledge_status": "INFERRED"
  },
  "evidence": {
    "claim_ids": [],
    "query_ids": [],
    "basis": "UNKNOWN",
    "coverage": "unknown"
  },
  "next": [{"rel": "query-symbol-context", "requires": "cognicode-runtime"}]
}
```

La ausencia de claims **impide** anunciar la definición como comprobada. Nunca incluir un `source_path` como autorización implícita para abrirlo; las rutas son **referencias emitidas por CogniCode**.

**Coste progresivo** (presupuestos iniciales revisables, no límites fijos): `microbrief` de 150–300 tokens → `task-brief` de 500–1000 → `deep` por demanda. El router empieza con el más económico capaz de responder. Si se pide visual thinking, reutiliza claims/terms para C4/Markmap sin consultas redundantes. Los textos pueden cambiar; IDs y hechos corroborados no.

## 5. Contextual narratives: recorrido pedagógico y handoff

Un `Knowledge Journey` sería una **secuencia de preguntas y vistas enlazadas**, no un manual inventado por el LLM ni un grafo nuevo: por ejemplo «qué es un step → quién lo invoca → qué sucede si falla → qué está sin comprobar». Cada paso describe un único concepto, con enlace a términos, claims y próxima consulta.

- **Persona principiante**: vista «Qué es / Ejemplo / Para qué / Qué no sabemos / Ver más». Un ejemplo ilustrativo se rotula `SYNTHETIC` y jamás se confunde con producción.
- **Agente**: mismos términos e IDs en cápsula compacta `task, context, evidence, unknowns, next`. Un handoff no certifica la revisión actual, debe reevaluar `basis` mediante CogniCode cuando importe.
- **Humano experto**: misma ficha, detalle de queries, relaciones, límite y planos.
- **Preguntas de validación del lenguaje**: el agente formula opciones claras cuando haya polisemia; nunca fabrica una aprobación humana.

Inspirarse en `Example Object` y `Defined/Dynamic Narratives` de Moldable Development, pero **no obligar a construir un test ni ejecutar un harness** por cada tarjeta. Ejemplos del dominio solamente a partir de evidencias o ejemplos expresamente sintéticos.

## 6. Navegación progresiva, coste y autoridad

Ruta de ejemplo **planificada**:

`observe-context → select-question → discover-cognicode → query-evidence → propose-term → project-report → (inspect-evidence | render-view | expand-context | finish)`.

- `inspect-evidence`, `expand-context` y `refresh-evidence` solo hacen nueva consulta si lo existente no basta. No mantener el ciclo abierto para producir más contexto.
- `propose-term` puede ofrecerse con datos parciales, pero el router no lo convierte automáticamente en `accepted`.
- `render-view` es puro frente a repositorio, solo lee artefactos derivados. Se reutiliza atlas actual: `objeto → término → claim → query → report/diagram`; el término aprobado es una **asociación de vocabulario**, no una arista arquitectónica.
- Un `status=VERIFIED` **se refiere únicamente a lo corroborado en ese alcance/revisión**. `PRESENTATION_READY` y `LANGUAGE_ACCEPTED` son certificados distintos.
- Nunca instalar GT, generar servidores, crear MCP nuevo ni insertar un control plane donde ya funciona CogniCode. No hacer `build_graph` por defecto. No inventar instrumentos de inspección runtime que CogniCode no ofrezca.

## 7. Roadmap de producto — sin segundo motor ni harness

| Hito | Valor entregable | Prueba mínima / cierre |
|---|---|---|
| **M0 — Higiene** | Retirar skill obsoleta `cognicode-quality-investigator` y rutas de catálogo; conservar las skills independientes instalables | Validador del repositorio y sin enlaces rotos |
| **M1 — Term Card (implementado)** | Un `term_id` contextual desde vocabulario externo y claims existentes; etiqueta para principiante | Dos contextos con mismo término quedan separados; candidato nunca aparece como aprobado |
| **M2 — Symbol Passport (implementado, UAT real pendiente)** | `intent=report` devuelve JSON agent-first y Markdown humano con mismos IDs/evidencias | Unit tests sobre ledger sintético; ejecutar UAT CogniCode real por lenguaje antes de afirmar compatibilidad |
| **M3 — Contextual View (implementado, UAT visual real pendiente)** | Desde un símbolo abrir informes/diagramas/evidencia y volver desde los nodos SVG con ficha vigente, con nombres DDD contextuales | Pruebas de ida/vuelta, términos ambiguos y rechazo de enlaces caducados; UAT visual real pendiente |
| **M4 — Change Impact Brief (implementado, UAT real pendiente)** | Informe JSON/Markdown sobre la intención del usuario, relaciones entrantes/salientes corroboradas, hipótesis y preguntas CogniCode; accesible desde atlas y moldable view | Pruebas focalizadas sin falsear fallos; medir utilidad en cambio real con UAT efímero, seguir en `PARTIAL` ante impacto no demostrado |
| **M5 — Context Capsules y handoff (implementado, UAT agentes real pendiente)** | Cápsulas JSON/Markdown con contexto DDD, hechos corroborados y preguntas; receptor compara ledger y **revalida por CogniCode real**, nunca directamente el checkout | Pruebas de stale, fuente exclusiva, cobertura y HATEOAS; medir ahorro de tokens y llamadas con dos agentes reales |

El primer entregable útil es **una ficha humana + microbrief para agentes con una misma `term_id`**, no una plataforma de modelado nueva. Tras cada bloque, integrar y entregar, UAT/e2e/AAT efímeros que aporten valor y retirar lo no reusable. La calidad se mide con: comprensión por principiantes, exactitud factual, consultas efectivas, ahorro de tokens, ausencia de `read_file/grep`, frescura y tiempo hasta una decisión útil.

## 8. Anti-patrones, para no degenerar

- **Glosario mágico**: inferir términos de negocio por nombre de clase/paquete o por clusters detectados.
- **Renombrado silencioso**: mostrar etiqueta amigable como sustituta de `symbol_id` o cambiar implementación sin aprobación.
- **Lenguaje único de toda la empresa**: ignorar bounded contexts, polisemia o fronteras aún no demostradas.
- **Report-factory**: generar seis informes de la misma pregunta porque existen plantillas.
- **HATEOAS de escaparate**: ofrecer acciones sin herramienta, versión, permiso ni precondición observada.
- **Moldable = scripts arbitrarios**: ejecutar snippets externos sobre el checkout o conceder nuevas lecturas al LLM.
- **Harness antes que valor**: crear tests, UAT y snapshots permanentes por cada variación estética sin garantía nueva.
- **DDDesign por decreto**: no afirmar `bounded context`, agregado ni evento de dominio por proximidad física en un grafo.
