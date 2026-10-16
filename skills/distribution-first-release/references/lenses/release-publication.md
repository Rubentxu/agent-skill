# Lente: publicación multicanal sin falsos verdes

1. Comprobar permisos, gates y `main/tag/SHA` normativos. No publicar desde checkout sucio ni distinto al candidato construido.
2. Exigir inventario de productos y [rutas](registry-contracts.md) completos antes de operar. Para GitHub Releases definir allowlist de assets; para Maven enumerar todos los GAV y POM/sources/javadoc/signaturas; para OCI cada imagen/plataforma/digest. Completitud es por producto Y canal, no solo ZIP del CLI.
3. Verificar la lista exacta de assets/paquetes antes de subir y **después** consultando los registros remotos. Un `SHA256SUMS` de 3 archivos puede pasar pero NO prueba que no falten otros cinco ni que una librería JVM esté en Maven.
4. GitHub Releases: draft cuando corresponda, adjuntar binarios e integridad sin sources ZIP manuales, HANDOFF, tests ni logs. Con `immutable releases`, comprobar y publicar al final; un asset ausente exige nueva candidata según política.
5. Maven Central/GitHub Packages/Nexus: comprobar autenticación, coordenadas, metadatos y firma; publicar con herramienta/protocolo real. No sustituir resolución real con un zip de GitHub Releases. No reescribir versiones inmutables.
6. OCI: publicar tags/digests/plataformas declaradas y verificar pull `@sha256`. Otros registros: instalar/resolver versión exacta con herramienta nativa.
7. Descargar/instalar desde remoto con entorno limpio; comparar digest/versión/contenido y ejecutar una acción funcional cuando aplique. Un upload con exit 0 no acredita consumidor ni certificación.
8. **Éxito parcial**: informar estados y URI por producto/canal; global `BLOCKED/FAILED` hasta completar todos los obligatorios, sin borrar ni compensar de modo fingido.
9. Estados independientes: `CANDIDATE_PUBLISHED`, `PUBLISHED` por canal, `CERTIFIED`, `STABLE`; solo el certificador correspondiente acredita su parte. Transmisión remota delegada a [PipelineK](publishing-pipelinek.md) si está instalado/soportado.

**Salida:** revisión SHA, cada producto, cada ruta, registro, coordenada/URI, assets completos, digest, resultado real de instalación/consumo, estado y siguiente acción.

[GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) · [Maven Central](https://central.sonatype.org/publish/requirements/) · [GitHub Packages](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-apache-maven-registry).
