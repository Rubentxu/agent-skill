# playful-learning-design

Skill de **diseño educativo y ludificación**. Entra con una materia, una audiencia y un objetivo de aprendizaje. Sale con un brief que describe una interacción jugable y cómo probar el aprendizaje. No crea HTML automáticamente ni exige tarjetas.

Instalación selectiva en un agente que admita el formato `SKILL.md`; router opcional: `python3 scripts/affordances.py examples/session-create.json`. El agente usa `references/navigation.md` y `references/lens-registry.json` para autodescubrimiento, no lee siempre todas las lentes.

Ejemplos: `examples/atlas-quest-brief.md` (geografía) y `examples/fracciones-brief.md` (simulador sin tarjetas). Tests mínimos bajo `tests/`. Evals de agente aún por ejecutar.
