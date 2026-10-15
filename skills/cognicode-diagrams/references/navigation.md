# Navegación HATEOAS-like: sesión como recurso, playbooks como enlaces

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
- `intent`: `catalog|setup|scan|discover|create|interpret|translate|review|update|validate|preview`.
- `lens`: `id` del registro de lentes. Para `catalog` puede omitirse; las lentes `planned` no se ofrecen para ejecución.
- `environment`: `unknown|missing|cli_ready|mcp_ready|both_ready`. La observación se toma de comandos/calls, nunca de memoria.
- `evidence`: `absent|symbols_ready|graph_ready|partial|stale`; un grafo READY exige consulta posterior que confirme su disponibilidad, no solo un stdout exit 0.
- `basis`: `unknown|current|stale`. Un SHA sin conocer `dirty` y cobertura no demuestra vigencia.
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

## Semántica de las acciones

`inspect-workspace`, `init-workspace`, `inspect-environment`, `install-cognicode`, `scan-symbols`, `build-graph`, `interpret-input`, `discover-model`, `review-model`, `reconcile`, `render-mermaid`, `render-structurizr`, `validate`, `inspect-kroki`, `start-kroki`, `start-mermaid-companion`, `preview-mermaid`, `preview-structurizr`, `finish`. Para `catalog`, `list-lenses`. Para una lente no disponible, `UNSUPPORTED` con razón; no se suplanta por C4.

A continuación de cada acción, observar si ha funcionado y actualizar **en la conversación** los campos realmente cambiados. Evitar ejecutar el mismo paso sin que cambie alguna precondición. El agente puede saltarse el helper y aplicar estas normas directamente.

## Reglas de cierre

- `VERIFIED`: artefactos presentes con validaciones realmente ejecutadas y modelo revisado; declarar en la respuesta el **alcance de la verificación**, que puede ser solo formato si se traduce un archivo sin código.
- `PARTIAL`: diagrama entregable, pero falta revisión de modelo, validador o datos suficientes; no afirmar PASS.
- `BLOCKED`: hace falta instalación/permisos/entrada y no se dispone de ello.
- `FAILED`: un validador o contrato ha demostrado un fallo.
- `UNSUPPORTED`: lente deshabilitada o salida semántica imposible para el formato solicitado.

Para cambios de código o diagramas, no prometer equivalencia si el SHA o los archivos observados cambiaron desde el escaneo. En trabajos centrados exclusivamente en la traducción entre formatos, CogniCode puede no intervenir: identificar el alcance de esa validación.
