# Navegación HATEOAS-like contextual (sin HTTP)

El router es **puro** respecto al proyecto: lee catálogos empaquetados, calcula decisiones y ofrece `_links[]`. Ninguna recomendación equivale a ejecutar tests, leer código o cambiar el repositorio.

## Entrada — sesión observada y evidencia mínima

```json
{
  "intent": "refactor",
  "phase": "plan",
  "basis": "observed",
  "language": "rust",
  "risk": "high",
  "signals": ["side-effects", "large-service"],
  "problems": [{
    "id": "mixed-rules-effects",
    "evidence": [{"source": "src/usecase.rs:42", "observation": "Decisión invoca SQL en la misma rama"}]
  }],
  "facts": ["behavior-characterized", "effect-order-understood"],
  "constraints": [],
  "available_skills": ["delivery-first-testing"]
}
```

- `intent`: `catalog|discovery|design|implementation|refactor|review`.
- `phase`: `diagnose|plan|verify` (default `diagnose`). En diagnóstico no se exponen recetas ni perfil de sintaxis; en planificación se anuncia `read-recipe` solo si se cumplen precondiciones; en verificación se anuncia `verify-contracts`.
- `basis`: `observed|unknown|stale`, nunca certificación automática del router.
- `signals`: observaciones superficiales del caso; **no bastan** para `APPLY`.
- `problems`: problema tipado de `problems.json`. `evidence` con pares no vacíos `source/observation` produce `OBSERVED` declarado por el llamante; sin evidencia, `INFERRED`. El helper no puede verificar la veracidad de esas cadenas.
- `facts`: precondiciones afirmadas observadas por el llamante; `constraints`: contraindicaciones; ambos vocabularios proceden de `recipe-registry.json` y el script los valida.
- `available_skills`: IDs que el anfitrión ha confirmado realmente disponibles, no sugerencias ni plugins presumidos.
- `risk`: `routine|high|critical`, alerta sobre riesgo; no sustituye los preconditions de cada receta.

## Máquina de decisión

1. `catalog`: listar lentes y recetas, sin activarlas.
2. `basis=unknown|stale`: `inspect-code|refresh-basis`, sin diagnosticar.
3. `language=unknown`: `identify-language`, sin asumir sintaxis.
4. Sin observaciones útiles: `discover-signals`, sin patrón predeterminado.
5. Con señales solamente: inferir **hipótesis** y activar `problem-diagnosis`; no `APPLY`.
6. Con problemas respaldados por evidencias, comparar `KEEP_AS_IS` y recetas `ready` por precondiciones, contraindicaciones, esfuerzo, riesgo y reversibilidad **en ese orden**. La comparación es ordinal, no probabilidad ni rentabilidad demostrada.
7. `APPLY`: la receta es una propuesta implementable, no ejecución; `INSPECT_MORE`: falta evidencia; `KEEP_AS_IS`: no hacer cambio; `BLOCKED`: contraindicación.
8. Seleccionar 1–3 lentes metodológicas contextuales más perfil de lenguaje en `plan/verify`. Preferir especialización con problema coincidente antes que prioridad fija del catálogo.
9. Solo enlazar a otra skill con `delegate-skill` si el anfitrión ha observado su disponibilidad real; no invocar ni instalar automáticamente.
10. Una nueva observación o giro de la conversación reinicia este cálculo; **no se escribe un archivo de sesión**.

## Rutas

`read-lens`, `read-recipe` incluyen `href` relativo **dentro de esta skill**; acciones sin archivo (`inspect-problem`, `compare-options`, `propose-slice`, `verify-contracts`, `preserve-existing`, `delegate-skill`) tienen `rel` y `why`. Ninguna `href` es URL de ejecución.

## No-vacuidad

No llamar `PASS` a una recomendación; una entrada `OBSERVED` con texto de evidencia falso sigue siendo responsabilidad del agente que inspecciona. Si no existe inspección de código, reportar `BLOCKED/NOT_RUN`, jamás suponer que un archivo o una prueba existen.
