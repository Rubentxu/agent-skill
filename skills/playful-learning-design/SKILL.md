---
name: playful-learning-design
description: "Diseña experiencias de aprendizaje gamificadas para niños 8–16 y adultos. Selecciona juegos, experimentos, mapas, aventuras o tarjetas por objetivo cognitivo y evidencias, mediante lentes HATEOAS-like, con explicaciones progresivas, accesibilidad y motivación ética. No programa HTML ni fuerza Anki."
---

# Playful Learning Design — aprendizaje primero

**Resultado:** Learning Experience Brief reducido, con una actividad jugable verificable; no un curso enorme ni un juego elegido por moda.

## Loop agent-first

1. Observar objetivo, público y lo que ya sabe; si falta un dato **imprescindible**, pedir solo ese dato. Edad no determina capacidad.
2. Leer [navigation](references/navigation.md) + [lens-registry](references/lens-registry.json); elegir una lente `ready` y su playbook según pregunta/estado observados. `planned` no es ejecutable.
3. Definir objetivo **observable**, unidades de contenido fiables y equivocaciones probables, sin afirmar fuentes no verificadas. Separar mnemotecnia de hecho.
4. Seleccionar una **acción cognitiva** (recordar, localizar, manipular, explicar, ordenar, decidir, construir) y entonces su representación lúdica. Variar solo si añade valor.
5. Diseñar ciclo: introducción concreta → reto → respuesta → feedback útil → reintento → observación de dominio, con pistas retirables.
6. Diferenciar dominio (`MasteryEvidence`), actuación (`Attempt`) y recompensa (`XP/Badge`); no tratar tiempo/clics/racha como aprendizaje.
7. Adaptar dificultad, privacidad, lenguaje, accesibilidad y riesgos con ayuda de [inclusive-design](references/lenses/inclusive-design.md).
8. Entregar [brief](assets/learning-experience-brief.md) con 1 experiencia vertical, mecánica justificada, evidencia, rutas de errores, contexto y límites. Si el contenido no está contrastado, `PARTIAL`, nunca `VERIFIED`.

## Lentes disponibles (cargar bajo demanda)

[Perfil](references/lenses/learner-context.md) · [Objetivo](references/lenses/learning-loop.md) · [Contenido](references/lenses/knowledge-and-misconceptions.md) · [Mecánica](references/lenses/mechanic-selection.md) · [Explicaciones](references/lenses/novice-scaffolding.md) · [Motivación](references/lenses/ethical-motivation.md) · [Dominio](references/lenses/learning-evidence.md) · [Inclusión](references/lenses/inclusive-design.md).

## Invariantes

- Tarjetas y repetición espaciada **opcionales**, solo cuando se precisa recuperación de hechos/procedimientos memorizables.
- Experiencias adecuadas a nivel y preferencias, sin contenido infantilizante por defecto para mayores.
- No cuentas, seguimiento individual remoto ni anuncios en páginas infantiles por defecto; evitar rankings públicos, cajas aleatorias y castigos por descansar.
- La ayuda simplifica el acceso, **no** falsifica el contenido.
- HATEOAS-like = enlaces locales `rel/href/why` derivados de estado observado; no API, runtime ni ejecución automática.
- No instalar otras skills por inferencia. `learning-game-html` puede recibir el brief, pero no es dependencia requerida.

**Cierre:** objetivo + evidencia observable + datos fiables o incertidumbre + mecánica justificada + errores/pistas + motivación + acceso + brief realizable. [Evals](tests/skill-evals.md).
