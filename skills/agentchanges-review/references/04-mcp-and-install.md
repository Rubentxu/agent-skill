# 04 — Instalación y servidor MCP

## Instalar el CLI

`agc` se distribuye como un paquete npm autocontenido, con GUI incluida y **cero
dependencias de runtime**:

```bash
npm install -g agentchanges
agc --version
```

Requiere Node 20 o superior y un repositorio git para trabajar: fuera de un repo
sólo funcionan `agc repo list` y `agc store`.

El store (las revisiones y notas) vive en el directorio del usuario, **nunca dentro
del repositorio**, y se identifica por el remote (`slug(remote)-hash8`) con respaldo
por ruta. Es deliberado: las revisiones no ensucian el repo y un `git status`
limpio es una garantía, no una casualidad.

## Registrar el servidor MCP

`agc mcp` habla MCP por stdio. Sin argumentos usa el **directorio de trabajo del
cliente**, así que una sola configuración sirve para todos los repos: el agente
trabaja sobre el repo en el que esté. Con `agc mcp -C <ruta>` queda atado a ese repo.

| Cliente | Fichero | Entrada |
|---|---|---|
| mcode | `~/.minimax/mcp.json` | bajo `mcpServers`: `{"type":"stdio","command":"agc","args":["mcp"]}` |
| opencode | `~/.config/opencode/opencode.json` | bajo `mcp`: `{"type":"local","command":["agc","mcp"]}` |
| codex | `~/.codex/config.toml` | `[mcp_servers.agentchanges]` + `command = "agc"` + `args = ["mcp"]` |
| zcode | `~/.zcode/zcode.json` | bajo `mcp`: `{"type":"local","command":["<node>","<…/agentchanges/agc.mjs","mcp"]}` |

**zcode necesita rutas absolutas.** Se lanza como AppImage desde el escritorio, con
un `PATH` que no contiene ni `node` ni `agc`; ahí `command: "agc"` falla. Compruébalo
antes de asumirlo:

```bash
tr '\0' '\n' < /proc/<pid-de-zcode>/environ | grep ^PATH=
```

Si `node` no está en ese `PATH`, invoca el binario de forma explícita:

```text
"command": ["/ruta/a/node", "/ruta/a/lib/node_modules/agentchanges/agc.mjs", "mcp"]
```

Comprueba el registro antes de dar por buena una configuración:

```bash
agc mcp --list-tools
```

Deben salir 11 tools: `review_open`, `review_status`, `review_diff`, `notes_list`,
`note_read`, `note_add`, `note_update`, `review_brief`, `patch_preview`,
`patch_apply`, `verify_note`.

## Comprobar que el servidor responde

Un `initialize` correcto y un `tools/list` con 11 entradas no bastan: hay que llamar
a una tool real. En un repo sin revisiones, `review_status` **debe devolver un error
con su motivo** y el servidor debe seguir respondiendo. Si el proceso muere, la
configuración está mal.

## Seguridad

Un `review.json` exportado por otra persona contiene campos `check` que son
**comandos de shell**. Importar sus checks e importarlos sin más es ejecución de
código arbitrario en la máquina de quien importa.

```text
agc import <fichero>                 ← los checks quedan suspended
agc import <fichero> --with-checks   ← los conserva; solo con confianza explícita
```

Revísalos uno a uno antes de usar `--with-checks`. Un check importado que ejecuta un
`check` de otro es un `check` que ejecuta lo que quiera.