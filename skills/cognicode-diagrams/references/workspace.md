# Workspace derivado, separado del repositorio

**Contratos:** CogniCode CLI/MCP es la única interfaz de investigación arquitectónica; los scripts de esta skill nunca ejecutan Git ni leen ficheros de código, configuración o documentación del repositorio. La ruta `--repo` es un identificador **explícito proporcionado por usuario o CogniCode**. Se exige la raíz real: no hay `git rev-parse` ni auto-descubrimiento de la raíz desde una subcarpeta.

## Estructura externa

`~/.cognicode-diagrams/workspaces/<nombre>--<hash-ruta>/` contiene solo `workspace.json` (identidad opaca), `evidence/` (respuestas/claims CogniCode), `inputs/` (diagramas aportados), `lenses/<lens>/sources/`, `renders/`, `reports/`, `sessions/`, `exports/` y `navigation/` cuando hay atlas.

`
python3 scripts/workspace.py inspect --repo /ruta/explicita/a/raiz
python3 scripts/workspace.py init --repo /ruta/explicita/a/raiz
python3 scripts/workspace.py init-lens --repo /ruta/explicita/a/raiz --lens c4
python3 scripts/workspace.py path --repo /ruta/explicita/a/raiz --relative lenses/c4/sources/context.mmd
`

El script solo realiza comprobaciones sobre la **ruta suministrada** (`is_dir`, `resolve`) y sobre sus propios directorios/manifiestos en HOME. No puede verificar que un directorio es realmente la raíz de Git sin violar la exclusividad; el agente debe aportar la raíz indicada por el usuario o CogniCode. Para una subcarpeta, volver a proporcionar esa raíz explícita.

## Invariantes

- No escribir en el checkout ni crear artefactos auxiliares dentro de él. `init` es idempotente; no reemplazar `workspace.json` ajeno.
- Rechazar HOME dentro del objetivo, symlinks que salen del workspace, destinos absolutos o `../`, identidades distintas y fuentes externas.
- El directorio de destino debe ser `ready` antes de generar/proyectar. La skill no inspecciona el contenido del checkout para verificar este estado.
- Los proyectores consumen **exclusivamente** `sources/`, `renders/` y `navigation/` del workspace y nunca montan el repo. Su parámetro `--repo` solo localiza el workspace derivado mediante hash de ruta.
- SHA, dirty y vigencia de análisis se obtienen **solo si CogniCode los comunica**; la skill no consulta Git para suplir ausencia de identidad. Si falta ⇒ `UNKNOWN`.
- El renderer Kroki rechaza fuentes fuera de `lenses/<lens>/sources/` y salidas fuera de `lenses/<lens>/renders/`; ambos deben corresponder al mismo workspace/lente.

Para protocolos de lectura y pruebas: [investigation-contract.md](investigation-contract.md), [evidence.md](evidence.md) y [projectors.md](projectors.md).
