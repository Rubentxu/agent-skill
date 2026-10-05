# Procedencia y confianza — extensión agent-first

MOSAT original usa fichas y modelos para representar conocimiento. En trabajo con agentes añade una capa explícita de procedencia para evitar que síntesis plausibles se conviertan en “hechos” sin soporte.

## Unidad de conocimiento

```text
Claim
├── Evidence
├── Source
├── Authority class
├── Scope / version / date
├── Confidence
├── Contradictions
└── Status
```

## Clases de autoridad

Usa categorías, no puntuaciones universales:

- `primary-spec`: estándar, RFC, paper fundacional, contrato normativo;
- `official-doc`: documentación mantenida por el producto/proyecto;
- `source-code`: implementación ejecutable y tests del alcance estudiado;
- `academic`: publicación técnica relevante;
- `practitioner`: ingeniería de terceros con evidencia reproducible;
- `community`: experiencia colectiva útil pero no normativa;
- `anecdotal`: señal débil que sirve para generar preguntas, no conclusiones.

La autoridad depende de la pregunta: el código puede superar a la documentación para comportamiento real de una versión, mientras una especificación puede seguir siendo autoridad para semántica normativa.

## Confianza

- `high`: evidencia primaria/ejecutable coherente y alcance claro;
- `medium`: evidencia suficiente pero indirecta, parcial o dependiente de contexto;
- `low`: inferencia, fuente débil, versión incierta o conflicto no resuelto.

Nunca uses confianza para ocultar contradicciones: conserva ambas evidencias y explica el alcance.

## Disciplina de salida

En el entregable final distingue:

- **Known**: sustentado;
- **Inferred**: derivado razonablemente de evidencia;
- **Assumed**: hipótesis de trabajo;
- **Unknown**: no resuelto;
- **Disputed**: fuentes fiables incompatibles dentro del alcance actual.
