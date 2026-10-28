# Groma.md + Backlog.md: integración observada, límites y privacidad

## Qué integra realmente el producto

Groma.md trae un **work source** `backlog` que ejecuta la CLI Backlog.md: lee `backlog task list --json`, `backlog task view <id> --json`, estados y configuración; para mapas vivos consume `backlog task list --json --watch`. **No hay otro almacén de tareas**. En Groma.md 0.7.x la inicialización se reconoce por `<groma-root>/project.md` e `index.md`: `config.json` es **opcional** y aparece cuando se configura un plugin. El work source se registra en `<groma-root>/config.json` bajo `workSources` mediante `groma plugin add backlog`, solo tras consentimiento. El plugin requiere CLI Backlog.md en PATH; un Groma instalado **no** implica Backlog instalado. Descubre con `groma plugin list` y `backlog --version`.

Fuentes verificadas: [Groma README](https://github.com/MrLesk/Groma.md/blob/main/README.md), [configuración](https://github.com/MrLesk/Groma.md/blob/main/docs/config.md), [guía oficial de enlaces](https://github.com/MrLesk/Groma.md/blob/main/docs/agent-instructions/backlog.md), [plugin](https://github.com/MrLesk/Groma.md/blob/main/plugins/work-sources/backlog/src/index.ts) y [Backlog README](https://github.com/MrLesk/Backlog.md/blob/main/README.md#groma-md).

## Ruta de descubrimiento y uso

1. **Backlog**: leer `backlog instructions overview`, inspeccionar proyecto/ID, `task view --json` y efectos Git; no instalar ni inicializar por detectar Groma.
2. **Groma**: comprobar `groma --version`, `groma plugin list`, `groma agent-instructions` y luego `groma agent-instructions backlog` solo si ambos existen. `groma view --plain` y `groma view <source-file>` son consultas; `groma plugin add backlog` e `init` cambian configuración y requieren aprobación.
3. Si no hay mapa, confirmar si se quiere inicializar/escanear. `groma scan` **escribe arquitectura Markdown** y puede disparar comprobaciones/actualizaciones en segundo plano según `automaticUpdates`; no ejecutarlo de oficio como simple lectura. `groma web` inicia un servidor y puede escanear: solo en sesiones interactivas autorizadas, con ciclo de vida conocido.
4. El primer scan **no es arquitectura certificada**. Consultar guías `inspect`, `structure`, `describe`, `relationships` bajo demanda. Curar con CLI de Groma únicamente cuando se solicita; sus restricciones, grupos, IDs, responsabilidades y fuentes son de Groma. No editar OKF/frontmatter a mano.
5. **Plan de tarea**: `backlog task view <id> --plain`; si Groma ha observado el elemento o el archivo exacto, `--add-ref <element-id>` o `--add-ref <path>`. Conservar además los IDs originales ROADMAP/ADR/SPEC; son contexto, **no** relaciones ni componentes. No atribuir propiedad por una mera referencia.
6. **Al modificar cada archivo**: leer el estado actual y agregar el path con `--modified-file`, repitiendo la opción con **toda la lista anterior**: es una operación de reemplazo, no append. La utilidad `scripts/groma_task_links.py` propone argv seguros sin escribir ni inferir dueños. El plugin Groma ancla los archivos reales a su componente actual.
7. **Comandos estructurales de Groma**: capturar `created/changed/removed/affected/replaced OLD -> NEW`. Mantener la lista completa de modified files e intercambiar referencias antiguas por IDs **supervivientes** en la tarea inmediatamente. Groma no persiste alias de IDs de combine/rename. Confirmar el cambio antes de otra operación.
8. **Verificación y cierre**: usar `groma view <file>` para comprobar dueño actual, `groma lint` como **preguntas sobre posible lógica duplicada**, y `delivery-first-testing` para garantías. Ni scan verde ni parecido de código prueban calidad o AC/DoD. Referir IDs Groma en la tarea y opcionalmente en el commit si son observados, sin documentos privados.

## Distinción de responsabilidades

- Backlog.md: IDs, estados, dependencias, AC, DoD, `references` y `modifiedFiles`.
- Groma.md: C4/OKF, propiedad de archivos, relaciones, flows, drafts, scans y mapa visual.
- `pure-functional-design`: decidir si la arquitectura o el duplicado observado justifica refactor; puede responder KEEP_AS_IS.
- `delivery-first-testing`: pruebas mínimas basadas en garantías.
- `pipelinek-local-ci`: gates cuando realmente se use PipelineK.
- `agent-secretless`: credenciales vía capacidades anunciadas; Groma no reemplaza el broker.
- `cognicode-diagrams` (si instalada): análisis complementario, **no** segunda autoridad automática; comparar evidencia y no duplicar diagramas sin beneficio.

## Políticas de documentación privada y compatibilidad

Groma.md está diseñado para versionar `groma/` o `.groma/` como OKF Markdown, y también su `config.json`. En proyectos consumidores con política **documentos de gestión fuera de Git**, añadir esos directorios, configuración, snapshots, exports y ZIP asociados a la revisión del guard. La skill NO debe excluir `*.md` ni `*.zip` globalmente, ni borrar contenido, ni alterar Git sin aprobación. Asegurar **backup y sincronización privada** antes de retirar del índice: Groma conserva la lectura local, pero la comparación histórica Git, el action en PR, revisión colaborativa de arquitectura y reconstrucción desde clones **no** son equivalentes a la modalidad recomendada upstream. Verificar capacidad real de cada instalación; no prometer historial o diffs cuando el OKF está ignorado.

`automaticUpdates` de Groma puede consultar paquetes npm e instalar releases en segundo plano; para política local-first sin actualizaciones inesperadas evaluar `automaticUpdates=false` con aprobación. El escaneo usa analizadores locales; no implica envío de código a IA. **`groma export` incluye arquitectura y código fuente**, y aunque excluye tareas, debe tratarse como salida sensible: no subir ni publicar automáticamente. `groma lint` puede devolver exit 1 por hallazgos y **no** constituye fallo del producto por sí mismo.

**Cobertura:** Rust dispone de escáner; Kotlin es experimental y no proporciona fingerprints para `groma lint` de duplicación. Consultar `groma plugin list` y guías exactas: ninguna ausencia de relaciones demuestra ausencia de dependencias.

## Flujo mínimo que más valor aporta

`SPEC/Roadmap → Backlog task → consultar Groma ownership → proponer seam → implementar slice → registrar modifiedFiles/refs → pruebas mínimas → commit con IDs → actualizar task/DoD → (opcional) revisar mapa`. En cambios rutinarios no ejecutar de nuevo una curación completa; Groma propone registrar rutas inmediatamente y actualizar relaciones solo cuando se alteran de verdad.
