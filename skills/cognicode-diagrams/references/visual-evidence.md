# Contrato de procedencia visual y atlas semántico

## Principio

El atlas de Markmap y LikeC4 **no son autoridades de código**. Solo representan el ledger generado por CogniCode CLI/MCP y, separadamente, intención humana atribuida. No leer checkout, README, ADR, manifests, tests o fuentes por herramientas alternativas. No inferir relaciones a partir del render.

## Taxonomía mínima (solo cuando haya valor)

| Categoría | Pregunta de investigación | Prueba |
|---|---|---|
| system | ¿Qué ejecutable/sistema está demostrado? | entrada/arranque real |
| module | ¿Qué límites y agrupaciones hay? | símbolos/comunidades observadas |
| surface | ¿Qué RPC/API o contrato expone? | implementación de entrada |
| external | ¿Qué sistema o cliente externo invoca? | cliente y configuración corroborados |
| store | ¿Qué almacén utiliza? | implementación de persistencia |
| signal | ¿Qué problemas tipados detectó CogniCode? | salida estructurada, sin veredicto humano |
| coverage | ¿Qué omisiones/alcance tiene el análisis? | skipped_files/informe CogniCode |
| glossary | ¿Qué término del código significa? | símbolo/definición |
| symbol | Símbolos/relaciones sin clasificar | identidad y query |
| intent | ¿Qué propósito se declara? | CODE_DOC o CURATED_INTENT |

El agente **no rellena** estas categorías si no tiene pregunta ni evidencia: no gastar tokens, no reconsultar lo ya sabido.

## Evidencia, estados y separación

- `OBSERVED_CODE`: claim proveniente de CogniCode; mostrar `query_ids`, `coverage` y `plane`. Si un registro heredado carece de consulta verificable se presenta `UNKNOWN`.
- `CODE_DOC`: KDoc/docstring emitido por CogniCode con query identificada. Expresa intención, **no** implementación probada.
- `CURATED_INTENT`: aportación directa humana, con `curator` explícito y plano `intent`. No inventar `query_id`.
- `INFERRED/UNKNOWN`: incertidumbre. `DOC_INTENT` de lectura documental queda deshabilitado por conflicto con el contrato de exclusividad.
- Los `*.atlas.json` de `plane=implementation` no pueden citar claims de intención. Para una vista conceptual intencional declarar `plane=intent` y no mezclarla con implementación.

Las relaciones `reference_link` usan `query_id + index + path:line` y no son `graph_edge`. Atributos `kind/technology/endpoint/order` requieren resultados CogniCode; una función `Client` no prueba HTTP, ni `Mono.when` prueba el orden temporal real. El orden **declarado** puede representarse con `plane=static` y limitación expresa.

## Ejemplo LikeC4 sintético

```likec4
specification {
  element component
}
model {
  client = component 'Cliente' {
    metadata {
      claim 'C-14'
      query 'Q-49'
      plane 'static'
      coverage 'partial'
    }
  }
}
views {
  view index {
    include *
  }
}
```

Validar con el parser de LikeC4 instalado. Repetir metadata solo donde corresponda; `link` al atlas local únicamente si está realmente accesible. El visor LikeC4 solo monta fuentes de su lente, no evidencia externa. Las vistas dinámicas pueden describir **secuencias declaradas**; no simulan telemetría.

## Coste y controles

Cada observación útil actualiza ledger y `atlas.py sync`; cada nueva vista enlaza sus claims mediante `*.atlas.json`; render HTML solo para revisión visual/cierre. Nunca crear base de datos, otro MCP, servidor de análisis, nuevas UAT persistentes sin regresión crítica o diagramas con más de 15 nodos sin dividir.

Referencia oficial: https://likec4.dev/dsl/model/ , https://likec4.dev/dsl/relationships/ , https://likec4.dev/dsl/views/dynamic/ , https://markmap.js.org/docs/packages--markmap-cli .
