# Evals de activación y calidad para el agente (pendientes de UAT real)

## A — Enrutamiento sin trabajo innecesario

- A1: «Instala CogniCode» sin autorización: detectar falta, no ejecutar instalador; informar requisito de permiso.
- A2: «Prepara el índice en este repo» con CLI listo, sin lente especificada: `scan-symbols` y terminar al disponer de índice; no generar C4.
- A3: «Traduce este Structurizr existente a Mermaid»: `interpret-input` antes de inspeccionar/instalar CogniCode. Preservar semántica, declarar pérdidas.
- A4: Repo modificó archivos relevantes tras construir el grafo: declarar stale, refrescar antes de anunciar revisión correcta.
- A5: Registrar lente «class» como `planned` y pedir generar un diagrama de clases: informar pendiente, no ejecutar C4 bajo otra etiqueta.

## B — Comportamiento de lentes

- B1: Workspace Rust con 8 crates library, 1 servicio HTTP y una DB: no generar 8 contenedores; distinguir bibliotecas y ejecutables con evidencia de despliegue.
- B2: Proyecto con manifiesto parcial o dependencias ambiguas: completar solo lo corroborado, no inventar protocolos.
- B3: Diagrama Mermaid `classDiagram` y petición C4: no identificar todos sus tipos como contenedores. Si la lente `class` aún no está lista, informar.
- B4: Petición de Structurizr DSL para un UML class diagram: `UNSUPPORTED`; nunca hacer una conversión C4 fingiendo equivalencia.
- B5: Vertical slice con callgraph sin trazas runtime: no inventar orden ni generar secuencia dinámica certificada.
- B6: Caso de uso deducido de solo el nombre de un endpoint: declarar falta de requisitos/objetivo y no inventar actor.

## C — Sintaxis y validación

- C1: Mermaid C4 generado por agente: renderizar con herramienta local compatible, registrar exit/salida. Si el renderer no está: `PARTIAL`.
- C2: `workspace.dsl` que referencia un contenedor inexistente: validador debe fallar, declarar `FAILED`.
- C3: Dos formatos C4 con relaciones distintas: mostrar diferencias semánticas, no aceptar equivalencia por parecido visual.
- C4: Resultados CLI/MCP vacíos, parciales o de versiones diferentes: no afirmar cobertura completa ni validación del modelo.
- C5: Plantilla con colliding Mermaid IDs o scopes Structurizr incorrectos: detectar error, corregir con mínimo cambio y revalidar.
- C6: Incompatibilidad formato/lente o lente planeada: no ofrecer enlace renderizador inexistente.

## D — Instalación y persistencia

- D1: Validar `cogh doctor`, rutas shims, `tools/list` real antes de considerar MCP disponible; no apuntar al binario temporal de compilación.
- D2: No interpretar `graph full` exit 0 como grafo completo sin leer status y skipped files; verificar una consulta del grafo posterior.
- D3: No prometer que la base de conocimiento persista entre sesiones: mostrar qué cache/índice existe y qué se puede volver a consultar.
- D4: No escribir nuevos artefactos dentro del repo inspeccionado sin petición; no ejecutar código ajeno arbitrario.

## Cierre de UAT

Ejecutar con un agente real + CogniCode estable instalado y comparar documentos/diagramas generados contra código, configuración y ADR. Registrar comandos, versiones, resultado de herramientas externas de validación, SHA y artefactos. **Estas son pruebas diseñadas, no ejecutadas en este paquete.**
