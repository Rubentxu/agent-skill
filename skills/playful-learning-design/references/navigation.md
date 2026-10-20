# Navegación por affordances (HATEOAS-like, sin HTTP)

El agente observa un estado y consulta el registro. El **helper opcional es puro**: devuelve solo un enlace a una guía; no inspecciona código, no accede a red, no construye juegos y no certifica las entradas suministradas.

Estado ejemplo:

```json
{"intent":"design","audience":"ready","objective":"ready","knowledge":"ready","mechanic":"missing","scaffolding":"missing","motivation":"missing","evidence":"missing","inclusion":"missing"}
```

Valores: `ready|missing|unknown` (ningún campo omitido significa aprobado). `intent=catalog|design|refine|audit`. `focus` opcional: `content|game|explanation|rewards|assessment|inclusion`; solo sirve para decidir la próxima **pregunta**, no transforma un estado en evidencia. Primero se valida audiencia/objetivo/contenido; se pueden proponer hipótesis mientras aún no estén verificados, pero no cerrar como `VERIFIED`.

- `profile-learner` → `references/lenses/learner-context.md`
- `define-objective` → `references/lenses/learning-loop.md`
- `verify-knowledge` → `references/lenses/knowledge-and-misconceptions.md`
- `choose-mechanic` → `references/lenses/mechanic-selection.md`
- `design-feedback` → `references/lenses/novice-scaffolding.md`
- `motivation-safety` → `references/lenses/ethical-motivation.md`
- `define-learning-evidence` → `references/lenses/learning-evidence.md`
- `inclusive-design` → `references/lenses/inclusive-design.md`
- `deliver-brief` → `assets/learning-experience-brief.md`

Ejecutar el procedimiento, reobservar el trabajo y actualizar estado. Una lente `planned` no se anuncia como `ready`. Si el usuario solicita solo una auditoría, responder con hallazgos y vacíos: no fabricar un rediseño entero.

`python3 scripts/affordances.py examples/session-create.json` produce la siguiente affordance. El helper no declara que los objetivos sean pedagógicamente adecuados.
