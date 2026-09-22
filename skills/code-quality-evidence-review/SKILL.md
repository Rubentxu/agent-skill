---
name: code-quality-evidence-review
description: "Audita calidad de código de cualquier repositorio o PR con evidencias reproducibles: arquitectura y dependencias, SOLID, tipado, connascence, duplicación, deuda, pruebas, CI/CD, seguridad, rendimiento, supply chain, documentación y observabilidad. Úsala para detectar riesgos, verificar cumplimiento o preparar integración/release sin asumir un lenguaje, framework o arquitectura concretos."
---

# Auditoría transversal de calidad basada en evidencias

**Objetivo:** obtener conclusiones comprobables, con coste de verificación proporcional al riesgo. Esta skill no presupone Kotlin, Jenkins, arquitectura hexagonal ni una plataforma CI determinada. Los principios de arquitectura y diseño son hipótesis de revisión: solo se convierten en *reglas exigibles* si el proyecto las adopta o existe una consecuencia técnica demostrable.

## Procedimiento (cada paso tiene criterio de cierre)

1. **Fija alcance, invariantes y baseline.** Determina tipo de revisión (`PR`, `focal`, `repositorio`, `pre-release`), revisión exacta (`git rev-parse HEAD`, árbol sucio, base del diff), lenguajes, módulos, producto, despliegue y límites de acceso. Consulta instrucciones del proyecto (`AGENTS.md`, ADR, tests, README y políticas CI) sin presumir que estén actualizadas. No ejecutes scripts del repo no confiable ni envíes código privado a servicios sin autorización. **Cierre:** se sabe *qué* se audita, frente a *qué* se compara y qué es una norma del proyecto frente a una preferencia del auditor. Si no hay checkout, delimita la evidencia disponible.

2. **Prepara el mapa de evidencia.** Distingue fuentes: código de producción, build/lockfiles, grafo de dependencias, tests y resultados, CI por SHA, ejecución y documentación. Enumera entradas, salidas, límites de confianza, consumidor/productor y rutas de ejecución relevantes. Usa `references/01-evidence-workflow.md` y, si hay varios lenguajes, `references/04-language-recipes.md`. **Cierre:** inventario de componentes, rutas revisadas, trazas de comprobación y lagunas; las búsquedas negativas incluyen patrones, exclusiones y alcance.

3. **Selecciona dimensiones sin imponer tecnologías.** Para revisión global cubre las 12 dimensiones de `references/02-dimensions-playbook.md`; para revisión focal cubre las relacionadas con el diff, los contratos consumidores y riesgos transversales, dejando explícito el resto. Para arquitectura y connascence usa `references/03-architecture-connascence.md`; para seguridad, `references/07-security-supply-chain.md`. **Cierre:** cada dimensión en alcance tiene pregunta, método de obtención, evidencia o `NO VERIFICADO`; `NO APLICA` exige justificación.

4. **Escoge mecanismos y herramientas por hipótesis.** Empieza por Git, lectura dirigida y comprobaciones del build/test *ya disponibles*. Si un dato requiere una herramienta, consulta el anexo `references/05-tool-catalog.md`: selecciona la opción mínima adecuada al lenguaje, coste, sensibilidad de datos y capacidad de exportar evidencia. Si falta una herramienta, consulta `references/08-installation-managers.md` para ofrecer rutas verificables con **asdf-vm, mise y/o Homebrew**; detecta primero los gestores presentes y diferencia una CLI de una dependencia del proyecto. No instales herramientas ni edites archivos del repositorio sin permiso. Las herramientas son opcionales y no constituyen dependencias de esta skill. Una alerta automática es un candidato, no un defecto probado. **Cierre:** cada herramienta elegida responde a una pregunta y se registra versión, configuración, comandos y limitaciones, o se describe una alternativa manual.

5. **Contrasta los candidatos.** Recupera `archivo:líneas` y símbolo, vincula dos lados de cada dependencia o incompatibilidad, reproduce el fallo con una prueba mínima segura o formula una verificación pendiente. Distingue explícitamente `EJECUTADO`, `CÓDIGO`, `DOCUMENTADO`, `HISTÓRICO`, `INFERIDO`, `NO VERIFICADO`. Valida falsos positivos (generados, test fixtures, reflexión, dependencias dinámicas, compatibilidad, invariantes intencionales). **Cierre:** ninguna inferencia, porcentaje, CVE, afirmación de ausencia o estado de CI se presenta como medida sin respaldo.

