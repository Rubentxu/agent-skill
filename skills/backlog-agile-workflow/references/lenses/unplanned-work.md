# Trabajo imprevisto sin duplicar backlog

**Activación:** bug, deuda, duplicidad, seguridad, fallo de integración o caso de uso nuevo durante una tarea.

1. Comparar hallazgo con alcance y AC/DoD. ¿Impide el resultado actual? ¿Puede verificarse por separado? Buscar coincidencias mediante `backlog search <consulta> --json`, también en roadmap/spec/commits y borradores.
2. Elegir una acción: `IN_SCOPE_FIX` cuando es inseparable del slice; `DRAFT` para hipótesis; `NEW_TASK_PROPOSAL` para entrega distinta y verificable; `KEEP_AS_IS` si ya existe; `DISCARD_WITH_REASON` si no aporta valor.
3. No usar umbrales arbitrarios de minutos/LOC. Evitar prioridad inventada, títulos vagos y tickets nuevos por cada warning de scanner.
4. La nueva tarea solo se crea con autorización, criterios de aceptación y vínculo al ID de origen; si bloquea, comprobar dependencia real con [dependency-management](dependency-management.md).
5. Continuar el trabajo original cuando no hay bloqueo. No hacer `groma scan` ni escribir arquitectura a partir del hallazgo.

**Salida:** evidencia, decisión, relación con trabajo actual y propuesta de comando CLI (si procede).
