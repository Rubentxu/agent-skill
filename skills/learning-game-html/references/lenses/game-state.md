# Lente: dominio de juego y estados explícitos

Arquitectura proporcionada: un `reducer(state,action)->state` puro para transiciones, selectores derivados y adaptadores de efectos en DOM / tiempo / persistencia. La representación solo genera eventos y dibuja el resultado. Evitar framework propio y gigantescos ifs de pantalla.

Estados típicos: `intro → active → answered → feedback → active|complete`; rutas independientes `free-practice`, `review-errors`, `settings`. Acciones semánticas como `START_SESSION`, `SUBMIT_ANSWER`, `SHOW_HINT`, `MARK_FOR_REVIEW`, `RETRY`, `ENTER_FREE_PRACTICE`, `RESTART_SESSION`, `CLEAR_ALL_PROGRESS`.

**Contratos críticos de Atlas Quest**:

- `dailyComplete` → `ENTER_FREE_PRACTICE` debe generar cola real, no reusar modo `daily` agotado.
- `RESTART_SESSION` reinicia la cola actual, NO hace `localStorage.clear()` ni borra mastery; esto sería `CLEAR_ALL_PROGRESS` con confirmación.
- `missed`, `marked`, `recovery`, `mastery` son estados distintos, con condiciones de recuperación verificables.
- Una respuesta incorrecta no se convierte en correcta porque la persona pulse «Bien» y no hay XP ilimitado por dar vueltas/revelar la misma actividad.
- La pantalla «completado» siempre ofrece siguiente acción real, y `queue empty` no conduce a spinner o botón inerte.

La puntuación y XP son proyecciones; **solo evidencia sin pista** puede acreditar dominio. Los eventos tienen identidad para evitar duplicados por doble clic, transiciones y reentradas. No inventar un event bus si no hace falta.
