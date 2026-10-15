---
name: delivery-first-testing
description: "Orquesta verificación rápida orientada a entrega de valor en cambios, features, merges, integración y releases. Descubre lentes de impacto, UAT efímero, regresión, fallos, salud del harness y certificación mediante affordances HATEOAS-like; selecciona tests por riesgo, evita duplicados y no exige full suite en cada iteración."
---

# Delivery-First Testing — una entrada, lentes bajo demanda

**Objetivo:** maximizar funcionalidades consumibles entregadas con evidencia suficiente y coste de feedback controlado. **No** maximizar número de tests, contratos, recibos o gates. Es UNA skill instalable, no un nuevo framework CI, harness, servidor REST, MCP ni motor de conocimiento.

## Ontología y límites

- **Capacidad**: comportamiento observable que importa al consumidor. **Garantía**: propiedad que no puede romperse. **Prueba**: instrumento para contrastarla; nunca la identidad de una garantía.
- **UAT efímero**: exploración o aceptación vinculada a una feature, descartable al cerrar el ciclo **después** de registrar el resultado y decidir si hace falta protección permanente.
- **Regresión permanente**: comprobación pequeña, determinista y discriminante de una garantía crítica o sin cobertura equivalente. No promocionar automáticamente todos los UAT.
- **Lente**: pregunta especializada sobre el cambio. No es una skill instalada ni ejecutor. **Affordance**: acción que puede hacerse ahora según datos observados, con `rel` + `href` local a una guía; NO es URL HTTP ni implica ejecución.
- **Evidencia vigente**: resultado asociado a código/revisión/artefacto y alcance observados. No llamar verde a `SKIP`, caché sin contexto, binario obsoleto, falsa salida cero ni prueba no ejecutada.

## Router: observar, descubrir, actuar, volver a observar

1. Reconocer intención `feature | merge | integration | release | audit | catalog`, garantías afectadas, riesgo, consumidor y política real del proyecto. Leer primero wrappers reales de Cargo/Gradle/Vitest/Playwright/PipelineK; no inventar comandos ni un segundo orquestador CI.
2. Usar [lens-registry.json](references/lens-registry.json), el [descubrimiento de skills disponibles](references/related-skills.md) y [navegación](references/navigation.md) para seleccionar lenses `ready` según señales y precondiciones. `planned` no es ejecutable. Helper **puro** opcional: `python3 scripts/affordances.py examples/session-feature.json` (solo calcula enlaces, nunca ejecuta tareas).
3. Leer únicamente el playbook de la lente anunciada y los archivos productivos realmente necesarios. El catálogo sugiere; el agente contrasta código, dependencias, riesgo y evidencias. Si el helper no está disponible, aplicar las mismas reglas manualmente sin inventar estados.
4. Ejecutar **solo pruebas afectadas y contratos críticos relacionados** en desarrollo. Los cambios transversales, seguridad, persistencia, identidad, despliegue y compatibilidad pueden exigir más fidelidad. No usar selección heurística para afirmar que un riesgo desconocido está cubierto.
5. Para una feature, crear y usar escenarios UAT **temporales** si requieren demostración real; preferir herramienta existente o exploración CLI/browser a crear E2E permanente. Confirmar observabilidad: asserts sobre comportamiento, timeout limitado, entorno aislado y fallo discriminante. Nada de sleeps fijos, snapshots globales ni readme-tests para justificar una feature.
6. Al cerrar feature, decidir `promote | replace | retire`: conservar la menor prueba que proteja una garantía sin cobertura; registrar por qué un UAT se descarta y qué evidencia de aceptación produjo. Nunca borrar tests legacy automáticamente ni perder protección de fallos críticos.
7. En merge usar [impacto](references/lenses/change-impact.md) y verificación selectiva [merge](references/lenses/merge-assurance.md). Suite completa en integración o RC según autoridad del proyecto; certificación de instalación/publicación solo sobre artefacto real. **La integración puede fallar y requerir revert o arreglo antes de release**.
8. Reinspeccionar después de cada acción; no declarar `PASS` por una intención o un plan. Informe final mínimo: capacidad, revisión/artefacto, garantía, comprobación ejecutada/no ejecutada, resultado, UAT retirados/promovidos, riesgos residuales, siguiente acción para entregar.

