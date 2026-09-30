# Installation cookbook: mise, asdf y checkout directo

Objetivo: **pin de proyecto + identidad runtime exacta**. No uses `latest` como identidad CI persistente.

## Mise — backend GitHub nativo

Mise soporta release assets GitHub, `asset_pattern`, `strip_components`, `bin_path` y el prefijo `v` habitual de tags. No uses el backend asdf para PipelineK cuando ya existe este backend nativo.

Configuración de proyecto recomendada:

```toml
# mise.toml
[tool_alias]
pipelinek = "github:Rubentxu/pipeline-kotlin"

[tools.pipelinek]
version = "<PINNED_VERSION>"
asset_pattern = "pipelinek-{{ version }}.zip"
strip_components = 1
bin_path = "bin"
```

Después:

```bash
mise install
mise exec -- pipelinek version
mise exec -- pipelinek doctor
mise which pipelinek
```

Para descubrir versiones estables:

```bash
mise ls-remote 'github:Rubentxu/pipeline-kotlin'
```

Para una RC explícita, añade `prerelease = true` a la entrada y fija exactamente `X.Y.Z-rcN`. Nunca cambies automáticamente de estable a RC para conseguir una feature DSL.

### Gate de identidad

Tras instalar `V`:

```text
mise-selected V == pipelinek version V
```

Si no coincide, la release/canal no es utilizable como evidencia.

## asdf — plugin PipelineK

```bash
asdf plugin add pipelinek https://github.com/Rubentxu/asdf-pipelinek.git   # sólo si falta
asdf list all pipelinek
asdf latest pipelinek
asdf install pipelinek <PINNED_VERSION>
asdf set pipelinek <PINNED_VERSION>
asdf current pipelinek
asdf which pipelinek
asdf exec pipelinek version
asdf exec pipelinek doctor
```

`asdf set` escribe `.tool-versions` del proyecto. Para home/global moderno:

```bash
asdf set -u pipelinek <PINNED_VERSION>
```

No uses `asdf global`: no es la API moderna.

Ejemplo de `.tool-versions`:

```text
java temurin-21.0.8+9.0.LTS
pipelinek <PINNED_VERSION>
```

El plugin puede verificar descarga/checksum, pero **la skill siempre verifica además el runtime**.

## Instalador versionado del producto

En un checkout de PipelineK:

```bash
bash scripts/install-pipelinek.sh install <VERSION>
bash scripts/install-pipelinek.sh use <VERSION>
export PATH="$HOME/.local/share/pipelinek/current/bin:$PATH"
bash scripts/install-pipelinek.sh doctor
pipelinek version
```

El instalador es stable-only y transaccional.

## Cuando conviven mise + asdf + instalación manual

No desinstales nada automáticamente. Ejecuta:

```bash
bash <skill>/scripts/pipelinek-preflight.sh
type -a pipelinek
```

Elige **un owner por proyecto** y ejecuta mediante ese owner:

```bash
mise exec -- pipelinek ...
# o
asdf exec pipelinek ...
# o path absoluto
```

Nunca uses un shim ambiguo como evidencia.

## Release health

Una etiqueta GitHub “stable” no basta. El gate mínimo de un canal es:

```text
requested version
== selected manager version
== archive identity
== pipelinek version
```

Si una estable pública reporta una RC internamente, marca `IDENTITY_MISMATCH` y detente. No renombres archivos ni toleres prefijos para “arreglarla” localmente.
