# learning-game-html

Skill autónoma para crear/evolucionar HTML educativos con **dirección artística de videojuego**, mapa, SVG, motion, UI responsive, modos y persistencia, sin fijar Anki ni requerir frameworks. Entrada: una actividad/objetivo y HTML existente opcional. Salida: artefacto real jugable (un HTML offline por defecto cuando viable) y estado de verificaciones.

Consulta `references/navigation.md` y `references/lens-registry.json`. Para visuales, `references/lenses/art-direction.md`, `references/lenses/visual-qa.md` y `references/patterns/catalog.md`. Helper puro: `python3 scripts/affordances.py examples/session-create.json`.

Para la ruta inicial: `examples/non-flashcard-fractions.md`. Para regresiones: `examples/atlas-quest-refinement.md`. El agente puede usar `delivery-first-testing` **solo si está instalada**, sin crear harness ni CI alternativo. UAT agente real `NOT_RUN` hasta ejecutarla.
