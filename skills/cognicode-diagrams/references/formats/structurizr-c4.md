# `render-structurizr` — modelar y crear Structurizr DSL

Crear o interpretar `workspace.dsl` usando el mismo conocimiento semántico que Mermaid. Structurizr declara **modelo primero** y **vistas después**; una vista solo muestra una selección del modelo.

- Conservar ids estables y nombres dentro de `workspace`, `model`, `views`; definir actores, sistemas software, contenedores, componentes y relaciones con semántica C4 y límites correctos.
- No convertir cada carpeta o dependencia librería en un `container`. Para relaciones, etiquetar la intención y tecnología solo si está acreditada; no convertir `calls` en HTTP sin prueba.
- Construir vistas `systemContext`, `container` y `component` según lo solicitado, con identificadores predecibles y enfoque en un sistema/contenedor.
- Interpretar los DSL ya existentes sin eliminar `tags`, estilos o documentación curada innecesariamente. Si existen includes/constantes/extensiones de Structurizr, resolver de forma segura dentro del ámbito permitido o declarar interpretación parcial.
- El agente es quien escribe el DSL; no se añade un parser o exportador a CogniCode. No subir el workspace a Structurizr Cloud ni usar `push` sin autorización explícita.
- Si está disponible `structurizr` local, comprobar la sintaxis usando `structurizr validate -workspace workspace.dsl` (confirmar `structurizr help` según versión). Revisar `inspect` si se necesita revisión semántica adicional. **No instalarlo automáticamente**.

Plantilla: [Structurizr de ejemplo](../../assets/example-workspace.dsl). Documentación oficial: https://docs.structurizr.com/cli y https://docs.structurizr.com/validate.
