---
name: cognicode-quality-investigator
description: "Audita la calidad de un repositorio o PR usando CogniCode para localizar símbolos, relaciones e impacto; contrasta cada candidato con código, contratos, pruebas y CI. Úsala para revisar arquitectura, SOLID, connascence, deuda, seguridad o las doce dimensiones de code-quality-evidence-review con CogniCode."
---

# Auditoría de calidad asistida por CogniCode

**Misma metodología que `code-quality-evidence-review`; distinta herramienta de exploración.** Las preguntas, los doce criterios, el nivel de exigencia y el informe son los mismos. CogniCode ayuda a **encontrar** relaciones y candidatos; no emite por sí solo el veredicto. Esta skill es autocontenida: las fichas completas están en `references/quality-criteria.md`.

## Procedimiento

1. **Delimita la revisión.** Fija repositorio, SHA, árbol limpio/sucio, base del diff si es PR, archivos/módulos incluidos y reglas efectivas del proyecto. Para una PR, empieza por el diff y sus consumidores; para una auditoría global, recorre las doce fichas de `references/quality-criteria.md`. **Hecho cuando** cada dimensión relevante tiene una pregunta comprobable y un ámbito; las excluidas tienen motivo.

2. **Consulta CogniCode con una pregunta concreta.** Prioriza `cognicode-mcp` si el agente lo tiene conectado; usa `cognicode` CLI cuando sea la interfaz disponible. Consulta únicamente la herramienta/comando necesarios de `references/cognicode-queries.md`, verificando su nombre y parámetros en la interfaz instalada. Para relaciones entre archivos, construye o refresca el grafo si hace falta y se permiten sus efectos de caché. **Hecho cuando** tienes el resultado real de la consulta, el ámbito explorado y sus limitaciones, o has anotado que no se pudo consultar.

3. **Sigue la pista hasta el código.** Para cada candidato, localiza `símbolo → definición → usos/llamadores → contrato → archivo:líneas`. Distingue llamadas de imports, tipado de comportamiento y conectividad estática de ejecución. Busca explicaciones alternativas: homónimos, interfaces, código generado, tests, DI, reflexión y eventos. **Hecho cuando** el candidato tiene una proposición falsable y enlaces a sus dos extremos o se descarta razonadamente.

4. **Contrasta con una fuente adecuada a la afirmación.** Lee `references/evidence-checks.md`: código y build para arquitectura, compilación/contratos para tipos, tests para comportamiento, CI del SHA para gates, scanners/SBOM para dependencias, benchmark o traza para rendimiento. Dos consultas del mismo grafo —también MCP y CLI sobre el mismo motor— no son corroboración independiente. **Hecho cuando** cada conclusión está respaldada por evidencias suficientes o se declara `NO VERIFICADO`, sin confundir resultado vacío con ausencia demostrada.

5. **Entrega el informe.** Usa `assets/report-template.md`. En cada hallazgo conserva exactamente **Severidad → Ubicación → Evidencia → Impacto → Recomendación**, en ese orden, con prueba de cierre. Separa confirmados, hipótesis, deuda histórica y verificaciones pendientes; indica tests realmente ejecutados y CI del SHA. **Hecho cuando** otro agente puede repetir las comprobaciones y ninguna dimensión revisada tiene una conclusión sin fuente o límite explícito.

## Reglas breves

- Un grafo parcial, cacheado sin vigencia comprobable, con archivos omitidos o aristas ambiguas no permite concluir «no hay incidencias». `get_hot_paths` no mide latencia; `trace_path` no es traza runtime; `get_complexity` necesita parser válido. No inventes una métrica de connascence.
- Hexagonal, ADTs, programación funcional u observabilidad son exigencias solo cuando existe contrato del proyecto o consecuencia técnica demostrable. Una alerta o un score no es automáticamente un defecto.
- No instales herramientas, ejecutes scripts desconocidos, reescribas archivos ni transmitas código privado sin permiso. Comprueba el efecto de los comandos que generan caché/índice. Si CogniCode no está disponible, sigue el mismo procedimiento mediante lectura y herramientas ya autorizadas; declara la limitación.
- No afirmes haber ejecutado pruebas, benchmark, CLI o MCP sin una salida observada. Una certificación antigua o un workflow configurado no acredita el SHA actual.

## Consulta bajo demanda

- `references/cognicode-queries.md`: qué operación de CogniCode utilizar para cada pregunta, y su alternativa CLI. **Leer solo al seleccionar consultas.**
- `references/quality-criteria.md`: doce dimensiones y criterio completo de revisión original. **Leer las fichas que correspondan al alcance.**
- `references/evidence-checks.md`: suficiencia, falsos positivos, severidades, tests/CI y seguridad. **Leer al validar un hallazgo o un gate.**
- `assets/report-template.md`: salida; `examples/hexagonal-investigation.md`: ejemplo sintético; `tests/skill-evals.md`: evaluaciones de la skill, no parte de la auditoría ordinaria.
