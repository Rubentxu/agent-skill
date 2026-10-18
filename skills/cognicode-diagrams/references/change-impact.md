# M4 — Change Impact Brief: preparar cambios mediante evidencias CogniCode

**Disponible en M4**: `report_thinking.py --kind change-impact` genera un informe JSON agent-first y Markdown para novatos desde el ledger CogniCode ya existente. No ejecuta refactorizaciones, no investiga autónomamente el checkout ni es un análisis de impacto semántico/runtime verificado.

## La pregunta y las fronteras de autoridad

Un agente parte de **una intención concreta del usuario** (`--goal`) y un símbolo identificado exclusivamente por CogniCode (`--symbol`). Nunca se infiere la petición desde una clase ni se afirma que un nombre DDD prueba qué hace el código. `--context` es opcional y ayuda a elegir un término DDD, sin cambiar la identidad técnica.

Separa **cuatro categorías que no se pueden fusionar**:

1. **HECHO ESTÁTICO:** arista estructural, extremos, dirección, claim, query ID y cobertura corroborados por una consulta estructurada de CogniCode. Solo se admiten `graph_edge`; `reference_link` no es una arista.
2. **HIPÓTESIS DE IMPACTO:** una relación entrante señala un posible consumidor que *podría* necesitar revisión. NO demuestra rotura, dependencia funcional en runtime ni cambio de comportamiento.
3. **DESCONOCIDO:** contratos exactos, cobertura global, transitorios/runtime, flujos de error, vigencia del checkout o relaciones no indexadas.
4. **SIGUIENTE CONSULTA:** preguntas delimitadas para que el agente investigue **solo a través de la instalación real de CogniCode CLI/MCP**, descubriendo sus capacidades y verificándolas por lenguaje según `research-protocol.md`. No asumir que todos los lenguajes exponen `analyze_impact` ni construir un grafo por defecto.

No se permite abrir archivos del proyecto mediante read_file, grep, GitHub, terminal, IDE, otro agente o una función de fallback. Los scripts solo leen `~/.cognicode-diagrams/.../evidence` y vocabulario derivado. El argumento `--repo` es identidad explícita del proyecto, no permiso de lectura.

## Ejecución del vertical

Primero usar CogniCode para obtener el `symbol_id`, claims/queries y omisiones pertinentes. Con solo el ledger ya preparado:

```bash
# Preflight seguro: no escribe ni afirma frescura
python3 scripts/report_thinking.py --repo /raiz/explicita \
  --kind change-impact --symbol 'App::Store' \
  --context orquestacion --goal 'Cambiar persistencia sin romper consumidores' --check

# Emitir ambas proyecciones derivadas
python3 scripts/report_thinking.py --repo /raiz/explicita \
  --kind change-impact --symbol 'App::Store' \
  --context orquestacion --goal 'Cambiar persistencia sin romper consumidores'

# Integrar el nuevo informe en el atlas existente
python3 scripts/atlas.py sync --repo /raiz/explicita
python3 scripts/atlas.py check --repo /raiz/explicita

# Volver a crear la página contextual SOLO si interesa tener acceso desde el diagrama
python3 scripts/moldable_views.py --repo /raiz/explicita \
  --symbol 'App::Store' --context orquestacion
python3 scripts/atlas.py sync --repo /raiz/explicita
```

Las salidas tienen nombres estables `reports/change-impact-<digest>.report.json` y `.report.md`. El digest separa **objetivo + contexto + intención**, de modo que dos tareas sobre el mismo símbolo no se sobrescriben. El atlas enlaza los informes existentes y rechaza un Change Impact Brief cuyo contenido ya no coincida con la proyección actual de las evidencias. Una página moldable enlaza el brief solo cuando coincide con su JSON y Markdown generados.

## Qué recibe cada lector

**Agente (JSON):** `kind`, `target_id`, `requested_context`, `language`, `evidence.claim_ids/query_ids/basis/coverage`, `change.goal`, `change.observed_incoming/outgoing`, `change.potentially_affected[]` con estado `HYPOTHESIS_NOT_VALIDATED`, `change.unknowns[]`, `change.next_questions[]` con autoridad `cognicode-only`, `change.readiness` y campos fijos `edit_authorized=false`, `impact_verified=false`.

**Novato (Markdown):** explicación del término en su bounded context cuando está aceptado, símbolo técnico, petición expresamente rotulada como **intención del usuario**, relaciones con flechas y claims, hipótesis de posibles consumidores, incertidumbres y preguntas siguientes. Un cero observado nunca se expresa como «no tiene consumidores»; la cobertura es solo la del ledger. No se calcula una puntuación de riesgo especulativa ni se inventan recomendaciones de pruebas sin investigar los contratos.

**Preparación no es ejecución:** el informe puede evitar lecturas redundantes y orientar el análisis de un agente, pero nunca autoriza editar código ni sustituye una comprobación de contratos y pruebas afectadas. `report_affordances` devuelve `PARTIAL` para el Change Impact Brief incluso si un llamador declara `basis=current`, cobertura verificada y término aceptado: ninguna arista estática demuestra por sí sola el efecto de una modificación.

## Router y diseño moldable

El mismo router existente usa `intent=report` con `report.kind=change-impact`, `report.symbol`, `report.goal` (obligatorio, una sola línea, máximo 240 caracteres), y `report.context` opcional. Enlaces según estado: `inspect-report-evidence → render-report → build-atlas → finish`. **No** añade un router nuevo, una base de datos, un indexador, un plugin MCP ni un harness de tests. Un `prepared=missing|invalid` o una procedencia distinta de CogniCode bloquea; el preflight real es `--check` sobre HOME.

La página moldable existente descubre automáticamente los **briefs ya generados y vigentes** del mismo símbolo y contexto. Si falta el brief, no añade enlace ni intenta fabricarlo. Si cambia el ledger o una definición DDD, no enlaza la versión anterior hasta regenerarla.

## Validación mínima y próximos límites

Regresiones focalizadas: direcciones entrante/saliente acreditadas, hipótesis sin afirmación de fallo, petición separada por objetivo/contexto, ausencia de lectura del checkout, rechazos de goal multilínea y evidencias falsas, frescura en atlas y enlace moldable solo a brief vigente. No introducir una suite E2E/AAT permanente para esta proyección.

**No completado todavía:** UAT contra un CogniCode real por lenguaje; identificación de contratos específicos y trazas runtime; análisis de impacto transitivo; acciones de edición; construcción automática de nuevos queries en base a capacidades descubiertas. La siguiente capa solo tendría sentido si demuestra ahorro de consultas y mejor comprensión en un cambio de producción real.