# Informe CogniCode Quality Investigator — <repo> @ <SHA>

**Alcance:** <global/focal/PR/release>. **Fecha:** <fecha>. **Base diff:** <SHA/null>. **Dirty:** <sí/no/desconocido>. **Permisos:** <read-only/etc.>. **Fuentes realmente ejecutadas:** <lista concreta o NINGUNA>.

## 1. Inventario y límites

| Servidor/fuente | Versión | Tools reales/schema capturados | Workspace/basis | Estado | Límites |
|---|---|---|---|---|---|
| cognicode-mcp | | | | NOT_RUN | |
| explorer-mcp | | | | NOT_RUN | |
| Git/build/test/CI | | | | NOT_RUN | |

**Grafo:** estrategia, fecha/manifest/config, archivos esperados/analizados/omitidos, aristas resueltas/no resueltas, lenguajes y soporte, caché, salidas truncadas, falsos negativos conocidos. **No llamar «cobertura de tests» a cobertura de grafo.**

## 2. Matriz de doce dimensiones

| ID | Dimensión | Fuente CogniCode/consulta real | Contraste independiente | Estado | Exclusiones/lagunas |
|---|---|---|---|---|---|
| D01 | Arquitectura y límites | | | | |
| D02 | SOLID y tipado funcional | | | | |
| D03 | Connascence estática | | | | |
| D04 | Duplicidad/acoplamiento/cohesión/complejidad | | | | |
| D05 | Deuda técnica | | | | |
| D06 | Tests y cobertura | | | | |
| D07 | CI/CD | | | | |
| D08 | Seguridad | | | | |
| D09 | Rendimiento | | | | |
| D10 | Dependencias/licencias | | | | |
| D11 | Documentación y mantenibilidad | | | | |
| D12 | Observabilidad | | | | |

## 3. Hallazgos con evidencia (solo confirmados; no rellenar por cuota)

### H-01 — <título>

**Severidad:** <BLOQUEANTE/ALTA/MEDIA/BAJA/INFORMATIVA + motivo contextual>.

**Ubicación:** `<ruta>:<inicio>-<fin>` y símbolos, commit exacto o job/run.

**Evidencia:** IDs de ledger, regla demostrable, comandos/consultas ejecutadas, extracto y resultado, base del grafo, confirmación independiente y evidencia en contra inspeccionada. Estado de análisis (`CONFIRMADO/PARCIAL/...`) y límites.

**Impacto:** mecanismo causal, consumidor afectado, observado frente a potencial y condiciones necesarias.

**Recomendación:** acción focal, oráculo reproducible de cierre, tests afectados, momento de integración y rollback si procede.

## 4. Hipótesis, contradicciones, deuda histórica y cobertura faltante

<No mezclar con hallazgos confirmados. Registrar extractores correlacionados, homónimos, reflexión, archivos omitidos, cambios de base y resultados negados.>

## 5. Ledger de evidencia

| E-ID | SHA/basis | Fuente/versión/schema | Tipo (SOURCE/GRAPH/EXECUTION/HISTORY/DOCUMENTED/HYPOTHESIS) | Entrada y ámbito | Salida/ubicación/digest | Estado | Límite |
|---|---|---|---|---|---|---|---|

## 6. Tests/CI/performance

| Gate/benchmark | SHA/comando/run | Entorno/dataset | Resultado realmente observado | Pendiente |
|---|---|---|---|---|

## 7. Plan incremental

| H/E | Acción mínima | Verificación focal | Gate de integración/release | Dependencia/permiso |
|---|---|---|---|---|