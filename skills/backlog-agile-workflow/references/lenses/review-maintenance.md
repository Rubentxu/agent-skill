# Review & Maintenance — mejora continua sin burocracia

1. Inspeccionar tablero/listado y milestones con opciones no interactivas; comparar WIP, bloqueos, antigüedad visible y tareas listas, sin inventar velocity.
2. Preguntar qué impidió entregar valor: tareas demasiado grandes, dependencias evitables, AC difusos, fallos repetidos o interrupciones. Elegir **una** mejora de flujo que pueda verificarse.
3. Repriorizar con autorización, registrar una decisión si cambia una política real. No reescribir todo el backlog ni regenerar ROADMAP.md automáticamente.
4. `backlog doctor` es lectura/diagnóstico; `backlog doctor --fix` puede reorganizar ficheros/IDs y requiere revisión expresa. No usar `backlog cleanup` en agentes no interactivos.
5. `backlog task archive <id>` conserva ID/historia y retira del board; solo por solicitud explícita. `backlog task delete <id>` es definitivo y afecta referencias: por defecto rechazar automatización y requerir confirmación específica.
6. `backlog board export` crea/sobrescribe ficheros según flags: confirmar destino antes de generar un informe.

**Salida:** 1 problema del proceso, 1 mejora, 1 señal futura para revisarla; mantener el resto `KEEP_AS_IS`.
