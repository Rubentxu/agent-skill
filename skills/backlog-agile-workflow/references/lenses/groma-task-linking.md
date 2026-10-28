# Lente Groma ↔ Backlog.md: enlaces operativos, sin doble fuente de verdad

**Activar:** al ejecutar una tarea Backlog con Groma disponible, en cada archivo modificado y después de combinar, mover o renombrar elementos C4.

1. Verificar ambas CLIs, `groma plugin list` y `groma agent-instructions backlog`. Leer `backlog task view <id> --plain` antes de cualquier edición. No crear una tarea nueva solo para tener un pin en el mapa.
2. Al planificar, usar `groma view <file>` y seleccionar referencias exactas a componentes conocidos. Mantener también referencias documentales originales: ADR/ROADMAP/SPEC no se convierten en C4.
3. Tras modificar cada archivo, conservar todas las entradas de `modifiedFiles` y añadirlo inmediatamente; `--modified-file` reemplaza la lista completa. El helper [groma_task_links.py](../../scripts/groma_task_links.py) acepta una instantánea curada y emite argumentos, **no** escribe Backlog.md.
4. Si un comando Groma imprimió `replaced: X -> Y`, sustituir **solo** el ID X en las referencias, por Y, además de registrar todos los paths creados, modificados y eliminados. No inventar alias persistentes ni asumir que la cadena se puede recuperar más adelante.
5. Evitar duplicidad de vínculos: archivos modificados determinan sus actuales propietarios cuando el mapa los conoce; `--add-ref` es para arquitectura prevista, actores, flows, drafts o alcance no cubierto por archivos.
6. Releer `task view` después de aplicar argv autorizados; no reutilizar snapshots tras cambios de worktree/branch, ni atribuir componentes con scanner no instalado. Los ficheros `groma/` y de Backlog.md siguen fuera del índice Git del consumidor.

**Resultado:** `BACK-42|referencias planificadas|archivos modificados|componentes efectivamente identificados|IDs reemplazados|confirmación de CLI|pendientes`.
