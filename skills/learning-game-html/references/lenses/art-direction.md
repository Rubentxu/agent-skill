# Lente: dirección artística de videojuego educativo

**No escoger «dashboard + tarjetas» por defecto.** Proponer 2 metáforas de interfaz rápidas y elegir una por el objetivo: atlas cinematográfico, nave de expedición, mesa de investigación, museo interactivo, estación espacial, libro desplegable, laboratorio animado, simulador físico. La metáfora debe **mostrar relaciones del conocimiento**.

Checklist creativo de primera pantalla:

1. **Escena protagonista** que invite a tocar algo, con respuesta inmediata y espacio visual suficiente. El usuario ve qué jugar en cinco segundos.
2. Sistema visual: 3–5 colores funcionales, fondos con profundidad discreta, contraste, escala tipográfica reconocible, iconografía consistente, espaciado, capas y sombras selectivas.
3. **Voz visual propia**: editorial/retro futurista/ilustrado/ciencia/minimalista según público. Evitar plantillas Bootstrap genéricas, UI gris indiferenciada y saturación de emoji.
4. **Estados con dramaturgia**: bienvenida, hover/foco/touch, anticipación, descubrimiento, error con pista, éxito proporcionado, transición a siguiente misión, final con opción de continuar.
5. Antes del código: breve `art direction`: metáfora, paleta, tipografía/fallback, escena hero, microinteracciones, sonido opcional, fallback y accesibilidad.
6. Animación con semántica: enfocar país/mostrar órbita, transformación de fracción, abrir compartimento al resolver, resaltar causalidad. Respetar preferencias de movimiento reducido y pausa.

**Regla visual:** una animación solo existe si enseña, orienta, confirma una acción o recompensa un avance legítimo. Mantener `transform/opacity` cuando baste para reducir repaints; no garantizar FPS por escribir CSS.

[Calidad visual](../../assets/visual-quality-gate.md) · [Patrones](../patterns/catalog.md).

**Inspiración externa, no dependencia:** la skill pública [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) de Anthropic promueve comprometerse con una identidad visual concreta. Aquí lo vinculamos además a una interacción educativa y evidencia funcional: tipografía/motion no valen como sustituto de juego.