6. **Ejecuta verificaciones proporcionadas al riesgo.** Consulta `references/06-test-ci-performance.md`: diff → tests focales y contratos afectados; integración/release → gates integrales exigidos en el repositorio y CI *del nuevo SHA*. Separa fallo real, timeout, flakiness, test omitido y no ejecutado; no cambies configuración, instales herramientas, provoques carga ni lances tests destructivos sin autorización. **Cierre:** resultados, comandos, entorno, SHA y cobertura del alcance constan o figuran pendientes; un badge o recibo antiguo nunca certifica el HEAD nuevo.

7. **Emite un informe accionable.** Usa `assets/report-template.md` y los criterios de severidad de `references/01-evidence-workflow.md`. Cada hallazgo confirmado: **Severidad / Ubicación / Evidencia / Impacto / Recomendación**, *en ese orden*, con criterio reproducible de cierre. Separa defectos confirmados, deuda histórica, riesgos plausibles, propuestas y lagunas. Prioriza acciones sin inventar métricas; no crees hallazgos para completar cuotas. **Cierre:** otro agente puede repetir cada comprobación y distinguir lo observado de lo que falta medir.

## Reglas invariantes

- Una convención (hexagonal, ADTs sellados, programación funcional, OTel, cobertura porcentual o la existencia de benchmarks) **no es universal**; pregunta si hay motivo técnico o requisito explícito antes de declararla incumplida.
- `grep` de imports ≠ grafo completo: contrasta manifests/build, referencias de código, codegen, reflexión/carga dinámica y dependencias de runtime pertinentes. Ausencia de coincidencia ≠ ausencia global.
- La connascence estática se analiza como *pares de elementos que deben cambiar juntos* (nombre, tipo, significado, posición, algoritmo); no declares “baja/alta” o un índice como SCIJ sin método validado, alcance y medición. No extrapoles una métrica Java a otro lenguaje.
- La cobertura describe lo instrumentado, no la calidad de las assertions. Un test presente no ha pasado; un workflow presente no ha ejecutado; un informe de otra revisión no acredita el SHA auditado.
- Seguridad: no reportes secretos en claro ni envíes muestras a terceros. Una vulnerabilidad de dependencia solo aplica tras comprobar paquete, versión, ruta y contexto reales.
- La salida válida puede ser **0 defectos confirmados + verificaciones pendientes**. Indica limitaciones relevantes y nunca afirmes haber ejecutado comandos que no se ejecutaron.

## Material bajo demanda (lectura directa, un salto)

- `references/01-evidence-workflow.md`: etiquetas de evidencia, búsquedas, falsos positivos, severidad y gestión del alcance; siempre que se emita una auditoría.
- `references/02-dimensions-playbook.md`: 12 fichas «pregunta → extracción → contraste → anti-falso-positivo → evidencia»; en toda auditoría global o al revisar cada dimensión.
- `references/03-architecture-connascence.md`: límites hexagonales, excepciones legítimas, SOLID, funcional y connascence; solo al analizar diseño.
- `references/04-language-recipes.md`: comandos de diagnóstico por lenguaje; solo para stacks detectados.
- `references/05-tool-catalog.md`: **anexo de herramientas externas con enlaces oficiales, usos y límites**; cuando el análisis demande medición o automatización.
- `references/08-installation-managers.md`: **anexo opcional de instalación** para CLIs/runtimes con asdf-vm, mise y Homebrew; consulta al sugerir herramientas ausentes; exige detección, permiso, verificación del paquete y versión fijada.
- `references/06-test-ci-performance.md`: selección de tests, matrices, CI SHA, rendimiento y observabilidad; cuando corresponda.
- `references/07-security-supply-chain.md`: amenazas, controles, CVEs, SBOM y manejo de secretos; cuando corresponda.
- `assets/report-template.md`: informe final; `examples/example-audit.md`: ejemplo sintético; `tests/skill-evals.md`: pruebas de la *skill*, solo al modificarla.
- `scripts/context_inventory.py`: **opcional**, inventario de archivos de configuración y revisión Git en JSON, sin ejecutar scripts del repositorio. No emite juicios de calidad ni busca contenido sensible.
