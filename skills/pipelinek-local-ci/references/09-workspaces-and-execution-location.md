# Workspaces y ubicación de ejecución

Esta referencia fija el contrato local-first introducido por la remediación RP-034 de PipelineK. No confundas la ubicación del fichero `pipeline.kts` con el proyecto sobre el que se ejecuta.

## Modelo mental

Mantén separados estos hechos:

| Concepto | Significado |
|---|---|
| `InvocationDirectory` | cwd del proceso que invoca `pipelinek run` |
| `PipelineDefinitionPath` | ruta del `pipeline.kts`; puede estar dentro o fuera del proyecto |
| `WorkspaceRoot` | frontera autorizada para paths de usuario durante el run |
| `CurrentDirectory` | cwd efectivo dentro del workspace; cambia con `dir { }` |
| `ControlRoot` | estado interno de PipelineK; nunca base para paths del proyecto |
| ownership | `Attached` = usuario/checkout; `Managed` = scratch propiedad de PipelineK |

La ley clave es:

```text
PipelineDefinitionPath != WorkspaceRoot
```

Mover el pipeline a un directorio central no mueve el proyecto.

## Default local-first

En builds que exponen el contrato RP-034 (comprueba también que `pipelinek run --help` ofrece `--isolated`), el caso normal es:

```bash
cd /repos/service-a
pipelinek run /home/me/.pipelinek/pipelines/ci.pipeline.kts
```

Resultado esperado:

```text
InvocationDirectory = /repos/service-a
WorkspaceRoot       = /repos/service-a
CurrentDirectory    = /repos/service-a
PipelineDefinition  = /home/me/.pipelinek/pipelines/ci.pipeline.kts
ownership           = Attached
```

No añadas `--workspace .` por reflejo. Es válido como override explícito, pero oculta que el contrato normal es operar sobre el directorio desde el que el usuario o agente invoca PipelineK.

## Workspace explícito

Usa `--workspace <path>` cuando el proceso se lanza deliberadamente desde otro cwd y quieres adjuntar un proyecto concreto:

```bash
pipelinek run \
  --workspace /repos/service-a \
  /home/me/.pipelinek/pipelines/ci.pipeline.kts
```

El workspace sigue siendo **Attached/user-owned**. Un `--workspace` explícito no convierte el checkout en scratch gestionado.

## Modo aislado

Usa `--isolated` sólo cuando quieres un workspace scratch gestionado por PipelineK:

```bash
pipelinek run --isolated /home/me/.pipelinek/pipelines/smoke.pipeline.kts
```

`--isolated` y `--workspace` son mutuamente excluyentes.

No uses `--isolated` para "arreglar" un `./gradlew: no such file` o un path de proyecto ausente. Un scratch empieza sin el checkout del caller salvo que la propia pipeline lo materialice/clone de forma explícita.

## Semántica de `dir`

```kotlin
dir("backend") {
    sh("./gradlew check")
    pwd()
}
```

`dir("backend")`:

- deriva `CurrentDirectory` a `<WorkspaceRoot>/backend`;
- **no** cambia `WorkspaceRoot`;
- **no** cambia ownership;
- restaura el cwd al salir del bloque;
- no autoriza escapar de la frontera del workspace.

Para cambiar cwd de Steps, prefiere `dir { }` a esconder `cd ...` dentro de una cadena shell.

## Seguridad destructiva

Un workspace `Attached` pertenece al usuario. PipelineK debe proteger su raíz:

- `deleteDir()` / `cleanWs()` contra la raíz adjunta: **fail closed por defecto**;
- una subruta derivada mediante `dir("...")` puede limpiarse cuando el contrato lo permita;
- un workspace `Managed` creado con `--isolated` puede limpiar su propia raíz.

Nunca deduzcas ownership porque exista `.git`, `pom.xml`, `Cargo.toml` o cualquier otro marcador. Ownership es un hecho explícito del runtime, no una heurística VCS.

Si una operación destructiva se rechaza, no la "soluciones" cambiando a `--isolated` o moviendo el workspace salvo que esa sea realmente la intención del usuario.

## Estado durable y control root

Workspace y estado durable son responsabilidades distintas. Mantén DB/control-root fuera del checkout:

```bash
state="${XDG_STATE_HOME:-$HOME/.local/state}/pipelinek/service-a"
mkdir -p "$state"

cd /repos/service-a
pipelinek run \
  --db "$state/run.sqlite" \
  --control-root "$state/control" \
  /home/me/.pipelinek/pipelines/ci.pipeline.kts
```

`ControlRoot` nunca debe usarse como base para resolver `./gradlew`, `src/`, artefactos del proyecto o paths relativos del usuario.

## Diagnóstico de problemas de workspace

Ante un "file not found", cwd inesperado o artefacto en ruta incorrecta, captura antes de modificar la pipeline:

```text
pipelinek realpath/version:
invocation directory:
pipeline definition path:
workspace mode: default-attached | explicit-attached | isolated-managed
workspace root:
pwd() en root:
pwd() dentro de dir(...):
db/control-root:
primer path que no resolvió:
```

Comprueba en este orden:

1. ¿el agente invocó PipelineK desde el checkout que pretendía?
2. ¿está confundiendo la carpeta del pipeline con la del proyecto?
3. ¿se activó `--isolated` accidentalmente?
4. ¿se pasó `--workspace` a otro repo?
5. ¿el fallo aparece sólo dentro de `dir`?
6. ¿algún Step está intentando usar control-root como base de paths?

No corrijas un problema de cwd añadiendo paths absolutos por todo el DSL: corrige primero la ubicación de ejecución.

## Builds antiguos

La instalación real manda. Si `pipelinek run --help` no expone `--isolated` o el runtime pertenece a una versión anterior a RP-034, no presupongas local-first. En ese caso usa el comportamiento validado por esa instalación, normalmente un `--workspace <repo>` explícito, y reporta que se está operando en modo legacy.
