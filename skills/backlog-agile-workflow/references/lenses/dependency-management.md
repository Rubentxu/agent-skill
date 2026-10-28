# Dependencias reales y desbloqueo

1. Consultar `backlog task view <id> --json` y `dependencyGraph`; comprobar identidades, estados, archivo y `isReady` desde corpus completo. Una tarea archivada sin completarse **sigue bloqueando**.
2. Distinguir bloqueo genuino de orden deseado, etiqueta, milestone y relación padre-hijo. No encadenar vertical slices sin dependencia de producto.
3. Validar ausencia de ciclos, autodependencia, ID desconocido y conflicto de rama. Inspeccionar `backlog task edit --help` antes de usar flags `--dep`/quitar dependencias: no asumir semántica de reemplazo.
4. Proponer cambio y efecto sobre tareas dependientes; ejecutar mediante CLI únicamente con permiso y reconsultar el grafo/ready.
5. Nunca marcar Done de una tarea para desbloquear otra sin pruebas ni convertir archivo en completado.

**Salida:** aristas observadas, cambio propuesto, readiness afectado, resultado CLI o `PROPOSE_ONLY`.
