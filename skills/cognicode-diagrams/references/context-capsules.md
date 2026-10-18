# M5 — Context Capsules y handoff CogniCode-only

**Disponible:** el agente investigador genera una cápsula pequeña y comprobable desde el ledger derivado. El agente receptor recibe el objetivo, el símbolo/contexto de lenguaje ubicuo DDD, hechos estructurales trazados hasta queries CogniCode, hipótesis diferenciadas, incertidumbres y siguientes preguntas. No recibe una copia del código, no obtiene una autorización de edición y **nunca sustituye CogniCode por lectura directa**.

## Autoridades y política infranqueable

- **Único acceso al código de la aplicación: CogniCode CLI/MCP**, por sus capacidades estructuradas realmente publicadas y probadas para el lenguaje. Nunca `read_file`, `grep`, `find`, `cat`, scripts de lectura, shell, IDE, Git, GitHub source, subagentes lectores ni otros indexadores. Tampoco recorrer el árbol de fuentes; `--repo` es únicamente la identidad opaca del checkout.
- **Fuentes permitidas al proyector:** los objetos bajo HOME derivados de CogniCode: `evidence/claims.json`, `queries.json`, `terms.json` (este último es una propuesta/curación humana, no prueba de implementación). El proyector NO ejecuta CogniCode ni comprueba por sí solo el checkout.
- **Prohibición de fallback:** si la instalación CogniCode no está disponible para el receptor, el estado es `PAUSED_NO_FALLBACK`; no se consulta el proyecto por otros medios. El texto de una cápsula nunca concede permisos de herramientas.
- **Contrato técnico vs significado DDD:** una etiqueta `accepted` acredita lenguaje revisado por curador humano, NO responsabilidad implementada. La identidad estable de código es `symbol_id`; dos contextos homónimos y dos objetivos diferentes producen cápsulas distintas.

## Flujo mínimo — un agente entrega, otro continúa

1. Agente A: investiga **solo con CogniCode**; consolida las entidades/aristas con `claim_id`, `query_id`, `symbol_ids`, `relation_ids`, base y cobertura. Si hay un M4 Change Impact Brief, su contenido se reproyecta desde el ledger, sin depender de su Markdown.
2. Agente A: `context_capsule.py --check` sin escribir; genera JSON/Markdown si aporta valor. El atlas los indexa y la página moldable los enlaza solo cuando siguen siendo actuales respecto al ledger.
3. Agente B: localiza la cápsula por `symbol + context + goal`; ejecuta `--receive`. Eso compara con el **ledger derivado**, detecta corrupción/obsolescencia y devuelve `LEDGER_MATCHES_RUNTIME_UNVERIFIED`, **NO** `VERIFIED`.
4. Agente B: consulta CogniCode instalado para verificar versión e identidad del símbolo (sondeo por lenguaje), investiga solo las incertidumbres necesarias y actualiza el ledger derivado si cambió la evidencia. Si falla CogniCode: PAUSED, sin lectura directa.
5. El agente continúa con trabajo autorizado por el usuario, no porque la cápsula lo autorice. `edit_authorized=false`; el M5 no modifica código.

```bash
# Agente A: preflight sin escritura
python3 scripts/context_capsule.py --repo /raiz/explicita \
  --symbol 'App::StepExecutor' --context orquestacion \
  --goal 'Modificar recuperación sin romper consumidores' --check

# Agente A: empaquetar el mínimo conocimiento
python3 scripts/context_capsule.py --repo /raiz/explicita \
  --symbol 'App::StepExecutor' --context orquestacion \
  --goal 'Modificar recuperación sin romper consumidores'

# Agente B: antes de confiar en un handoff guardado
python3 scripts/context_capsule.py --repo /raiz/explicita \
  --symbol 'App::StepExecutor' --context orquestacion \
  --goal 'Modificar recuperación sin romper consumidores' --receive

# Solo el atlas existente, sin DB adicional
python3 scripts/atlas.py sync --repo /raiz/explicita
```

