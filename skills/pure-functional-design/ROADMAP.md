# Roadmap de `pure-functional-design` — skill genérica para aplicaciones

**Alcance:** evolucionar únicamente la skill portable dentro de `Rubentxu/agent-skill`. No hay objetivo de modificar, auditar ni preparar refactors para repositorios de aplicaciones concretas. Los proyectos que adopten la skill deciden por sí mismos qué ejecutar.

## Entregado: fundamentos y router R1–R3

- **F0:** contrato portable, ontología y bibliografía de Haskell → Rust/Kotlin.
- **F1:** lentes de ADT, efectos, arquitectura funcional, algoritmos y vertical slices.
- **R1:** diagnóstico por problemas, hechos observados frente a hipótesis y alternativa `KEEP_AS_IS`.
- **R2:** ocho recetas de refactor incremental con precondiciones, contraindicaciones y reversibilidad.
- **R3:** carga contextual `diagnose → plan → verify`, delegación únicamente a skills disponibles.
- **Integración:** publicado en `main`; validación de catálogos, enlaces y tests de navegación por CI.

## R4 — Evaluaciones portables sin proyectos específicos

**Entrega:** fixtures Rust/Kotlin y sesiones sintéticas autocontenidas, que cubren:
1. `INSPECT_MORE` si existen reglas y efectos mezclados, pero faltan contratos observados.
2. `KEEP_AS_IS` si la responsabilidad es cohesionada, aunque el archivo tenga muchas líneas.
3. `APPLY` como **propuesta** si se aportan diagnóstico y precondiciones, nunca como ejecución.
4. Transiciones `diagnose → plan → verify`, `unknown/stale`, cambios de contexto y ausencia de skills externas.

**Gate:** tests reproducibles del selector, sin acceso a código ni credenciales de terceros. Los ejemplos son **sintéticos**, no evidencias de incidencias en aplicaciones reales. No atribuir `PASS` a Cargo, Gradle ni tests de consumidores.

## R5 — Calidad y extensibilidad del sistema de skills

- Evaluar con agentes reales la activación desde peticiones generales, ambiguas y cambiantes.
- Medir falsos positivos/negativos, abstenciones correctas y coste de contexto del router.
- Mejorar la correspondencia `problema → alternativas → receta` y eliminar rutas redundantes.
- Añadir lenguajes nuevos mediante perfiles idiomáticos cuando se justifique, sin copiar Haskell literalmente.
- Mantener independencia de instalación: ninguna skill requiere importar archivos de otra.
- Si el agente anfitrión no anuncia otra skill, limitar la delegación sin simular disponibilidad.

**Criterio de cierre:** el agente que usa la skill elige transformaciones por evidencia y valor, ofrece `KEEP_AS_IS` cuando corresponde y adapta los procedimientos al contrato del proyecto receptor, sin depender de nombres o rutas de un repositorio particular.

## Fuera de alcance

- Refactorizar, probar o modificar aplicaciones reales desde este repositorio.
- Acumular evaluaciones específicas de productos en la skill genérica.
- Introducir CI duplicado, servicio persistente, motor de reglas complejo o runtime nuevo.
- Confundir validación de la skill con validación de código de producción.
