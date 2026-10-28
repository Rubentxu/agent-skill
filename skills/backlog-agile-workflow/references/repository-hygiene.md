# Política de repositorio: gestión de proyecto fuera del índice Git

**Regla para aplicaciones consumidoras:** ROADMAP, BACKLOG, ADR, SPEC, paquetes de hitos, tasks/drafts/docs/decisions/milestones de Backlog.md, y ZIP de estos materiales son **datos privados de gestión**, no entregables de código. No añadirlos ni mantenerlos en el índice Git. Los documentos que son **fuentes de una skill distribuida** (p. ej. `skills/<skill>/SKILL.md`, sus referencias y fixtures) son parte del producto skill y no entran en esta clasificación.

## Inventario seguro (sin cambios)

Desde la raíz de **la aplicación consumidora**, ejecutar:

```bash
python3 <ruta-a-la-skill>/scripts/git_artifact_guard.py --repo . --check
git status --short
git ls-files --cached
```

El guard produce JSON con archivos ya rastreados, clasificaciones, patrones `.gitignore` sugeridos y argv de **propuestas**. No borra ni altera el índice. Clasifica por rutas y patrones explícitos; un ZIP distribuible de software o documentación técnica de API no debe confundirse con el archivo ZIP de un roadmap. La lista no es exhaustiva: inspeccionar nombres custom, exportaciones, ficheros grandes e historial.

## Procedimiento de limpieza autorizado

1. Clasificar cada hallazgo según **propósito real**, no solo extensión: planificación/gestión vs código, contratos generados para consumidores, tests, documentación de API y assets distribuibles. No borrar contenido de código o documentación pública de producto.
2. Identificar ubicación persistente **privada y con backup** para documentos y Backlog.md. Si varias personas colaboran, acordar almacenamiento/sincronización externo con control de acceso antes de sacar del repositorio compartido. Un `.gitignore` no crea una copia de seguridad.
3. Revisar configuración `backlog config get autoCommit`, `remoteOperations`, `checkActiveBranches`, `onStatusChange` y `bypassGitHooks`. Proponer `backlog config set autoCommit false` y `... remoteOperations false` si conviene, **solo con aprobación**. Sin archivos en Git, funcionalidades de reconstrucción de tareas entre ramas y auto-commits dejan de ser equivalentes a la modalidad Git de Backlog.md.
4. Añadir entradas precisas a `.gitignore` (incluido directorio de Backlog.md real, sea `backlog/`, `.backlog/` o custom, config y exportaciones). Nunca sobrescribir el ignore existente; evitar patrones globales `*.md` o `*.zip` que ocultan código/productos.
5. Sobre cada archivo rastreado y **tras autorización**, `git rm --cached -- <ruta>`, conservando contenido local. Para un directorio completo, usar `git rm -r --cached -- <ruta>` cuando sea seguro. Verificar backup, `git diff --cached --name-status`, `git status --short` y nuevo audit. Hacer commit del cambio de índice y `.gitignore` siguiendo la plantilla de trazabilidad.
6. No confundir esta limpieza con borrado del historial remoto. Los documentos siguen presentes en commits anteriores. Si contienen secretos o información que deba purgarse, tratarlo como incidente separado con aprobación explícita y procedimiento de reescritura de historial/rotación; este guard no lo hace.
7. **Gate previo a commit:** escanear archivos rastreados y staged. Si hay artefactos de gestión, detenerse, resolver o documentar una excepción explícita, y nunca ignorar silenciosamente el fallo.

El guard **no** debe ejecutarse sobre el repositorio fuente de las skills para tratar sus `ROADMAP.md`, `ADR-*.md` y referencias internas como datos de una aplicación consumidora.

## Consecuencia importante

La trazabilidad **no** se obtiene publicando documentos de gestión en Git. Se obtiene conservando sus **IDs lógicos** en Backlog.md y en trailers de commits, y manteniendo los documentos originales en almacenamiento privado duradero. El commit no publica su contenido: refiere identidades y evidencia mínima no sensible.
