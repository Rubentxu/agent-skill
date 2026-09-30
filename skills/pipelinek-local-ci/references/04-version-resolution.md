# Resolución de versión e instalación

Esta referencia responde a: **¿qué `pipelinek` ejecutará realmente el agente?** Para recetas de instalación usa `09-installation-cookbook.md`.

## Preflight automatizado

```bash
bash <skill>/scripts/pipelinek-preflight.sh
```

La sonda es read-only y muestra repo root, JDK, `command -v`, realpath, versión runtime, mise/asdf y pins de proyecto.

## Invariante

Una ejecución sólo acredita CI si puedes demostrar:

```text
requested version
== manager-selected version
== resolved executable identity
== runtime-reported version
```

Un ZIP/tag con otro nombre no cambia la identidad del binario.

## Diagnóstico manual

```bash
type -a pipelinek || true
command -v pipelinek || true
resolved="$(command -v pipelinek 2>/dev/null || true)"
[ -n "$resolved" ] && readlink -f "$resolved" 2>/dev/null || true
[ -n "$resolved" ] && pipelinek version

mise which pipelinek 2>/dev/null || true
asdf current pipelinek 2>/dev/null || true
asdf which pipelinek 2>/dev/null || true
readlink -f "$HOME/.local/share/pipelinek/current" 2>/dev/null || true
```

Busca además `mise.toml`, `.mise.toml` y `.tool-versions` desde el cwd/repo.

## Owner por proyecto

Puedes tener mise y asdf instalados para otras herramientas. Para PipelineK elige uno por proyecto y ejecútalo explícitamente:

```bash
mise exec -- pipelinek version
# o
asdf exec pipelinek version
```

Si `pipelinek` desnudo resuelve a un tercer shim/symlink, no lo uses como gate hasta reconciliar PATH.

## JDK

PipelineK requiere JDK 21+. La instalación del binario no provisiona necesariamente Java.

```bash
java -version
pipelinek doctor
```

En mise/asdf conviene fijar también Java en el proyecto cuando la toolchain del repo no lo gestiona.

## Stable vs prerelease

- estable: pin explícito `X.Y.Z`;
- RC: sólo si el proyecto/usuario opta por ello, pin exacto `X.Y.Z-rcN`;
- nunca promociones una RC localmente renombrando archivos;
- nunca cambies a RC sólo porque contiene una feature que deseas.

### Finding histórico que la skill debe detectar

El 2026-09-29 se publicó una GA `v0.43.0` cuyos bytes reportaban `pipeline 0.43.0-rc1`. Si esa release sigue accesible y aparece en un bootstrap, el resultado correcto es `IDENTITY_MISMATCH`, no éxito. La skill no debe asumir que este finding sigue siendo la última release: verifica siempre el runtime.

## Síntomas típicos

| Síntoma | Lectura |
|---|---|
| `pipelinek` sigue en 0.39 tras instalar otra | shim/symlink/PATH anterior |
| mise dice V y runtime otra | release/layout o resolver incorrecto |
| asdf dice `No version is set` | cwd/pin `.tool-versions` |
| sólo funciona desde un directorio | manager/JDK depende del cwd |
| estable reporta `-rcN` | identity mismatch de distribución |
| `doctor` falla Java | JDK 21+ no visible al proceso |

## Regla de cambio

No modifiques globales, borres shims o desinstales managers como efecto lateral de una ejecución CI. Corrige primero el pin/proveedor del proyecto; cambios globales requieren intención explícita.
