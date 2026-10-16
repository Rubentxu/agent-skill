# Lente: identidad, integridad, procedencia, SBOM

1. Comparar versión del tag, nombre, raíz del archive, JAR/manifest, CLI runtime y candidato. Diferencias de versión invalidan release aunque el checksum sea correcto.
2. Calcular SHA-256 para cada binario obligatorio; verificar ausencia de nombres duplicados/conflictivos en `SHA256SUMS` y que estén todos los assets requeridos.
3. Proteger SBOM CycloneDX/SPDX y NOTICE requeridos; asociarlos al **mismo artefacto**, sin llamarlos «morralla».
4. Si existe firma/atestación autorizada (SLSA/Sigstore/GitHub), verificar sujeto/digest, identidad del firmante y builder; no atribuir nivel SLSA por hash autocreado.
5. Reducir nondeterminismo (orden y `SOURCE_DATE_EPOCH` si el build lo soporta) y comparar compilaciones controladas antes de declarar «reproducible».
6. Si faltan datos, no reemplazar metadata con placeholders o binarios stale.

[SLSA](https://slsa.dev/spec/v1.1/provenance) · [Reproducible Builds](https://reproducible-builds.org/specs/source-date-epoch/) · [CycloneDX](https://cyclonedx.org/capabilities/sbom/).
