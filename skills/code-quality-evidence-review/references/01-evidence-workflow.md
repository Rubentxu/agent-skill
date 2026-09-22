# Evidencia, método de indagación y severidad

## El protocolo operativo

1. Registra `repo`, ruta raíz, rama, HEAD, base, estado de trabajo, fecha y límites de acceso. Si se dispone de Git: `git rev-parse HEAD`; `git status --short`; `git diff --name-status <base>...HEAD` si hay base válida. En un archivo aislado, usa el hash del archivo y marca `sin SHA de repositorio`.
2. Forma hipótesis **falsables**: «dominio importa adaptador», «dos componentes interpretan distinto el mismo estado», «este input no limita expansión», «CI del SHA no ejecutó un job requerido». Define *qué resultado la refutaría*.
3. Localiza productor y consumidor; no infieras arquitectura de nombres de carpetas. Para cada regla: origen (ADR/contrato/riesgo demostrado), universo revisado, búsqueda o grafo, muestra positiva, contraejemplos, validación.
4. Si usas búsqueda, registra patrones, rutas, inclusiones/exclusiones, código generado, tests, lenguajes y sensibilidad de mayúsculas; diferencia `0 coincidencias en <alcance>` de `ausencia demostrada`.
5. Si usas analizador, anota nombre/versión, reglas, severidad nativa, exclusiones, cobertura de lenguaje, tipo de análisis y falsos positivos. El score de la herramienta no sustituye al hallazgo concreto.
6. Si hay resultado dinámico, conserva comando, exit code, selección de tests, caso, fragmento de output sin secretos, entorno, SHA y run/artefacto. Si no se ejecuta, `NO VERIFICADO` más comando y prerequisitos pendientes.
7. Evita mutar el repo auditado; el script opcional de inventario trabaja por lectura. Herramientas que construyen/descargan dependencias, llaman APIs, indexan remoto, generan datos, reescriben o hacen scans intrusivos requieren autorización adecuada.

## Niveles de evidencia

- **EJECUTADO:** comprobación efectivamente realizada en el pase, con resultado y alcance/entorno.
- **CÓDIGO:** fuente y build observados en ruta/líneas, sin afirmar runtime.
- **DOCUMENTADO:** norma o afirmación hallada en ADR/informe; validar vigencia.
- **HISTÓRICO:** resultado de otro SHA, otra fecha u otro entorno.
- **INFERIDO:** interpretación plausible sin reproducción; separar de defectos.
- **NO VERIFICADO:** evidencia insuficiente o herramienta no disponible.

Un “pasa CI” exige id de run, SHA coincidente, jobs exigidos realmente ejecutados, estado final y reporte/artefactos exigidos; un skip justificado queda explícito. Un test que figura en el árbol no cuenta como ejecutado. Un hallazgo de seguridad generado por un scanner necesita triage de la ruta explotable o del riesgo aplicable.

## Severidad y clasificación

- **BLOQUEANTE:** gate obligatorio de integración/release incumplido o fallo confirmado que invalida el objetivo auditado; especifica condición concreta. `No ejecutado` por limitación de acceso es **gate no acreditado**, no un fallo imaginario.
- **ALTA:** defecto confirmado con impacto significativo demostrado o razonamiento causal verificable (seguridad, datos, contratos críticos, límite arquitectónico exigible).
- **MEDIA:** defecto delimitado con escenario de daño/retrabajo plausible y soportado; severidad no basada solo en un score.
- **BAJA:** deterioro concreto de mantenibilidad, operación o riesgo acotado.
- **INFORMATIVA:** observación, propuesta, hipótesis o medición pendiente; separarla de defectos confirmados.

No escales automáticamente todas las advertencias estáticas a una severidad humana. Explicita alcance, explotabilidad/contexto, barreras, exposición, consumidores y confianza. Marca si es `REGRESIÓN`, `PREEXISTENTE`, `DEUDA ACEPTADA`, `RIESGO`, `PROPUESTA` o `PENDIENTE` cuando proceda.

## Contrato del hallazgo, sin campos omitidos

**H-XX — Título breve**

1. **Severidad:** nivel + justificación de impacto y alcance.
2. **Ubicación:** rutas relativas, líneas, símbolos y componente; para CI workflow/job/run + SHA. Si no hay línea fiable: alcance y razón.
3. **Evidencia:** fuente/categoría, SHA, comandos y resultados *reales*, regla y alcance analizado, contraejemplos relevantes; si es inferencia, decirlo aquí.
4. **Impacto:** mecanismo causal, afectados, observado vs potencial y límites de la demostración.
5. **Recomendación:** modificación mínima o siguiente experimento; test/gate/criterio de cierre reproducible y, cuando sea relevante, mecanismo de rollback.

No incluyas tokens, contraseñas, payloads ofensivos ni rutas privadas innecesarias en el informe. Para fallos sistémicos añade al final referencias a otros hallazgos, sin duplicar el mismo problema bajo doce dimensiones.
