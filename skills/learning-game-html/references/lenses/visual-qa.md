# Lente: revisión visual de producto, no de captura promocional

Abrir **artefacto construido** en navegador a 390, 768, 1440 px (o equivalentes) y tocarlo. Verificar jerarquía clara, composición sin cortes, tipografía y áreas táctiles, scroll/zoom y foco, affordances visibles, estado vacío y errores.

Rúbrica [visual-quality-gate](../../assets/visual-quality-gate.md) de 0 a 2 por criterio. Primeras entregas deben mostrar una **escena interactiva** y un bucle completo, no solo hero o particles. Las capturas representan evidencia de layout, **no** de clicks, memoria ni migración.

Probar motion normal y reducido; bajo CPU móvil no dejar animación permanente que bloquee respuesta. Corregir layout y reabrir la versión final (no usar screenshot de build antigua).

Sin navegador real: `VISUAL_NOT_RUN`; código CSS compilado no implica aprobación visual. Los criterios son orientativos, no medición automática de calidad artística.

**Revisión complementaria opcional:** [web-design-guidelines](https://github.com/vercel-labs/agent-skills) puede aportar reglas UI si la skill existe en el entorno. Su uso nunca certifica funcionalidad o aprendizaje; comprobar ambas cosas por separado.
