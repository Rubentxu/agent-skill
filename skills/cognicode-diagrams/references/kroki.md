# Kroki — proyección local SOLO de artefactos derivados

Kroki convierte `.mmd`, `.dsl` o `.puml` escritos por el agente en SVG/PNG; **no** analiza arquitectura ni accede al checkout. El script `render_kroki.py` solo acepta fuentes dentro de `~/.cognicode-diagrams/workspaces/<id>/lenses/<lente>/sources/` y salidas en `renders/` del mismo workspace/lente. La raíz `--repo` solo se suministra a `workspace.py`; no se usa para abrir ficheros. [Contrato](investigation-contract.md).

## Preparación

El agente primero obtiene evidencias de código mediante CogniCode, prepara un modelo trazado y escribe `workspace.dsl`/`context.mmd` en `sources/`. `workspace.py inspect/init/path` comprueban dónde guardar. **No usar `assets/example-*` como entrada al renderer en una tarea del usuario**: son ejemplos sintéticos, no artefactos investigados.

## Servicio local

Kroki debe estar en loopback (`http://127.0.0.1:8000`). Arranque de contenedor solo con autorización. Structurizr funciona con gateway; Mermaid necesita el companion `kroki-mermaid`. Mantener `SECURE`; no habilitar `!include`, `!docs` ni `!adrs` para buscar ficheros o generar arquitectura.

## Ejecución sobre fuentes derivadas

`
SRC="$HOME/.cognicode-diagrams/workspaces/<id>/lenses/c4/sources"
DST="$HOME/.cognicode-diagrams/workspaces/<id>/lenses/c4/renders"
python3 scripts/render_kroki.py "$SRC/workspace.dsl" "$DST/context.svg" --type structurizr --view-key Context
python3 scripts/render_kroki.py "$SRC/context.mmd" "$DST/context-mermaid.svg" --type mermaid
`

Sustituir `<id>` por la carpeta devuelta por `workspace.py`. El renderer limita bytes y tiempo, POST solo a localhost, rechaza redirecciones y respuestas que no sean imagen. Un render no confirma identidad de código, evidencia, contenedores ni despliegue. Para errores `RENDER_FAILED`, preservar fuentes y renders existentes; sin validador o revisión visual, declarar `PARTIAL`.

Como visualizadores alternativos de **los mismos derivados**, usar [LikeC4](projectors/likec4.md), [Structurizr Local](projectors/structurizr-local.md) o [Markmap](projectors/markmap.md).
