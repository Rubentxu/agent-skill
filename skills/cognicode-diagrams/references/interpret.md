# Interpretar, traducir y reconciliar diagramas existentes

1. Detectar lente y formato por **contenido**: no suponer C4 porque la extensión sea `.mmd` o `.dsl`. Ejemplos: Mermaid `C4Context` (C4), `classDiagram` (clases), `sequenceDiagram` (secuencia), `flowchart` (podría ser varias lentes). Structurizr `workspace {}` define modelos C4/vistas según su DSL; no identifica casos de uso UML ni clases UML.
2. Comprobar que la lente solicitada figura `ready` en `lens-registry.json`. Si está `planned` no activarla silenciosamente, aunque el agente sepa leer esa sintaxis; explicitar trabajo fuera de skill si usuario lo pide.
3. Interpretar entidades, relaciones, identidad, dirección, jerarquía, scope y vistas. Separar modelo conceptual de layout; los elementos ocultos en una vista Structurizr pueden seguir existiendo en el modelo. Resolver `!include` únicamente con rutas locales autorizadas y comprobar su contenido antes de confiar en él.
4. Marcar `CURATED`, `OBSERVED`, `INFERRED`, `UNKNOWN`; las declaraciones de diseño no se convierten automáticamente en hechos del runtime.
5. Para revisar contra código, inspeccionar CogniCode en el mismo workspace/revisión y corroborar con fuente independiente apropiada. Si la evidencia está obsoleta, ejecutar la acción de refresco permitida.
6. Para traducir, comprobar matriz lente/formato. La notación `adapted` exige declarar pérdidas y pedir consentimiento cuando cambie la semántica. `unsupported` no genera un supuesto equivalente.
7. Para actualizar, realizar diff mínimo, conservar IDs y decisiones manuales y no escribir el original salvo solicitud expresa.

## Resultado

Informe con significado de cada elemento, correspondencias y relaciones, incertidumbres, cambios propuestos, pérdidas de traducción y enlaces a próximos pasos. Un archivo legible no implica que el modelo sea verdadero.
