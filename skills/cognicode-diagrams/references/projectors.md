# Proyectores locales — ciclo de vida y límites

## Responsabilidad única

**Los proyectores consumen archivos de diagramas que el agente ya creó**. Nunca montan el checkout Git ni invocan CogniCode. No se habilitan MCP de LikeC4/Structurizr, análisis automatizado de repositorios ni servicios remotos. La salida visible no se convierte en fuente de verdad sobre código o arquitectura.

| Proyector | Entrada que genera el agente | Superficie | Procedimiento |
|---|---|---|---|
| Kroki local | Mermaid `.mmd`, Structurizr `.dsl`, PlantUML `.puml` | SVG/PNG | [Kroki](kroki.md) |
| LikeC4 local | LikeC4 `.c4`/`.likec4` | UI web interactiva, vistas y drill-down | [LikeC4](projectors/likec4.md) |
| Markmap (atlas) | Markdown `navigation/atlas.md` derivado de renders/sources | HTML interactivo, miniaturas/enlaces a SVG/PNG y visores locales | [Markmap](projectors/markmap.md) |
| Structurizr Local | `workspace.dsl` | UI web C4 interactiva C1/C2/C3 | [Structurizr Local](projectors/structurizr-local.md) |

No se crea un formato universal: la lente decide las entidades y relaciones; las recetas de formato enseñan al agente a escribir cada archivo de manera explícita. Los motores interpretan **solo el DSL**, no el repositorio.

## Workspace y contenedores

Antes de llamar a `projectors.py`, comprobar `scripts/workspace.py inspect` y `init-lens`. Siempre fuentes bajo `~/.cognicode-diagrams/workspaces/<repo>--<id>/lenses/<lente>/sources/`. No copiar ni montar código, ADR privados ni `.git` por defecto. Cuando se pidan explicaciones arquitectónicas, primero CogniCode y las evidencias autorizadas.

`python3 scripts/projectors.py status|start|stop|remove --repo <ruta Git> --projector likec4|structurizr [--engine podman|docker] [--lens c4]`

- `status`: solo inspecciona un contenedor etiquetado con el workspace, la lente y el proyector; `--check-http` consulta únicamente `127.0.0.1`. `running` no significa que el servicio esté listo.
- `start`: operación explícita autorizada; si falta el DSL no inicia. Usa imágenes oficiales, rutas de montaje del workspace externo, binding HTTP a loopback, y `:z` para SELinux/Podman cuando se comparten los archivos.
- `stop`: solo detiene el contenedor propio; **no borra archivos**.
- `remove`: retira el contenedor **propio**, tras parada; no borra imágenes ni fuentes. No se ejecuta automáticamente.
- `--port` y `--hmr-port` permiten resolver conflictos entre varios workspaces. Los puertos de cada contenedor ya existente no se cambian implícitamente.

La imagen LikeC4 se referencia actualmente como `likec4/likec4:latest` (tag móvil); la de Structurizr como `structurizr/structurizr:2026.09.19`. Registrar imagen/digest en las evidencias de UAT al reproducir una ejecución y fijar los digests para despliegues estrictamente reproducibles.

## HATEOAS y verificación

Para `intent=preview`, el agente elige `projector=likec4-local` con `formats=["likec4"]`, o `projector=structurizr-local` con `["structurizr"]`. La navegación solo anuncia `inspect-projector`, `start-projector`, `open-projector` o `review-layout` si cumplen precondiciones observadas. Un contenedor corriendo no habilita `VERIFIED`: requiere HTTP local observado, origen de los archivos válido, comprobación de sintaxis y revisión visual ejecutada. La revisión semántica **se acredita por separado** mediante CogniCode y la lente.

Usar [validación](validate.md), [evidencias](evidence.md), [workspace](workspace.md) y [navegación](navigation.md). UAT con Podman/Docker real pendiente hasta observar el proceso, no se sustituye por mocks.

## Atlas Markmap

`intent=atlas` ofrece un índice **transversal** de las lentes ya generadas. Se crea únicamente bajo `navigation/` en el workspace externo y no añade análisis ni un modelo canónico nuevo; permite seguir enlaces a visores interactivos solo tras observar que el contenedor responde en localhost. Markmap se ejecuta sin servicio permanente mediante [procedimiento](projectors/markmap.md), preferentemente con Podman.
