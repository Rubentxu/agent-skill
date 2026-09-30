# Bootstrap, instalación y resolución de PipelineK

Objetivo: terminar con **una versión explícita por proyecto y un ejecutable cuya identidad runtime coincide exactamente**.

PipelineK requiere JDK 21+. Verifica primero:

```bash
java -version
```

## Opción A — mise (recomendada cuando el proyecto ya usa mise)

Mise puede consumir directamente los assets de GitHub Releases; no necesita el plugin asdf.

Define el backend de PipelineK con el layout del ZIP:

```bash
TOOL='github:Rubentxu/pipeline-kotlin[asset_pattern=pipelinek-{{ version }}.zip,strip_components=1,bin_path=bin]'
mise ls-remote "$TOOL"
```

Elige una **VERSION estable explícita** de esa lista y fíjala en el proyecto:

```bash
VERSION='<VERSION>'
mise use "$TOOL@$VERSION"
mise exec -- sh -lc 'command -v pipelinek; pipelinek version; pipelinek doctor'
```

`mise use` escribe la selección de proyecto. Usa `mise use -g ...` sólo si el usuario pide un default global.

No dejes `latest` como identidad de CI reproducible. Puedes usarlo para descubrir una versión, pero materializa/pinea el número resuelto.

## Opción B — asdf

Plugin oficial del proyecto:

```bash
asdf plugin list
asdf plugin add pipelinek https://github.com/Rubentxu/asdf-pipelinek.git   # sólo si falta
asdf list all pipelinek
asdf latest pipelinek
```

Selecciona/pinea:

```bash
VERSION='<VERSION>'
asdf install pipelinek "$VERSION"
asdf set pipelinek "$VERSION"       # .tool-versions del proyecto
asdf current pipelinek
asdf which pipelinek
asdf exec pipelinek version
asdf exec pipelinek doctor
```

Para default de home usa `asdf set -u pipelinek "$VERSION"`, no sintaxis `global` antigua.

El plugin asdf verifica el ZIP contra `SHA256SUMS`, pero la skill **siempre verifica además identidad runtime**.

## Opción C — instalador del producto

Si se trabaja desde un checkout de `pipeline-kotlin` o se ha obtenido el instalador oficial:

```bash
bash scripts/install-pipelinek.sh install '<VERSION>'
bash scripts/install-pipelinek.sh use '<VERSION>'
bash scripts/install-pipelinek.sh list
bash scripts/install-pipelinek.sh doctor
```

Este instalador es estable-only, transaccional, usa `SHA256SUMS` y mantiene versiones bajo `~/.local/share/pipelinek` por defecto.

## Verificación obligatoria

Para cualquier canal:

```bash
type -a pipelinek || true
resolved="$(command -v pipelinek)"
printf 'resolved=%s\n' "$resolved"
readlink -f "$resolved" 2>/dev/null || true
pipelinek version
pipelinek doctor
```

Invariante:

```text
requested version == manager-selected version == runtime-reported version
```

Si `requested 0.X.Y` y runtime devuelve `0.X.Y-rcN`, la instalación **no acredita esa estable** aunque el asset se llame estable.

## Cuando mise y asdf conviven

No intentes desinstalar uno automáticamente. Diagnostica:

```bash
type -a pipelinek || true
command -v pipelinek || true
mise which pipelinek 2>/dev/null || true
asdf current pipelinek 2>/dev/null || true
asdf which pipelinek 2>/dev/null || true
readlink -f "$HOME/.local/share/pipelinek/current" 2>/dev/null || true
```

Busca pins: `mise.toml`, `.mise.toml`, `.tool-versions`. Ejecuta el gate mediante el manager seleccionado o path absoluto; no confíes en un shim ambiguo.

## Fallos típicos

| Síntoma | Lectura |
|---|---|
| `No version is set for command ...` | cwd/pin asdf incorrecto |
| manager dice V pero `pipelinek version` dice otra | identity mismatch |
| `pipelinek` resuelve a 0.39 tras instalar nueva | PATH/shim/symlink antiguo |
| Java no encontrado | JDK 21+ no provisionado en entorno real del proceso |
| `validate` funciona desde repo pero no fuera | toolchain/shim depende del cwd |

No declares bootstrap terminado hasta ejecutar `version` y `doctor` con el mismo mecanismo que usará el agente.

Fuentes operativas: mise GitHub backend y asdf moderno (`install`, `latest`, `set`, shims).
