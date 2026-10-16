# Contrato canónico de investigación — SOLO CogniCode CLI/MCP

## Alcance y precedencia

Esta política es normativa para `SKILL.md`, lentes, formatos, ejemplos, scripts, validadores, proyectores, agente y subagentes. Si cualquier otra guía recomienda abrir el checkout, leer Git, inspeccionar YAML/README/ADR, usar shell/grep/GitHub, otro indexador o agentes exploradores **como fuente arquitectónica**, esa instrucción queda revocada. No existe «fallback seguro» a lectura directa.

### Matriz de acceso

| Actor | Puede leer | Prohibido |
|---|---|---|
| Agente | archivos de esta skill, entradas de diagrama suministradas, artefactos derivados en HOME; **respuestas CogniCode** | archivos del repositorio objetivo mediante cualquier herramienta distinta de CogniCode |
| Subagente | preguntas y evidencia CogniCode delegadas; CLI/MCP CogniCode con límite idéntico | exploradores genéricos, GitHub, terminal para leer repo, IDE/búsqueda local |
| CogniCode CLI/MCP | repositorio objetivo para analizarlo (responsabilidad de CogniCode) | no altera este contrato |
| Scripts de skill | sus propios assets y workspace derivado, comprobación de la ruta `--repo` | analizar contenido del repo o ejecutar Git contra él |
| Proyectores | diagramas, SVG/PNG, atlas, fuentes del workspace externo | montar o investigar checkout Git; decidir arquitectura |

No usar documentos **aunque CogniCode los devuelva** para probar arquitectura. Solicitar símbolos, AST, enlaces a código y fragmentos de implementación mediante CogniCode. Las afirmaciones del usuario o los diagramas previos pueden servir para plantear **preguntas**, nunca para afirmar implementación.

## Bucle activo obligatorio

1. **Discovery runtime**: invocar ayuda/capabilities reales de CogniCode y `tools/list` paginado si existe MCP. Registrar versión, perfil, herramientas, esquemas y estado. Prohibido adivinar un comando. Si no existe soporte para una pregunta, indicar `UNSUPPORTED` o `PARTIAL`.
2. **Preguntar por la implementación**: identificar entradas (CLI/HTTP/eventos), ejecución, módulos, responsabilidades, símbolos, dependencias, stores, protocolos y fronteras. Preguntar específicamente qué información permite distinguir componente de biblioteca o proceso.
3. **Consulta de desambiguación**: ante un símbolo ambiguo, una arista no resuelta o un límite de C2/C3, consultar de nuevo con scopes, símbolos, referencias y subgrafos más pequeños. Si se pide más detalle, **deben observarse nuevas consultas**, no ampliar solo el dibujo.
4. **Contraste con código**: solicitar a CogniCode código/fragmentos y referencias de líneas de los dos extremos de cada arista relevante; validar coherencia con grafo. La herramienta puede devolver docs; descartarlos como evidencia de arquitectura.
5. **Suficiencia y cobertura**: registrar `complete/partial/unknown/unsupported/failed`, archivos omitidos, truncamientos y vacíos. Métricas de escaneo ≠ cobertura total. «No observado» ≠ «no existe».
6. **Interpretación y output**: separar `OBSERVED_CODE`, `INFERRED`, `UNKNOWN`. Una inferencia nunca puede ser etiquetada como implementación comprobada; omitirla del diagrama factual o señalizar incertidumbre explícita.
7. **Refresco**: si CogniCode no garantiza identidad/frescura del proyecto, no afirmar que un SHA dado basta; marcar base `UNKNOWN/STALE`.

## Afirmación arquitectónica y prueba

Cada entidad/arista debe enlazar a un `claim_id` en `evidence/claims.json` o un informe equivalente:

`{ "claim_id":"R-1", "kind":"relation", "from":"A", "to":"B", "plane":"static", "status":"OBSERVED_CODE", "query_id":"Q-3", "symbols":["A::serve","B::execute"], "code_refs":[{"path":"src/a.rs","line":42}], "limitations":[], "coverage":"partial" }`

La ruta/linea **solo referencia la respuesta de CogniCode**; el agente no abre ese archivo. Para afirmaciones de despliegue o runtime, la arista necesita prueba del plano correcto suministrada por CogniCode. Un simple `calls` no lo demuestra.

Guardar, de forma limitada y sin secretos, un ledger con `query_id`, interface, tool real, argumentos/scope, resumen de salida, snapshot/basis si se proporciona, omisiones, errores y decisiones posteriores. No copiar código masivamente.

## Fallos que cierran la investigación

- CogniCode CLI/MCP inaccesible, fallando o sin herramienta para la pregunta → `BLOCKED` o `PARTIAL` según exista evidencia anterior vigente. No shell, GitHub, Docs ni otro agente explorador.
- Documento contradice código → evidencia de implementación aportada por CogniCode gana; documento ignorado, no se lee directamente.
- Solo índices, grafo o contadores → falta contraste de afirmaciones; `PARTIAL`.
- Información sobre protocolos o procesos no demostrada → `UNKNOWN`; nunca elevar llamada estática a topología runtime.
- Subagente o proyector pide montar repo → rechazar delegación/proyección.

## Separación de certificaciones

`FORMAT_VALID`: archivo aceptado por validador. `RENDERED`: imagen generada. `VISUALLY_REVIEWED`: agente inspeccionó salida. `IMPLEMENTATION_GROUNDED`: **todas las afirmaciones factuales** de esa vista tienen prueba CogniCode, identidad vigente y cobertura declarada. Ninguno implica los otros.
