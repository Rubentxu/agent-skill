# Descubrimiento opcional de skills complementarias

La skill de creación HTML **funciona sola**. El agente no presume instaladas otras skills, no descarga prompts externos en automático y no mezcla derechos/licencias de terceros.

- `playful-learning-design` cuando el objetivo/mecánica/criterio educativo está poco claro; intercambiar un breve artefacto, no ejecutar dos motores.
- `delivery-first-testing` si está **realmente instalada**, para selección de pruebas, UAT efímeros y regresión mínima. No añadir CI nuevo.
- `frontend-design` (`anthropics/skills`, https://github.com/anthropics/skills/tree/main/skills/frontend-design) como **fuente opcional de inspiración en dirección artística** si está disponible. Sus criterios de coherencia, tipografía, espacio y motion se han sintetizado en nuestra lente, sin exigir instalación ni copiar código protegido.
- `web-design-guidelines` (`vercel-labs/agent-skills`, https://github.com/vercel-labs/agent-skills) para una revisión UI adicional si está instalada y los requisitos la justifican. No reemplaza el UAT funcional propio.
- `cognicode-diagrams` solo para preguntas de arquitectura **cuando CogniCode esté operativo** y se respeten sus restricciones de investigación; no es una dependencia para leer/editar HTML ni una puerta para mezclar sus claims.

El agente debe descubrir nombre/descripción de skills disponibles a través del cliente real. Recomendación ≠ instalación, disponibilidad ≠ ejecución, test sintético ≠ prueba real.
