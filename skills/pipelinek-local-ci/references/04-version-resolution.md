# Resolver exactamente qué PipelineK ejecuta el agente

No confíes en que “está instalado”. Una máquina puede tener mise, asdf y un symlink manual simultáneamente.

## Diagnóstico read-only

```bash
type -a pipelinek || true
command -v pipelinek || true

resolved="$(command -v pipelinek 2>/dev/null || true)"
if [ -n "$resolved" ]; then
  readlink -f "$resolved" 2>/dev/null || printf '%s\n' "$resolved"
  pipelinek version
  pipelinek doctor
fi

mise which pipelinek 2>/dev/null || true
asdf which pipelinek 2>/dev/null || true
asdf current pipelinek 2>/dev/null || true

readlink -f "$HOME/.local/share/pipelinek/current" 2>/dev/null || true
```

Busca también pins del proyecto cuando sean relevantes: `.tool-versions`, `mise.toml` / `.mise.toml`, configuración SDKMAN u otro manager adoptado por el repo.

## Invariante

Para acreditar un gate debes saber:

```text
resolved command
→ real path
→ reported PipelineK version
```

Si el proyecto fija una versión, esa versión debe coincidir exactamente.

## Mise y asdf

No cambies globales ni “arregles” shims como efecto lateral de ejecutar CI.

Si el usuario eligió mise, usa la forma explícita soportada por su configuración. Si eligió asdf, idem. Si conviven, el gate debe ejecutar mediante el proveedor elegido o un path absoluto, no mediante un `pipelinek` ambiguo.

## Prereleases y distribución

No deduzcas que un asset estable contiene binarios estables sólo por su nombre. Si aparece:

```text
requested 0.X.Y
pipelinek version → 0.X.Y-rcN
```

trátalo como **identity mismatch**, no como éxito.

La skill no repara la infraestructura de distribución por sí sola: informa el mismatch y evita usar esa ejecución como evidencia.

## Instalación ausente

Si no hay PipelineK:

- no instales automáticamente;
- informa qué falta;
- señala el canal/documentación que el proyecto haya adoptado;
- si el usuario autoriza instalación, verifica versión, path y `doctor` antes de crear evidencia CI.
