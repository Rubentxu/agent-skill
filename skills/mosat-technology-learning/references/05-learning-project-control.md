# Control del proyecto de aprendizaje

## Por qué

Una investigación tecnológica puede crecer sin límite. Controla explícitamente tiempo, alcance, profundidad y entregables para que MOSAT produzca comprensión útil, no una enciclopedia.

La gestión del proyecto se usa aquí como extensión operativa inspirada en la aplicación práctica mostrada por el autor; no la presentes como un artefacto formal adicional del paper original sin evidencia.

## Contrato inicial

Antes de investigar, fija:

```yaml
goal: ...
decision_or_use: ...
audience: ...
depth: orient | understand | comprehend | engineer
perspective_weights:
  discipline: low | medium | high
  process: low | medium | high
  product: low | medium | high
constraints: []
deliverables: []
stop_condition: ...
```

## Profundidad

- `orient`: ubicar tecnología, propósito, vocabulario y límites.
- `understand`: saber qué hace y cómo usar/explicar su funcionamiento principal.
- `comprehend`: explicar estructura, funciones, dinámica y contexto con relaciones causales.
- `engineer`: suficiente detalle para integrar, extender, operar o tomar decisiones de diseño/riesgo.

Estos niveles son una extensión de esta skill; no afirmes que son niveles oficiales de MOSAT.

## Stop conditions útiles

- todas las preguntas críticas para la decisión tienen respuesta o `UNKNOWN` aceptado;
- nuevas fuentes ya no cambian modelos ni claims decisivos;
- los gaps restantes son de impacto bajo respecto al objetivo;
- existe trazabilidad suficiente para que un tercero revise las conclusiones;
- el modelo permite responder las preguntas que motivaron el estudio.

Evita cerrar por “número de documentos leídos”.
