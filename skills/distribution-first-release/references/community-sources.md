# Evidencia comunitaria y fuentes primarias

Estos documentos son **fuentes de prácticas**, no autorizaciones para cambiar la política de un repositorio. Verificar versiones vigentes antes de automatizar. Se separan **propiedades documentadas** de **recomendaciones de esta skill**.

| Fuente primaria | Propiedad sustentada | Práctica derivada |
|---|---|---|
| [GitHub — About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) | Release ligada a tag, notas y assets binarios; GitHub añade source archives | No confundir fuente automática y binario subido |
| [GitHub — large files](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github) | Repositorio pequeño; publicar binarios grandes por Releases | No guardar copies ZIP en `evidence/` o `docs/` versionadas |
| [GitHub — repository limits](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits) | Outputs generados fuera de Git; límites y avisos | Analizar tamaño por árbol e historia por separado |
| [Git — gitattributes](https://git-scm.com/docs/gitattributes) | `export-ignore` excluye paths de `git archive` | Probar archives de nuevos tags sin pretender esconder código |
| [GitHub — Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage) | LFS gestiona objetos grandes versionados mediante punteros | No confundir LFS con CDN/distribución de aplicaciones |
| [SLSA — provenance v1.1](https://slsa.dev/spec/v1.1/provenance) | Builder y materiales de la build vinculados al producto | No atribuir SLSA levels sin evidencia del builder y verificador |
| [Reproducible Builds — SOURCE_DATE_EPOCH](https://reproducible-builds.org/specs/source-date-epoch/) | Timestamp reproducible, inputs controlados | Evitar timestamps volátiles cuando el build soporte el estándar |
| [CycloneDX — SBOM](https://cyclonedx.org/capabilities/sbom/) | Inventario de dependencias y relaciones de producto | SBOM no es ruido si hay obligación de distribución/compliance |
| [GitHub — artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations) | Atestación firmada de procedencia, debe verificarse | Firmar si existe plataforma autorizada; no introducir Actions por reflejo |

**Observaciones críticas:** checksum ≠ completitud; checksum sin canal autenticado ≠ firma; SBOM ≠ fuente; aplicación ZIP JVM con JAR compilados ≠ ZIP de fuentes; publicar un tag ≠ entregar paquete usable; `git rm --cached` ≠ reducir tamaño del historial; `.gitattributes` en HEAD no modifica archives de tags anteriores. Las obligaciones de licencia/NOTICE prevalecen sobre la eliminación indiscriminada de archivos.

**Prácticas comparadas:** [casos reales y separación de responsabilidades](practices-from-projects.md) · [registro Maven Central](https://central.sonatype.org/publish/requirements/) · [GitHub Maven](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-apache-maven-registry) · [GitHub source archives](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives).
