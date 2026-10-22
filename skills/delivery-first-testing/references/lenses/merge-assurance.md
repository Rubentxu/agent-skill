# Lente: merge rápido con señal honesta

**Pregunta:** ¿el cambio integra sin romper los compromisos relevantes? Verificar build/compilación incrementales, lint útil, contratos públicos afectados, unitarios/component tests, un smoke de consumidor si necesario y selección conservadora para cambios transversales. No compilar artefactos release completos por defecto.

Usar la autoridad CI local existente (PipelineK, Gradle, cargo, pnpm). Si existe selector, comprobar que sus decisiones afectan a **las tareas ejecutadas**, no solo imprimen un plan mientras corren todas. Mantener un negativo de runner que se ejecute por cambio de harness/CI, no un `exit 1` siempre al final de aceptación normal. Evitar esconder fallos con `|| true` o `exit` temprano.

**Cierre:** HEAD exacto, lista de pruebas ejecutadas y no ejecutadas, salida/outcome coherente; PASS indica cobertura esperada para merge, no certificación completa de release.
