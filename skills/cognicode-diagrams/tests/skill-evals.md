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

## E — Aislamiento de proyecto bajo HOME

- E1: ``/projects/pipelinek`` ⇒ `~/.cognicode-diagrams/workspaces/pipelinek--<hash>/`; no creaciones dentro de Git.
- E2: dos repositorios distintos con el mismo basename ⇒ workspaces diferentes; un subdirectorio ⇒ misma identidad Git.
- E3: directorio de HOME dentro del worktree, symlink de `.cognicode-diagrams` a la raíz Git, `../` o ruta absoluta ⇒ rechazar.
- E4: `workspace.json` de otro repositorio ⇒ bloquear sin sobrescritura ni migración automática.
- E5: intents `create`, `scan`, `preview` con workspace desconocido/ausente ⇒ `inspect-workspace`/`init-workspace` antes de generación o proyección.
- E6: `init-lens` solo crea carpetas de la lente solicitada; fuente/imagen/trazas no se duplican en Git.

## Cierre de UAT

Ejecutar con un agente real + CogniCode estable instalado y comparar documentos/diagramas generados contra código, configuración y ADR. Registrar comandos, versiones, resultado de herramientas externas de validación, SHA y artefactos. **Estas son pruebas diseñadas, no ejecutadas en este paquete.**

## Kroki (sin tocar CogniCode)

- Gateway solo + `Structurizr` → se ofrece previsualización Structurizr.
- Gateway solo + Mermaid → no ofrecer renderización Mermaid sin companion.
- Lente C4 y `intent=preview` con fichero fuente → no instalar ni escanear CogniCode por defecto.
- Kroki ausente + no autorización → solo bloquear/explicar, no lanzar Docker.
- Kroki con permiso → mostrar procedimiento compose local, no lanzar nube.
- Salida SVG/PNG real tras POST → `RENDERED`, mantener validación de ontología separada.
- HTTP 400, 302 o respuesta HTML → no sobrescribir imagen anterior.
- Structurizr con varias vistas → `view-key` por cada vista solicitada.
- Contenido privado → no POST a un dominio externo, ni derivar URL GET con contenido del código.
- UAT opcional con Docker/Podman real → solo cuando el usuario autorice el arranque, no en tests unitarios.

## Proyectores LikeC4 y Structurizr Local — UAT/AAT pendientes de ejecutar

- P1: proyecto Git limpio; el agente usa CogniCode real y escribe `model.c4` + `workspace.dsl` **solo en HOME**; Git status permanece idéntico.
- P2: Podman rootless/SELinux: arranque LikeC4, HTTP 200 local, `/view/index` navegable, HMR funcional; el agente verifica un detalle y anota la revisión visual.
- P3: Podman rootless/SELinux: arranque Structurizr Local contra `workspace.dsl`, navegación C1/C2/C3 y lectura sin permisos de edición; comprobar que no se crea nada en Git.
- P4: `start` no se ejecuta sin autorización explícita, no abre puertos públicos ni manda DSL a servicios externos.
- P5: dos clones llamados igual crean contenedores/paths distintos y ninguno puede controlar el del otro.
- P6: conflicto de puertos o contenedor con mismo nombre y etiquetas ajenas => fallo cerrado; stop/remove solo del contenedor propio.
- P7: LikeC4 `validate` falla sobre DSL inválido => no declarar `VERIFIED`; HTTP 200 por sí solo no significa vista inspeccionada.
- P8: modificaciones del `.c4` y `.dsl` en HOME se reflejan en las vistas sin volver a escanear CogniCode; cambios en el código requieren reconciliación previa.
- P9: un diagrama LikeC4 no debe enviarse a Kroki ni inferirse automáticamente de Structurizr DSL.
- P10: ejecución idéntica bajo Docker en entorno donde Podman no está instalado, con puertos configurables.

Hasta ejecutar estos UAT con Podman/Docker, reportar **integración y mocks**, no certificación OCI real.

## Markmap — atlas de navegación

- M1: A partir de `.dsl`, `.mmd` y SVG, generar `navigation/atlas.md` con imágenes y enlaces relativos válidos, sin abrir ni modificar el checkout Git.
- M2: Solo ofrecer LikeC4/Structurizr como links cuando contenedores etiquetados para **ese** workspace estén HTTP ready; sin ellos, enlaces SVG funcionales.
- M3: Imagen alterada, borrada o nueva => `atlas.py check` informa `STALE`; `build` regenera sin escanear CogniCode.
- M4: Enlace simbólico a `.git`, filenames adversarios, HTML previo ajeno, workspace inseguro => rechazar sin destruir datos.
- M5: Contenedor Podman efímero, sin montar Git ni publicar puertos; sin red por defecto y opt-in explícito si Markmap requiere descargar assets.
- M6: HTML servido/renderizado **no** equivale a inspección visual, y esta tampoco acredita fidelidad semántica.
- M7: UAT real debe comprobar Markmap `--offline` en Podman con red deshabilitada y con SELinux: no anunciarlo como certificado por los mocks.
