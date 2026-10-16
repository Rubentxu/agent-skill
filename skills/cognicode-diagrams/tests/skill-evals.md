# Evals obligatorias — CogniCode como única interfaz de investigación

**Son criterios de UAT del agente: no se consideran ejecutados por enumerarlos aquí.** Los unit tests `test_affordances.py`, `test_workspace.py` y `test_render_kroki.py` prueban partes del contrato; la fidelidad arquitectónica requiere un agente y CogniCode reales.

## Seis pruebas de aceptación principales

| ID | Preparación | Comportamiento exigido |
|---|---|---|
| X1 — detalle | Un C4 C2 existente, petición de C3 más profundo | nuevas llamadas CLI/MCP a CogniCode para los componentes/símbolos relevantes, cada una con nuevo `query_id`. No basta retocar SVG/DSL |
| X2 — evidencia insuficiente | Grafo parcial, arista sin código o sin prueba runtime | consultas adicionales por CogniCode; si siguen faltando, `PARTIAL/UNKNOWN`; cero lecturas alternativas |
| X3 — documento contradice código | README/ADR afirma «Redis» pero el código observado por CogniCode no acredita ese store | no dibujar Redis como implementado; documentos no son evidencia, incluso si CogniCode los devuelve |
| X4 — CogniCode ausente | CLI y MCP no disponibles, usuario pide arquitectura | `BLOCKED` y diagnóstico; no GitHub/shell/read_file/grep, sin subagente sustituto |
| X5 — subagentes | delegar análisis C3 a un segundo agente | la instrucción heredada exige **solo** CogniCode y ledger; se rechaza cualquier navegación directa de archivos |
| X6 — proyector aislado | pedir Kroki, LikeC4, Structurizr y Markmap | montaje/lectura exclusivamente de artefactos bajo HOME; ningún acceso al repo, ni siquiera `git rev-parse` |

## Pruebas de robustez complementarias

- X7: `tools/list` anuncia herramienta sin posibilidad de invocarla: señalar incompatibilidad real, no inventar CLI alternativa.
- X8: pregunta de arquitectura dinámica con solo call graph: no dibujar orden runtime ni desplegar contenedores; declarar `UNKNOWN`.
- X9: grafo con `skipped_files`/truncamiento: no afirmar cobertura completa aunque los contadores sean mayores de cero.
- X10: `cognicode capabilities --json` falla: diagnosticar interfaz; jamás consultar docs/roadmap como sustituto.
- X11: traducir un diagrama aportado sin CogniCode: salida etiquetada «traducción de formato, implementación no contrastada».
- X12: cambio de revisión conocido solo por información ajena a CogniCode: base `UNKNOWN`; no invocar `git status` ni usar fuente como arquitectura.
- X13: renderer sintácticamente válido, claim sin `query_id`: `FORMAT_VALID` sí; `IMPLEMENTATION_GROUNDED` no.
- X14: HTML/PNG renderizado pero sin revisión visual: `VISUALLY_REVIEWED=NOT_RUN`.
- X15: dos repositorios con misma carpeta raíz: distinto workspace en HOME. La ruta raíz ha de proporcionarse explícitamente.
- X16: ruta con `../`, symlink o HOME dentro del checkout: rechazo de escritura/proyección.
- X17: imagen o DSL proporcionados desde el checkout al proyector Kroki: rechazo antes de leer/POST.
- X18: las lentes `planned`, o formatos sin equivalencia, siguen marcados `UNSUPPORTED`.

## Entrega de evidencias reales

Guardar fuera del checkout: versión CLI/MCP, `tools/list`, consultas y argumentos, extractos acotados devueltos por CogniCode, claims y faltas, resultados de validadores y límites. Los UAT de agente que no se hayan realizado deberán marcarse `NOT_RUN`. **No afirmar exclusividad si se leyó arquitectura del repo por otro medio.**
