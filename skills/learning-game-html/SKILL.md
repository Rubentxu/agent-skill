---
name: learning-game-html
description: "Crea, evoluciona, repara y pule juegos educativos web visualmente espectaculares y realmente interactivos: HTML/CSS/JS, mapas SVG, escenas, simulaciones, animaciones con propósito, estado/persistencia y UAT de navegador. Autodescubre lentes HATEOAS-like; no obliga a tarjetas ni a framework."
---

# Learning Game HTML — que parezca un juego y enseñe algo

**Meta:** entregar una experiencia web **ejecutable y memorable**, no una maqueta ni cuestionarios con medallas. Diseñar como un pequeño videojuego educativo: arte, escena, decisiones, feedback, progreso real y acceso para todos.

## Routing

1. Observa intención `create|improve|repair|polish|audit|catalog`, HTML real si existe, material objetivo, datos del usuario, navegador disponible y riesgos. **No asumir** que Atlas Quest es el stack de otras apps.
2. Lee [navigation](references/navigation.md) y [lens-registry](references/lens-registry.json); una lente `ready` por pregunta. El helper [affordances](scripts/affordances.py) es puro y opcional.
3. Exige objetivo/actividad/evidencia mínimos, mediante [design-brief](assets/design-brief.md) o brief de otra skill instalada. Si no existe, especifica uno pequeño y continúa.
4. Selecciona metáfora y lenguaje visual propio ([art direction](references/lenses/art-direction.md)); idea **wow** con interacción, no decoración. Diseña estados de actividad y transición antes de dibujar.
5. Construye una **vertical jugable**: inicio → acción → evaluación → feedback → nueva oportunidad → cierre/repetición. Separa contenido, `reducer` puro y efectos de DOM/sonido/almacenamiento.
6. Aporta una escena verdaderamente manipulable ([interactive-scene](references/lenses/interactive-scenes.md)): SVG, diagramas, mapa, simulador, timeline u objeto físico simplificado. Usa CSS y transiciones proporcionadas, no loops ornamentales permanentes.
7. Comprueba estados extremos, historial/progreso, permisos, accesibilidad, ausencia de red y experiencia móvil. Preserva datos y funciones existentes; `Reiniciar ronda` nunca borra progreso por accidente.
8. Revisa **visualmente en navegador y haciendo clic** ([visual-qa](references/lenses/visual-qa.md), [browser-acceptance](references/lenses/browser-acceptance.md)). Si no hay navegador, declarar `NOT_RUN`. Pruebas temporales selectivas; conservar solo regresiones críticas.
9. Entrega **HTML/ZIP real** o cambio real al proyecto, instrucciones y evidencia/limitaciones. Proponer release y merge solo tras autorización.

## Diseño obligatorio, sin sobreingeniería

- Default: HTML, CSS, JS y SVG propios, offline y responsive. Si una app ya usa framework, respetarlo. Código fuente organizado y distribución HTML única cuando proceda.
- Separar `KnowledgeUnit`, `Challenge`, `Attempt`, `MasteryEvidence`, `GameSession`, `Reward`, `Progress`, `VisualScene`. XP no es dominio. Pistas usadas cambian la fiabilidad de la prueba de aprendizaje.
- Una escena hero atractiva, dirección visual deliberada, microinteracciones significativas, contenido contrastado, pantallas vacías y de error cuidadas, controles reales y accesibles.
- `prefers-reduced-motion`; color no exclusivo; teclado, touch, zoom, tipografía legible y alternativa textual o botonera para acciones espaciales.
- Local-first sin telemetría y sin anuncios, especialmente para menores. Almacén versionado y exportable; no eliminar datos sin consentimiento.
- No afirmar test, offline, compatibilidad, recuperación de progreso ni calidad visual si no han sido comprobados en el artefacto final.

## Modos

- `create`: crear una primera experiencia completa en pequeño, artística y jugable.
- `improve`: añadir mecánica/visual sin romper progreso ni borrar funcionalidades.
- `repair`: reproducir y resolver fallo; priorizar regresión pertinente antes de pulir.
- `polish`: elevar diseño, motion, mapa/escena, responsive y feedback **manteniendo contratos**.
- `audit`: medir defectos visibles/técnicos sin tocar el proyecto.

[Skills complementarias opcionales](references/related-skills.md).

**Salida:** aplicación real y usable; no motor de juegos universal, SaaS, framework nuevo ni tests de harness extensivo. [Evals](tests/skill-evals.md) · [Arte y criterios](assets/visual-quality-gate.md).
