# Lente futura: `vertical-slice` — **PLANNED, NO ACTIVA**

Antes de habilitar: delimitar caso, entrada (HTTP, CLI, evento, job), flujo por aplicación/dominio/infraestructura y persistencia/efectos. Usar `get_call_hierarchy`, `trace_path`, símbolos y código a través de CogniCode como **topología estática**, corroborar lo que sea necesario con pruebas, rutas y configuración.

Mermaid `flowchart` para la topología de la vertical slice; `sequenceDiagram` solo con evidencia de orden de ejecución. Structurizr `dynamic view` se reserva para secuencias realmente acreditadas y elementos C4 apropiados; no transformar un call graph en orden temporal. Si faltan trazas, informar `DYNAMIC_UNSUPPORTED`, no inventar pasos.
