# `render-structurizr` — modelar y crear Structurizr DSL

Crear o interpretar `workspace.dsl` usando solo claims arquitectónicos derivados del **análisis de código mediante CogniCode CLI/MCP**, o bien traducir un diagrama aportado sin afirmar fidelidad al código. Structurizr declara **modelo primero** y **vistas después**; una vista solo muestra una selección del modelo.

- Conservar ids estables y nombres dentro de `workspace`, `model`, `views`; definir actores, sistemas software, contenedores, componentes y relaciones con semántica C4 y límites correctos.
- No convertir cada carpeta o dependencia librería en un `container`. Para relaciones, etiquetar la intención y tecnología solo si está acreditada; no convertir `calls` en HTTP sin prueba.
- Construir vistas `systemContext`, `container` y `component` según lo solicitado, con identificadores predecibles y enfoque en un sistema/contenedor.
- Interpretar solo DSL suministrado por el usuario o derivado del workspace externo, preservando `tags` y estilos. Resolver `!include` **solo dentro de los artefactos derivados bajo HOME**, nunca desde el checkout; en cualquier otro caso, indicar interpretación parcial. Ni `!docs` ni `!adrs` aportan evidencia arquitectónica.
- El agente es quien escribe el DSL; no se añade un parser o exportador a CogniCode. No subir el workspace a Structurizr Cloud ni usar `push` sin autorización explícita.
- Si está disponible `structurizr` local, comprobar la sintaxis usando `structurizr validate -workspace workspace.dsl` (confirmar `structurizr help` según versión). Revisar `inspect` si se necesita revisión semántica adicional. **No instalarlo automáticamente**.

Plantilla: [Structurizr de ejemplo](../../assets/example-workspace.dsl). Documentación oficial: https://docs.structurizr.com/cli y https://docs.structurizr.com/validate.