Salidas en HOME: `handoffs/capsule-<digest>.capsule.json` (agent-first) y `.capsule.md` (novato). Idempotentes, límite aproximado de 12 KB para el JSON compacto, máximo cuatro relaciones entrantes y cuatro salientes en la cápsula. Se conservan los totales y los avisos sobre recorte para no ocultar omisiones. **Ninguna ausencia de aristas observadas prueba que no haya dependencias.**

## Semántica del documento

**Hecho:** arista cuya identidad, extremos y query han pasado la verificación estructurada de `report_thinking.evidence`. **Hipótesis:** un consumidor que podría necesitar revisión, `HYPOTHESIS_NOT_VALIDATED`. **Desconocido:** vigencia, cobertura global, contratos exactos, semántica o runtime que el grafo no demuestra. **Siguiente pregunta:** sugerencia de consulta que el agente debe planificar según las capacidades que **su CogniCode real** exponga; nunca receta para buscar el archivo. Las preguntas no son comandos automáticos.

`evidence.derivation_sha256` es la huella de la **proyección** del informe M4, **NO un commit Git ni la revisión real del checkout**. `evidence.basis` reproduce la identidad declarada por CogniCode si la había. `revision_freshness=UNVERIFIED_WITH_RUNTIME` siempre. La ruta receptora detecta `STALE_DERIVED_EVIDENCE` cuando la explicación guardada ya no coincide con el ledger; incluso si coincide, devuelve `runtime_verified=false` y exige nueva comprobación CogniCode.

## HATEOAS — mismo router

`intent=handoff` acepta `handoff.symbol`, `handoff.goal` (una sola línea y ≤240 caracteres), `handoff.context` opcional, `handoff.phase=sender|receiver`. Las affordances son **enlaces semánticos** con precondiciones, nunca ejecución automática:

- **Emisor:** `inspect-handoff → render-handoff → build-atlas → handoff-capsule` (resultado `PARTIAL`).
- **Receptor:** `inspect-handoff → receive-handoff → revalidate-handoff-via-cognicode → finish` (resultado como máximo `PARTIAL`). Si runtime unavailable ⇒ `BLOCKED`, sin fallback.

Los estados `prepared`, `received`, `render`, `runtime` son **declaraciones observadas por el agente**, no pruebas criptográficas de autenticidad del runtime; la política de herramientas debe restringir físicamente el acceso a checkout. La skill solo restringe la elección de rutas y la validez de las proyecciones. **Los agentes necesitan allowlist efectiva que autorice exclusivamente CogniCode para leer código**. No prometer aislamiento de seguridad a partir de un prompt o de un JSON.

## Integración moldable y atlas

El atlas registra solo cápsulas que pueden reconstruirse byte a byte desde su input derivado; una cápsula obsoleta bloquea el refresco hasta que se regenere. Las fichas contextualizadas anuncian `open-agent-handoff` únicamente para el mismo `symbol_id` y contexto DDD y si el contenido es vigente. Esto no convierte la cápsula en una nueva fuente de verdad ni abre rutas de lectura al proyecto.

## Pruebas y límites

Se mantienen solo regresiones quirúrgicas en la suite ya disponible: límites y símbolos/cuestiones, homónimos, idempotencia, rechazo de archivos ajenos, `--check` sin escrituras, staleness respecto al ledger, atlas, enlaces moldables y HATEOAS sin fallback. UAT real con agentes y CogniCode instalado por lenguaje **pendiente**; no se infiere de los tests sintéticos. La reducción de tokens todavía debe medirse comparando handoff breve con investigación duplicada.

El siguiente trabajo solo debe ejecutarse si añade utilidad real: investigar con un agente A, continuar con B, contar llamadas CogniCode y tokens, comprobar mejora del tiempo a una decisión. No crear orquestador de agentes ni memoria persistente adicional para este hito.