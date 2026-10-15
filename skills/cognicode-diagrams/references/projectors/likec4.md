# LikeC4 — visor interactivo opcional, contenido producido por el agente

**No instalar LikeC4 MCP ni usar LikeC4 para explorar el repositorio.** El agente, guiado por [LikeC4 DSL](../formats/likec4-c4.md), crea fuentes `.c4` desde CogniCode. LikeC4 interpreta sus propios archivos solo para servir vistas y navegación C4.

## Inicio seguro con Podman (recomendado)

```bash
# La ruta --repo identifica el proyecto, pero NUNCA se monta en el contenedor.
python3 scripts/workspace.py init --repo /ruta/a/mi-proyecto
python3 scripts/workspace.py init-lens --repo /ruta/a/mi-proyecto --lens c4
# El agente escribe model.c4 en lenses/c4/sources/ del workspace externo.
python3 scripts/projectors.py status --repo /ruta/a/mi-proyecto --projector likec4 --engine podman
python3 scripts/projectors.py start --repo /ruta/a/mi-proyecto --projector likec4 --engine podman
python3 scripts/projectors.py status --repo /ruta/a/mi-proyecto --projector likec4 --engine podman --check-http
```

Abrir `http://127.0.0.1:5173/` o `http://127.0.0.1:5173/view/index` (cuando existe una vista index). El cliente web usa un segundo puerto HMR en loopback para recarga automática; si están ocupados, indicar puertos libres con `--port` y `--hmr-port` **al crear** el contenedor. Docker puede reemplazar `--engine podman`.

```
python3 scripts/projectors.py stop --repo /ruta/a/mi-proyecto --projector likec4 --engine podman
# Solo si se desea destruir el contenedor concreto:
python3 scripts/projectors.py remove --repo /ruta/a/mi-proyecto --projector likec4 --engine podman
```

## Revisión visual

1. Validar `.c4` en un contenedor efímero o con la CLI LikeC4 (errores de gramática); nunca consultar fuente de código con LikeC4.
2. Verificar vista inicial y al menos una vista de detalle, drill-down, nombres y relaciones legibles. HMR no se da por comprobado solo por abrir la página.
3. Ante layout deficiente, **el agente corrige el `.c4`**, no las relaciones probadas por CogniCode. Reabrir y anotar los ajustes en `lenses/c4/reports/`.
4. No declarar `visual_review=passed` sin inspección efectiva del navegador. El HTML HTTP 200 solo permite afirmar que la UI respondió.

Fuente oficial: https://hub.docker.com/r/likec4/likec4 y https://likec4.dev/tooling/cli/.
