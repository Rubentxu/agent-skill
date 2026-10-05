# Validación y análisis de gaps

## Validar la descripción

La validación responde: **¿los artefactos representan fielmente lo aprendido y son suficientes para el objetivo?** No equivale a revisar ortografía ni a contar fuentes.

## Checks

### Coherencia semántica

- mismo concepto → mismo significado;
- términos distintos no ocultan el mismo concepto sin explicación;
- definiciones no se contradicen entre fichas/modelos.

### Coherencia estructural

- cada componente crítico tiene responsabilidad/frontera;
- dependencias y autoridades importantes están representadas;
- no hay “cajas mágicas” donde se esconda precisamente la incertidumbre relevante.

### Coherencia funcional

- cada capability relevante tiene mecanismo;
- cada paso de workflow tiene actor/componente responsable;
- outputs y efectos observables son distinguibles.

### Coherencia dinámica

- estados relevantes tienen eventos/transiciones;
- fallos/reintentos/recuperación se modelan cuando cambian la semántica;
- invariantes temporales importantes no dependen sólo de prosa.

### Evidencia

- claims decisivos tienen fuente;
- fuente y claim comparten versión/contexto;
- inferencias están etiquetadas;
- contradicciones siguen visibles.

## Estados de gap

Usa:

- `unknown`: todavía no hay respuesta;
- `assumed`: se usa una hipótesis sin evidencia suficiente;
- `contradicted`: evidencia fiable entra en conflicto;
- `unverified`: existe una afirmación plausible aún no comprobada;
- `obsolete`: era válida en otro alcance/versión.

## Prioridad

Prioriza cualitativamente:

```text
priority = uncertainty × impact × decision_relevance
```

No hace falta asignar números falsamente precisos. Clasifica `critical/high/medium/low` y explica por qué.

## Condición de iteración

Itera sólo si el gap puede cambiar:

- el modelo conceptual;
- una frontera o autoridad;
- una capability/workflow;
- una decisión de adopción/integración;
- un riesgo de alto impacto;
- la explicación que se pretende enseñar.

Si no, déjalo documentado y converge.
