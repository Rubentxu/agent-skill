# Lente: por qué fallan tests y gates

**Pregunta:** ¿falla el producto, el test, la infraestructura o la evidencia? Primero aislar el primer error causal; reproducir con el filtro más pequeño y revisar commit, binario, fixtures, runner, timeouts, variables, procesos y caché. Clasificar `PRODUCT_DEFECT`, `INTENTIONAL_CONTRACT_CHANGE`, `TEST_COUPLING`, `INFRASTRUCTURE`, `FLAKY`, `STALE_EVIDENCE`, `MISSING_EVIDENCE`.

Un test roto por cambio interno sin cambio observable debe rediseñarse. Evitar modificar producción para ajustar snapshots obsoletos. Para flaky comparar mismo código, entornos y ensayos controlados; no elevar timeouts indefinidamente sin hipótesis medible. Quarantine explícita acotada para pruebas no críticas con responsable, seguimiento y alternativa de protección; crítica nunca bypass automático.

**Cierre:** causa, prueba discriminante rojo→verde cuando aplica, qué se corrige, cuál es la garantía y si el gate permanece confiable. No hacer rerun de toda la batería para diagnosticar un solo test.
