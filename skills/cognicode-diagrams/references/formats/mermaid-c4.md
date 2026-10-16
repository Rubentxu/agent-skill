# `render-mermaid` — generador/lector Mermaid C4 especializado

Crear Mermaid C4 desde el modelo semántico elaborado por el agente con **consultas y referencias de código devueltas por CogniCode CLI/MCP**, nunca por lectura directa ni documentos, no transformar mecánicamente un call graph. En `C4Context`, presentar actores, sistema y sistemas externos; en `C4Container`, límites del sistema, contenedores realmente desplegables y relaciones; en `C4Component`, componentes de un contenedor elegido. Preferir vistas acotadas y legibles, no un diagrama inmanejable del monorepo.

- Cabeceras: `C4Context`, `C4Container`, `C4Component`, `C4Dynamic` únicamente con comportamiento ordenado verificado.
- Nodos: `Person`, `System`, `System_Ext`, `System_Boundary`, `Container`, `ContainerDb`, `Component`, `Rel` y variantes admitidas por el motor Mermaid instalado. Revisar la compatibilidad antes de añadir sintaxis poco soportada.
- Usar identificadores alfanuméricos estables; escapar/normalizar textos, comillas, saltos y caracteres especiales. No inventar tecnologías o protocolos.
- Mantener trazabilidad en un reporte adjunto de evidencias, no almacenar información epistemológica como texto decorativo ilegible en cada nodo.
- Para editar Mermaid existente, preservar id, nombre y contenido no afectado salvo petición de reestructuración.
- Si hay un validador Mermaid autorizado/disponible (por ejemplo `mmdc`), generar render de prueba; si no, realizar análisis estático básico y etiquetar **syntax-unverified**. La sintaxis C4 puede variar entre versiones del renderer; no introducir una nueva instalación sin consentimiento.

Plantilla autocontenida: [Mermaid de ejemplo](../../assets/example-c4.mmd). La presencia de `graph LR` u otro `flowchart` generado por `cognicode graph mermaid` es **insumo**, no certificado C4.
