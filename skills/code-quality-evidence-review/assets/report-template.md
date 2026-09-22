# Informe de auditoría de calidad — <repositorio / revisión>

**Fecha:** <fecha> · **Alcance:** <PR/focal/global/release> · **SHA auditado:** <hash/no disponible> · **Base:** <hash/no aplica> · **Árbol:** <clean/dirty/no accesible> · **Ecosistemas:** <lenguajes y herramientas> · **Permisos/límites:** <descripción>

## 1. Resumen ejecutivo, estrictamente respaldado

<Qué se ha validado; qué no; hallazgos confirmados vs hipótesis; posible efecto en la decisión de integración sin inventar verde/rojo. No hay obligación de producir hallazgos.>

## 2. Alcance y arquitectura realmente observada

<Gráfico textual o tabla de unidades y contratos. Exclusiones: generated, tests, módulos no accesibles, versiones de producto, runtime no inspeccionado. Fuentes/documentos y su vigencia.>

## 3. Matriz de las doce dimensiones

| ID | Dimensión | Pregunta y ámbito | Evidencia (ID + SHA/ruta/comando/run) | Estado | Lagunas y comprobación siguiente |
|---|---|---|---|---|---|
| D01 | Arquitectura y límites | | | CONFIRMADO / PARCIAL / NO VERIFICADO / NO APLICA | |
| D02 | SOLID y tipado funcional | | | | |
| D03 | Connascence estática | | | | |
| D04 | Duplicidad, acoplamiento, cohesión, complejidad | | | | |
| D05 | Deuda técnica | | | | |
| D06 | Tests y cobertura | | | | |
| D07 | CI/CD | | | | |
| D08 | Seguridad | | | | |
| D09 | Rendimiento | | | | |
| D10 | Dependencias y licencias | | | | |
| D11 | Documentación y mantenibilidad | | | | |
| D12 | Observabilidad | | | | |

`CONFIRMADO` en una dimensión significa **evidencia suficiente para la afirmación concreta**, no “toda la dimensión cumple”. Si la revisión es focalizada, marca las excluidas con motivo; no rellenar con conjeturas.

## 4. Hallazgos con evidencia

### H-01 — <título concreto>

**Severidad:** <BLOQUEANTE / ALTA / MEDIA / BAJA / INFORMATIVA> — <por qué, según alcance y criterio>.

**Ubicación:** `<ruta>:<línea-inicio>-<línea-fin>`; <símbolo/componente, o id de run/job de CI>; <SHA>.

**Evidencia:** <`EJECUTADO / CÓDIGO / DOCUMENTADO / HISTÓRICO / INFERIDO / NO VERIFICADO`; archivo y código mínimo, consulta/comando real, resultado/error, norma aplicable, alcance e hipótesis alternativas>.

**Impacto:** <mecanismo causal, afectado, OBSERVADO/POTENCIAL y límites de la demostración>.

**Recomendación:** <acción mínima o comprobación que falta + criterio de cierre / test reproducible en revisión nueva; rollback cuando aplique>.

**Clasificación opcional:** <REGRESIÓN / PREEXISTENTE / DEUDA ACEPTADA / RIESGO / PROPUESTA / PENDIENTE>.

<Repetir por cada hallazgo real. Si no hay ninguno confirmado, escribir “Sin defectos confirmados en el alcance verificado”, no fabricar H-01. Separar recomendaciones que no derivan de defectos.>

## 5. Ledger de evidencia

| ID | Fuente/categoría | SHA/fecha | Ubicación/comando | Alcance y exclusiones | Resultado real | Límite de inferencia |
|---|---|---|---|---|---|---|
| E-01 | | | | | | |

## 6. Tests y gates

| Gate | Estado (PASA/FALLA/NO EJECUTADO/NO APLICA) | SHA/run/caso/comando | Tests/jobs efectivamente ejecutados | Faltantes y por qué |
|---|---|---|---|---|
| Local focal | | | | |
| Integración | | | | |
| Release | | | | |

**No declarar aceptación de release o CI verde** cuando faltan runs, jobs, artefactos o coincidencia SHA. Diferenciar timeouts de fallos del SUT.

## 7. Plan incremental, riesgo y verificaciones pendientes

| Acción | Vinculación H-XX/E-XX | Experimento/cambio mínimo | Test de cierre | Momento (desarrollo/integración/release) |
|---|---|---|---|---|
| | | | | |

**Fuera de alcance:** <lista breve de sistemas/rutas no estudiadas>. **Limitaciones del pase:** <permisos, datos, herramientas, tiempo de ejecución>. **Sin medidas:** <métricas solicitadas que no se obtuvieron, sin inventar números>.
