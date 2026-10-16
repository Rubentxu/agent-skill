# Lente: allowlist completa de assets por producto y canal

1. Partir del **inventario completo de productos** de [product-discovery](product-discovery.md) y resolver su [contrato de registro](registry-contracts.md). No dar por distribuidas las librerías por existir el ZIP de la CLI.
2. Para **GitHub Releases**, definir `nombre exacto → rol → OS/arquitectura → SHA-256 → propietario` ANTES de publicar. Comparar conjuntos esperado/observado; descartar de ese cotejo únicamente los dos source archives automáticos de GitHub.
3. Para **Maven/Gradle**, listar TODAS las coordenadas `groupId:artifactId:version` esperadas, JAR primario, POM real (dependencias), metadata de módulo, sources/javadoc cuando corresponda, hashes/firma normativa. Comparar coordenadas y variantes por módulo en el registro.
4. Para **OCI**, enumerar imagen/tag/digest/plataformas y verificar pulls remotos. Para npm/PyPI/crates, identidad, versión y contenidos legítimos del paquete, no solo nombre de asset de Release.
5. Publicar instalador/binario y **metadatos normativos** (checksum, SBOM, firma, licencia, manifest); excluir handoffs, inventarios internos, logs, reports de agentes y sources ZIP de workspace añadidos manualmente.
6. SDK ZIP independiente solo con consumidor y uso propios; si son módulos SDK Maven, preferirlos por coordenadas antes que adjuntar el mismo JAR a GitHub Releases.
7. Un artefacto puede requerir licencia, NOTICE, service descriptors, schemas y recursos runtime incluso si su archivo no parece código.

**FAIL:** producto o módulo declarado ausente; binario incompleto; sources obligatorios de Maven omitidos; artefacto ajeno al canal o inesperado; checksum válido de un conjunto incompleto. Conservar licencias y NOTICE.

**Salida:** matriz completa `producto → coordenada → canal → obligatorio → bytes/digest → estado remoto`.
