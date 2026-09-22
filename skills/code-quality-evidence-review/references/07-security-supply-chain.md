# Seguridad y supply chain: búsqueda con contexto

## Mapa de confianza

Identifica fuentes no confiables (HTTP, CLI, plugins, archivos, entornos, eventos), transformaciones/parsers, sinks peligrosos (shell, SQL, archivos, network, deserialización, ejecución de terceros), autenticación/autorización y capacidades. Dibuja una ruta real `entrada → validación → transformación → sink`, junto con límites de tamaño, tiempo, permisos, errores y casos de denegación. Revisa secreto/scope de CI y permisos de tokens; no inspecciones su contenido ni lo copies al informe.

Por cada candidato analiza precondiciones: quién controla entrada, qué validación hay, qué configuración llega a producción, versión afectada, mitigaciones, impacto si falla. Casos frecuentes *solo si aplican*: traversal y Zip Slip en extracción; entidades/alias y expansión en YAML; inyección de comandos o variables de entorno; SSRF; deserialización; recursos sin límite; path/symlink races; ejecución de código generado; bypass de permisos. Tests adversariales deben usar fixtures inertes en entorno aislado; nunca ejecutar explotación contra servicios ajenos o de producción.

## Dependencias y vulnerabilidades

1. Obtener manifiestos, locks **y árbol resuelto/artefacto final**, incluyendo transitorias, plataforma/OS e imagen. Registrar fecha, SHA y herramienta/versiones.
2. Generar SBOM opcional y escanear con base de vulnerabilidades actualizada (OSV-Scanner/Trivy/Grype/cargo audit u otra compatible). Un CVE no aplica solo porque el nombre del paquete coincide: contrastar versión instalada, distribución, affected ranges, configuración, llamada vulnerable y advisory del proveedor.
3. Licencias: identificar licencia efectiva del artefacto concreto y obligaciones de distribución según el caso, con asesoría jurídica cuando proceda. Un archivo de licencia de un proyecto “de inspiración” no cubre sus transitivas.
4. Registrar falsos positivos, riesgos aceptados con fecha/owner y remediaciones verificables; no silenciar todo el scanner ni poner `ignore` permanente sin justificación.

## Operación responsable de herramientas

Herramientas SaaS, extensiones de IDE o escáneres que consultan servicios pueden sacar código, metadatos, hashes de dependencias o resultados fuera del entorno. Antes de usarlas, revisa política del repositorio y consentimiento. Los escáneres automáticos no sustituyen pruebas de abuso de autorizaciones y límites de confianza, ni prueban por sí mismos ausencia de vulnerabilidades.