## Contratos no negociables

- Ninguna prueba que observe fugas de secretos, pérdida de datos, integridad, aislamiento, persistencia o concurrencia se elimina sin cobertura equivalente demostrada y decisión justificada.
- Priorizar refactor-safe: prueba pública/dominio antes que estructura privada. No cristalizar rutas, número exacto de archivos, textos de logs, DOM interno o implementación salvo que formen parte explícita del contrato.
- Un test rojo se clasifica: defecto real, contrato intencionadamente cambiado, test acoplado, infraestructura, dato/fixture, flaky, stale/missing evidence. **No cambiar el producto para satisfacer tests obsoletos** ni desactivar el gate para obtener verde.
- Repetición de un mismo fallo no habilita retries ilimitados. Reportar coste, hipótesis y solución mínima. No prolongar el ciclo exclusivamente para aumentar cobertura sin nuevo riesgo.
- Mantener CI existente como autoridad única; esta skill no crea nuevos pipelines, catálogos normativos ni archivos de estado dentro del repositorio por defecto. Scripts temporales/evidencias sensibles fuera de Git, bajo directorio temporal aislado de la sesión (y con limpieza explícita tras comprobación).
- **No borrar, instalar, publicar, hacer push ni merge sin la autorización correspondiente.** El helper no ejecuta acciones. No transmitir datos privados a servicios externos.
- Si falta herramienta/artefacto, una prueba queda `BLOCKED`/`NOT_RUN`, nunca aprobada por defecto. Todo `SKIP` relevante requiere razón.
- No obligar a `--rerun-tasks --no-build-cache` en el inner loop. Usar caché correcta y procedencia verificable; escalar sólo cuando la identidad o el contexto invalidan la evidencia.

## Rutas disponibles (leer solo la necesaria)

| Intención | Lente primaria | Condición de cierre |
|---|---|---|
| Feature | [impacto](references/lenses/change-impact.md) → [UAT efímero](references/lenses/ephemeral-uat.md) → [promoción](references/lenses/regression-promotion.md) | comportamiento aceptado + evidencia afectada + decisión de regresión |
| Merge | [merge](references/lenses/merge-assurance.md) | chequeos seleccionados realmente ejecutados + resultado inequívoco |
| Integración | [integración](references/lenses/integration-assurance.md) | suite/contexto de integración ejecutados; corregir/revertir si rojo |
| Release | [release](references/lenses/release-assurance.md) | artefacto de distribución realmente instalado/ejecutado y verificado |
| Fallos repetidos | [triaje](references/lenses/failure-triage.md) | causa clasificada + corrección o cuarentena controlada |
| Harness pesado | [economía](references/lenses/harness-economics.md) | duplicidades/tiempos medidos + eliminación o reubicación justificada |
| Diseñar nuevas lentes | [extensión](references/extend-lenses.md) | preguntas, señales, contraejemplos y tests de routing |

## Definición de valor entregado

- El usuario/consumidor puede usar la capacidad, o se declara claramente el impedimento.
- Se observaron los tests baratos adecuados; los fallos y skips no se ocultaron.
- Las pruebas temporales tienen cierre: usadas, evidenciadas, decididas, retiradas o promovidas.
- El gate no se volvió más grande por defecto; las nuevas comprobaciones permanentes tienen justificación y coste medible.
- Para RC, la comprobación se hizo sobre distribución y artefactos reales, no solo árbol fuente.

[Ejemplos](examples/session-feature.json) · [Criterios de evidencia](references/evidence.md) · [Evaluaciones de la skill](tests/skill-evals.md)
