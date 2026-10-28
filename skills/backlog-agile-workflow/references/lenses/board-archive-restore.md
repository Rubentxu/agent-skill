# Kanban: archivar, restaurar y proteger el borrado

- **Done es un estado; archive retira la tarjeta del Kanban** y la convierte en solo lectura. No archivar automáticamente al terminar; el trabajo verificado puede quedarse en el tablero hasta mantenimiento explícito.
- Consultar `backlog task view <ID> --json`: ID, estado actual, `archived`, resumen, subtareas, dependencias y referencias. Releer antes de cada operación.
- **Terminada:** verificar AC/DoD y gate, guardar `--final-summary`, mover al estado terminal configurado, archivar únicamente si se ha autorizado `backlog task archive <ID>`.
- **Cancelada/duplicada/inválida/obsoleta:** puede archivarse SIN marcar Done, pero debe registrarse **antes** el motivo y sustituto si lo hay. Comprobar tareas dependientes: una dependencia sobre tarea archivada que NO terminó **sigue bloqueando**. No convertir automáticamente en completada para desbloquear el grafo.
- Tras archivar, verificar `archived=true` mediante `backlog task view <ID> --json`. Se conservan ID, estado y enlaces; no se puede editar hasta restauración.
- **Restaurar**: `backlog task restore <ID>` con autorización, tras comprobar que está archivada. Conserva el ID y el estado que tenía, **no la devuelve forzosamente a To Do**. Verificar `archived=false` tras ejecutarla.
- **Borrado** `backlog task delete <ID>`: requiere previamente archivo, es destructivo, puede liberar el ID y reescribir dependencias/referencias ajenas. No proponerlo dentro del CRUD automático. Solo tras aprobación independiente y revisión de impacto. `backlog cleanup` requiere sesión interactiva y no es un atajo seguro para un agente.
- Revisar callbacks `onStatusChange`, operaciones Git y autocommits antes de escribir. `scripts/board_crud.py` rechaza borrados automáticos y distingue archivo/completado.

**Salida:** ID, motivo, dependencias afectadas, estado previo, ubicación final, confirmación por CLI y siguiente acción.
