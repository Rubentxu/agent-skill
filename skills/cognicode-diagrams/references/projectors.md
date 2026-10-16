# Proyectores de artefactos — aislamiento absoluto del repositorio

Los proyectores **solo** leen fuentes y renders creados por el agente bajo `~/.cognicode-diagrams/workspaces/<id>/`. Nunca leen, montan, analizan ni buscan archivos del checkout; su `--repo` es únicamente un identificador opaco para resolver un workspace derivado mediante ruta explícita **sin Git**. No ejecutan CogniCode, porque la investigación ocurre ANTES con agente + CLI/MCP. [Contrato](investigation-contract.md).

| Proyector | Entradas derivadas | Salida |
|---|---|---|
| Kroki local | `lenses/*/sources/*.mmd|*.dsl|*.puml` | `lenses/*/renders/*.svg|*.png` |
| LikeC4 local | `lenses/*/sources/*.c4` | visor interactivo local |
| Structurizr Local | `lenses/*/sources/workspace.dsl` | visor C1/C2/C3 local |
| Markmap | `navigation/atlas.md` formado de sources/renders | `navigation/atlas.html` |

## Contrato OCI y render

- Solo proyectar si `workspace.py inspect` informa `ready`; `init-lens` crea carpetas del workspace, no inspecciona repo. No pasar código al runtime de render.
- Para `projectors.py start|stop|remove --repo <ruta-raiz-explicita>`, autorización específica de contenedores; preferir Podman, admitir Docker. El contenedor monta exclusivamente `sources/` del workspace (nunca el checkout), con puertos en loopback y verificación de etiquetas/volúmenes.
- Kroki `scripts/render_kroki.py` restringe origen `sources/` y destino `renders/` en el mismo workspace y lente; no permite archivos arbitrarios ni endpoints públicos.
- Markmap y Atlas usan únicamente el workspace y sus ficheros; no regeneran ni certifican hechos de código.
- `HTTP_READY`, `FORMAT_VALID`, `RENDERED` y `VISUALLY_REVIEWED` no implican `IMPLEMENTATION_GROUNDED`. Este último solo se obtiene mediante claims de CogniCode previos y actuales.

Procedimientos existentes: [Kroki](kroki.md), [LikeC4](projectors/likec4.md), [Structurizr Local](projectors/structurizr-local.md), [Markmap](projectors/markmap.md).

## Markmap local

`projectors.py status/start/stop/remove --projector markmap` sirve el HTML y artefactos derivados con allowlist de rutas, montaje RO y host `127.0.0.1`. No inicia nada durante `atlas.py sync` y no reemplaza el proyector HTML offline. [Operación](projectors/markmap.md).
