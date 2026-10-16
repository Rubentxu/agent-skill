# Lente: allowlist completa de assets

1. Identificar producto `application|cli|library|sdk|plugin|container`, consumidor, arquitectura, SO, canal y normas. La allowlist se deriva de contratos existentes, no de la opinión del agente.
2. Definir `nombre exacto → rol → OS/arquitectura → SHA-256 → propietario` antes de publicar. Comparar conjuntos esperado/observado, no solo ejecutar `sha256sum -c` sobre assets presentes.
3. Publicar instalador/binario distribuible y **metadatos normativos** (checksum, SBOM, firma, licencia, manifest); excluir handoffs, inventarios internos, logs, reports de agentes, sources ZIP añadidos manualmente y copias duplicadas.
4. Para JVM una distribución con `bin/` y `lib/*.jar` es binario real. Para Maven/Nexus, fuentes y POM pueden ser legítimos; no aplicar allowlist de apps a bibliotecas.
5. SDK ZIP independiente solo con consumidor y uso propios; si son módulos SDK Maven, preferir publicarlos por coordenadas sin duplicar el CLI.

**FAIL:** binario ausente, asset obligatorio omitido, duplicado, fuente añadida manualmente o set inesperado. Mantener licencias y NOTICE.
