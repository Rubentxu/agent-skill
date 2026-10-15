# Workspace de proyecto: `~/.cognicode-diagrams/workspaces/`

**Contrato obligatorio:** el checkout Git es una fuente para CogniCode y lectura del agente, nunca un destino de la skill. Los ficheros de representación, evidencias derivadas, renders, informes, plantillas de trabajo y estado de sesión viven **exclusivamente** bajo `~/.cognicode-diagrams/`. No escribir `.gitignore`, `.cognicode-diagrams`, `.pipeline`, `.mmd`, `.dsl`, imágenes, cachés de esta skill ni otros artefactos en el repositorio estudiado. Una petición de salida en el repositorio exige aprobación explícita distinta, y queda fuera del recorrido por defecto.

## Resolución estable sin colisiones

Para `/home/user/projects/pipelinek`, crear:

```text
~/.cognicode-diagrams/
└── workspaces/
    └── pipelinek--<12-hex-de-sha256-ruta-canonica>/
        ├── workspace.json             # vínculo a la ruta canónica del repo; NO base de conocimiento
        ├── evidence/                  # resúmenes derivados, con SHA, dirty y limitaciones
        ├── inputs/                    # diagramas del usuario aportados a la sesión
        ├── lenses/
        │   └── c4/
        │       ├── sources/           # .mmd / workspace.dsl (editables)
        │       ├── renders/           # .svg / .png derivados
        │       └── reports/           # reconciliación y revisión
        ├── sessions/                 # estado efímero, UAT, diagnósticos y handoffs
        └── exports/                  # artefactos compartibles, solo con autorización
```

Se utiliza el **nombre del directorio raíz de Git**, no el nombre remoto, más SHA-256 abreviado de su ruta canónica. Un worktree u otro clon con el mismo basename obtiene un workspace distinto; abrir un subdirectorio de un repo reutiliza su workspace. El archivo `workspace.json` únicamente identifica el checkout, no duplica el índice/grafo de CogniCode. No se presupone persistencia entre reinicios MCP.

## Operaciones explícitas de la skill (Python estándar)

```bash
# No crea ficheros; consulta git rev-parse de solo lectura.
python3 scripts/workspace.py inspect --repo /ruta/al/repositorio

# Inicializa el workspace, dentro de HOME; no altera el repo.
python3 scripts/workspace.py init --repo /ruta/al/repositorio

# Solo crea las tres carpetas de la lente solicitada (nunca precrea lentes futuras).
python3 scripts/workspace.py init-lens --repo /ruta/al/repositorio --lens c4

# Antes de escribir, pide a la skill la ruta destino segura.
python3 scripts/workspace.py path --repo /ruta/al/repositorio \
  --relative lenses/c4/sources/context.mmd
```

`inspect` devuelve `absent`, `ready`, `incomplete` o `invalid` y la ruta. `init` es idempotente: completa carpetas faltantes si la identidad coincide; **nunca sobrescribe** un manifiesto incorrecto. `path` rechaza rutas absolutas, escapes `../` y symlinks; no crea el archivo. El agente debe usar la ruta devuelta y crear padres de subcarpetas solo dentro del workspace autorizado. Si la raíz `~/.cognicode-diagrams` apunta mediante symlink al repo, se bloquea. Si HOME estuviera situado dentro del checkout, se bloquea.

No confundir `workspace` de este documento con una funcionalidad interna ni un repositorio de datos de CogniCode. CogniCode sigue inspeccionando `/ruta/al/repositorio`, y el agente guarda únicamente sus artefactos **fuera** de esa ruta. El nombre `workspace.json` es propio de la skill y no debe enviarse como modelo Structurizr ni sobreescribir `workspace.dsl`.

## Ciclo de vida HATEOAS

Para peticiones que produzcan artefactos o evidencias (`scan`, `discover`, `create`, `interpret`, `translate`, `review`, `update`, `validate`, `preview`):

1. **`inspect-workspace`** si el estado del workspace es desconocido. No escanear ni empezar a generar ficheros antes de resolverlo.
2. **`init-workspace`** si está ausente o incompleto. El usuario ha elegido explícitamente el destino `~/.cognicode-diagrams`; no hace falta inventar otra ruta. No modificar HOME fuera del subárbol propio.
3. **`ready`** habilita el trabajo. Crear un directorio de lente con `init-lens` solo cuando sea necesaria una salida de esa lente.
4. **`invalid`** detiene cualquier escritura, requiere revisar identidades, symlinks y manifest; no borrar, migrar ni sobrescribir silenciosamente.
5. **Reutilizar** las fuentes y las imágenes existentes si se corresponden con la petición y revisión actual; marcar `STALE` si la evidencia o render ya no corresponde al código/archivo, sin machacar un trabajo curado.

`catalog` y `setup` no necesitan crear workspace: listar lentes o instalar CogniCode globalmente no equivale a analizar un repo. El helper de affordances sigue siendo **puro**, solo selecciona acciones; `workspace.py` es el adaptador de sistema de archivos separado, con efectos de creación limitados a `init`/`init-lens`.

## Pruebas de aceptación

- Dos clones `pipelinek` en directorios distintos ⇒ dos IDs diferentes, mismo nombre visible.
- `src/` del repositorio ⇒ resuelve el mismo workspace que su raíz.
- `init` dos veces ⇒ mismo resultado, no sobrescribe fuentes ni afecta Git.
- Workspace inexistente ⇒ no se permite generar/renderizar hasta crearlo.
- `workspace.json` ajeno, symlink que sale hacia repo, destino `../` o HOME dentro de Git ⇒ se rechaza.
- `git status --porcelain` antes/después de cualquier ciclo de la skill ⇒ sin modificaciones **causadas por la skill**; no se confunden cambios de terceros con los propios.
- CogniCode MCP/CLI no se toca; sus cachés internos son responsabilidad del runtime y no se reinventan en este workspace.

## Proyectores locales y aislamiento

Los `.c4` para LikeC4 y `workspace.dsl` para Structurizr Local se generan en `lenses/<lente>/sources/` de **este** workspace. `scripts/projectors.py` obtiene de `scripts/workspace.py` la identidad del checkout Git, pero solo monta `sources/` del directorio HOME en los contenedores. No utiliza un Dockerfile dentro del repo, no modifica `.gitignore` y no monta el checkout. `stop` no destruye el contenido. Los contenedores están separados por workspace/lente, con etiquetas verificadas y puertos configurables en loopback. Revisar [projectors.md](projectors.md).
