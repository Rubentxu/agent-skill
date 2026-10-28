# Router conversacional y affordances

Entrada JSON para evaluación de **decisiones de la skill**, no un reflejo fiel de la CLI; todas las observaciones provienen del agente anfitrión y requieren corroboración.

```json
{
  "intent":"triage", "basis":"observed", "cli":"available", "project":"initialized",
  "mode":"read", "task":{"id":"TASK-4","isReady":true,"archived":false},
  "config":{"autoCommit":false,"remoteOperations":false,"bypassGitHooks":false,"onStatusChange":false},
  "available_skills":["delivery-first-testing"]
}
```

- `intent`: `discover|capture|triage|refine|plan|execute|verify|close|review|maintain|specify|decompose|sync-specs|catalog`.
- `basis`: `observed|unknown|stale`; `observed` describe evidencias **declaradas**, el router no las verifica.
- `cli`: `available|missing|unknown`; `project`: `initialized|absent|unknown`.
- `mode`: `read|propose|apply` (default `read`). `apply` representa autorización declarada por el llamante, **no ejecuta nada**.
- `task`: `id`, `isReady`, `archived`, `status`, `acceptanceCriteriaCount`, `acceptanceCriteriaCompleted`, `definitionOfDoneCount`, `definitionOfDoneCompleted`, todos opcionales salvo lo que cada fase exige. No adivinar lo no observado.
- `config`: `autoCommit|remoteOperations|bypassGitHooks|onStatusChange`; bool o `null` (desconocido). Otras claves y estados configurables son responsabilidad de la CLI.
- `available_skills`: solo inventario de habilidades confirmado por el anfitrión.

Orden de decisión: validar entrada → resolver capacidades/proyecto → escoger lente → evaluar lectura/propuesta/escritura → riesgos Git/estado → emitir enlaces. Los enlaces a lentes existen dentro de la skill. Para seleccionar candidatos en una instantánea JSON `task-list` ya descargada, usar el helper `ready_candidates.py`: preserva el orden de la CLI, no inventa prioridad y advierte cuando la instantánea puede estar filtrada o paginada. Para la CLI, el router anuncia **comandos de lectura orientativos**, sin ejecutarlos ni construir cadenas de shell a partir de datos del usuario.

Resultados: `DISCOVER`, `INSPECT_MORE`, `READY`, `PROPOSE_ONLY`, `AUTHORIZED_ACTION`, `KEEP_AS_IS`, `BLOCKED`. Ninguno significa `PASS` de tests ni que se haya escrito una tarea. Los cambios de fase y objetivo se reevalúan; no se conserva un estado de conversación en archivos.

## Proyección de roadmaps y especificaciones

`specify` abre la lente para descubrir autoridad documental; `decompose` elige hitos/AC/DoD y prioridades; `sync-specs` reconcilia con el corpus CLI. Los tres producen `plan-spec-projection` pero ninguna escritura. Ver [contrato](spec-contract.md).
