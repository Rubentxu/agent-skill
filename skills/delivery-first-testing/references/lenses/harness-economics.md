# Lente: economía y salud del harness

**Pregunta:** ¿qué coste genera el sistema de validación y qué defectos detecta? Priorizar datos reales: p50/p95 por gate, top tests lentos, tasa de falsos rojos, cambios solo para arreglar tests, tests duplicados, skips, reruns, cache hit, tiempo hasta entrega y defectos escapados. Si no hay datos, proponer una medición corta, no inventar porcentajes.

Inventariar pruebas de implementación, layout, snapshots, UAT de sesión obsoletos, checks de checks sin nueva garantía, E2E duplicados y gates de release ejecutados por merge. Eliminar/reubicar con evidencia; proteger lo crítico y comprobar que pruebas retiradas no dejan huecos. Regla de parada: si una nueva comprobación añade más mantenimiento que riesgo cubierto, diseñar alternativa o moverla de fase.

**Cierre:** top oportunidades ordenadas por tiempo recuperado, coste de migración, riesgo de escape y plan de medición postcambio. No crear un segundo sistema de seguimiento.
