# Milestones, tareas padre y tareas independientes

- **Milestone:** objetivo transversal compartido o entrega/release. Usar capacidad nativa `backlog milestone` cuando encaje.
- **Padre y subtareas:** capacidad cohesionada con varios slices que requieren agrupación verificable; el CLI ofrece `backlog task create -p <id> <título>`.
- **Tareas independientes:** por defecto si cada vertical slice entrega valor autónomo, aunque compartan ROADMAP.
- **Dependencia:** expresa bloqueo real; no equivale a padre-hijo ni a orden de prioridad.

Consultar [spec-decomposition](spec-decomposition.md), CLI `--help` y datos del proyecto antes de crear o reparentar. No crear jerarquía por el tamaño del roadmap, ni múltiples tareas para cada capa técnica. Confirmar IDs, parent y milestone mediante `task view --json` tras una operación autorizada.
