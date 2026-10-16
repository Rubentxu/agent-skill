# Investigación activa por CogniCode — no inspección directa

**Única superficie autorizada para conocer arquitectura del checkout objetivo: CogniCode CLI/MCP.** Leer antes [investigation-contract.md](investigation-contract.md). No usar Git, shell, grep, scripts propios, GitHub, manifiestos, IaC, README, ADR, tests, documentación ni otros agentes para investigar arquitectura. Aunque CogniCode devuelva documentos, **no usarlos como prueba de código implementado**.

## Descubrimiento primero

- CLI: ejecutar el binario **CogniCode** instalado con `--help` y `capabilities --json` si se anuncia; consultar ayudas específicas para esquemas/flags. No inventar `index`, `graph` o `inspect` por recordarlos de otra versión.
- MCP: `initialize` y `tools/list`, recorriendo `next_cursor` hasta completar el catálogo. Usar los esquemas y permisos anunciados; si `tools/list` declara algo no ejecutable, anotar incidencia y no fabricar un fallback.
- Anotar versiones, perfil, límites, permisos y alcance. Si no hay CLI/MCP operativo → `BLOCKED` sin lectura alternativa.

## Bucle de preguntas y consultas

1. **Entradas**: ¿qué símbolos constituyen `main`, handlers HTTP, comandos, workers o consumidores de eventos? Consultar índices y código mediante CogniCode.
2. **Responsabilidades**: ¿qué tipos, servicios y dependencias implementan cada capacidad? Navegar a símbolos, leer fragmentos por CogniCode y corroborar nombre frente a comportamiento.
3. **Relaciones**: ¿quién invoca a quién, importa qué, persiste dónde? Pedir subgrafos acotados, dependencias, referencias y ambos extremos. Separar `calls/imports` estáticos de ejecución.
4. **Fronteras**: ¿qué demuestra que un ejecutable es un proceso separado, que existe una comunicación runtime, un protocolo o un almacén externo? Pedir evidencias de **código de implementación** por CogniCode; si no responde, `UNKNOWN`.
5. **Profundizar**: petición de «más detalle» o ambigüedad → realizar **nuevas consultas** sobre componentes/símbolos/aristas específicos, no solo ampliar el diagrama.
6. **Verificar**: para cada hallazgo registrar herramienta+argumentos+respuesta+referencia+límites. Las ausencias se formulan como «no observado dentro del alcance», no como «no existe».

Un escaneo general o `build_graph` es solo preparación. `status=complete`, contadores y `skipped_files` no demuestran que la vista C1/C2/C3 sea correcta; un grafo de llamadas no establece topología desplegada. Ante errores parciales, registrar brechas y seguir con consultas acotadas cuando sea posible.

## Coste mínimo

Empezar con consultas de panorama/índice anunciadas, profundizar solo en las zonas necesarias, y construir el grafo cuando una relación lo exija. No escanear indiscriminadamente todo el monorepo. Reutilizar cache de CogniCode solo si la identidad/alcance son verificables; no construir índices alternativos.

## Handoff

Guardar bajo `workspace/evidence/` únicamente el ledger de consultas y claims con cobertura/ambigüedades; usar [evidence.md](evidence.md) y [plantilla](../assets/READINESS-template.md). Los artefactos derivados no son fuentes independientes del código.
