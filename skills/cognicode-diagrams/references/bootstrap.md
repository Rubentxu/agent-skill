# Instalación local y diagnóstico — usar solo si hace falta

Fuente operativa: `https://github.com/Rubentxu/CogniCode/blob/main/docs/distribution/INSTALL.md`.
Los comandos se documentaron en la rama `main` consultada el 15 de octubre de 2026; revisar `--help` en la versión instalada.

## Inspección no destructiva

```bash
command -v cogh || true
command -v cognicode || true
command -v cognicode-mcp || true
type -a cogh cognicode cognicode-mcp 2>/dev/null || true
# Ejecutar solo cuando exista cogh:
cogh current
cogh doctor
cogh where cognicode
cogh where cognicode-mcp
# Ejecutar solo cuando existan:
cognicode --version
cognicode doctor
cognicode-mcp --version
```

`cogh doctor` y `cognicode doctor` comprueban problemas diferentes: producto instalado, runtime MCP y herramientas/LSP auxiliares. No convertir un aviso sobre un lenguaje no utilizado en fracaso global sin explicar el alcance, ni declarar healthy cuando falta el MCP requerido.

## Instalación limpia en Linux (solo si autorizada)

Fuente oficial: `https://raw.githubusercontent.com/Rubentxu/CogniCode/main/install.sh`.
Descargar el instalador, inspeccionarlo según política de la organización y ejecutarlo **solo con consentimiento**. Nunca `curl | sh` indiscriminado.

```bash
curl -fsSL https://raw.githubusercontent.com/Rubentxu/CogniCode/main/install.sh \
  -o /tmp/cognicode-install.sh
# Revisar /tmp/cognicode-install.sh antes de ejecutarlo.
sh /tmp/cognicode-install.sh
export PATH="$HOME/.cognicode/bin:$HOME/.cognicode/shims:$PATH"
cogh init
# Elegir exactamente un IDE por invocación; EJEMPLO de OpenCode:
cogh install mcp-server --version latest --profile reviewer --ide opencode
cogh current
cogh doctor
cogh where cognicode-mcp
```

Para Claude Code, usar `--ide claude` en lugar de `--ide opencode` si esa versión lo soporta (`cogh install --help`). No usar `--ide all`.

`reviewer` incluye el MCP y los skills del bundle; `core` no garantiza daemon MCP. `cogh` usa versiones y shims: **no** configurar un IDE contra `target/release`, temporales ni un directorio `versions/latest` literal. Una comprobación `cogh doctor` correcta no reemplaza el handshake real `initialize`/`tools/list` del cliente agente.

Si una instalación existente usa mise/asdf, no mezclar propietarios: comprobar `type -a cogh`, `cogh current` y `cogh where` antes de decidir actualización. `cogh update --dry-run`, `cogh reshim`, `cogh rollback` existen para diagnóstico/reparación; usarlos solo tras revisar efectos y con autorización. No sobrescribir configuraciones del IDE; seguir los mecanismos de merge propios de `cogh`.

## Plataformas y límites

La guía de distribución publicada identifica Linux GNU x86_64/aarch64 como matriz estable. `explorer-mcp` y Explorer UI **no** son requisitos ni paquetes estables del recorrido descrito. Si la máquina o perfil no es compatible, marcar `BLOCKED` y explicar alternativas soportadas; no fabricar instaladores.
