# Patrones observados en proyectos distribuibles

Son **referencias de soluciones probadas**, no permiso para instalar sus plugins ni sustituir PipelineK por GitHub Actions.

- **[GitHub CLI](https://github.com/cli/cli/releases)** distribuye ejecutables y paquetes nativos para múltiples sistemas y arquitecturas, con checksums publicados. La lista de descargas reales convive con `Source code (zip/tar.gz)`, que no es el instalador.
- **[cargo-dist / dist](https://github.com/axodotdev/cargo-dist)** separa plan, build, host, publish y announce; genera instaladores, archivos y un manifiesto de distribución. Reutilizar ese **modelo conceptual** en PipelineK sin importar su CI generada cuando esté prohibida.
- **[Vanniktech Gradle Maven Publish Plugin](https://github.com/vanniktech/gradle-maven-publish-plugin/blob/main/docs/central.md)** distingue los módulos publicables y usa Central Publisher Portal, POM, firma y sources/javadoc; útil para SDK Kotlin/Java. No asumir que está instalado.
- **[Gradle Maven Publish](https://docs.gradle.org/current/userguide/publishing_maven.html)** publica un componente con POM, variante y metadatos de módulo; una colección de JARs compilados no sustituye esas publicaciones.
- **[Maven Central requirements](https://central.sonatype.org/publish/requirements/)** documenta fuentes/Javadoc y firmas exigidas para paquetes Maven normales.
- **[Sonatype Central Portal / Gradle](https://central.sonatype.org/publish/publish-portal-gradle/)** enumera adaptadores de terceros para Gradle; protocolo OSSRH tradicional no equivale al Central Publisher Portal.
- **[GitHub Packages Maven](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-apache-maven-registry)** soporta GAV públicos con autenticación de consumidores; **[billing](https://docs.github.com/en/billing/concepts/product-billing/github-packages)** confirma gratuidad de paquetes públicos.

## Conclusión operativa

Adoptar el inventario por **producto + variante + canal + consumidor** de cargo-dist y el contrato de artefactos y metadatos de Maven, ejecutado mediante PipelineK local. No duplicar la fuente de verdad ni imponer la misma política a CLI y SDK. `-sources.jar` de Maven ≠ source ZIP automático de GitHub.

Actualizar fuentes al aplicar la skill a versiones futuras.
