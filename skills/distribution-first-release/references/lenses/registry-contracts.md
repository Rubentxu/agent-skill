# Lente: enrutamiento y contratos de registros

**Pregunta:** ¿Qué registro nativo entrega cada artefacto y qué evidencia certifica su consumo?

Clasificar **producto** antes de elegir destino. GitHub Releases, registros de paquetes y archivo Git son superficies DIFERENTES; no duplicar el mismo JAR en todas por reflejo.

| Producto | Canal preferente | Secundario / condición |
|---|---|---|
| CLI, app, distribución multiplataforma | GitHub Releases (binario + instalador) | gestor de instalaciones si se mantiene |
| Java/Kotlin SDK o librería pública | Maven Central (consumer anónimo) | GitHub Packages o Nexus si se necesita mirror/privacidad |
| Gradle plugin | Gradle Plugin Portal si la API es el plugin DSL | Maven/Plugin marker y registros acordados |
| npm package | npmjs.com | GitHub npm registry cuando interese control de acceso |
| Python package | PyPI | índice interno cuando se requiera |
| Rust library | crates.io | Releases SOLO para CLI nativas, no como reemplazo del crate |
| Go module | VCS con tags, proxy Go | Releases para binarios |
| Imagen OCI | GHCR u otro OCI registry | Releases solo si se requiere export portable |
| Jenkins plugin | canal oficial compatible de plugins / HPI | Releases si el consumidor usa HPI directo |
| Binario genérico sin registry | GitHub Releases | object storage (política del proyecto) |

**GitHub Packages Maven/Gradle:** GitHub indica que requiere autenticación para instalar incluso paquetes públicos. Su uso público gratuito **no equivale a consumo anónimo**. No afirmar que GitHub Packages reemplaza a Maven Central para SDK abiertos sin explicar configuración de credenciales. El registry Maven/Gradle está ligado al repositorio. Publicar multi-módulo desde Gradle/Maven siguiendo el `maven-publish` real.

**Coste y elegibilidad de Maven Central (vigente 2026-10-01):** la publicación de código abierto comunitario ordinario puede mantenerse gratuita dentro de sus límites. Publisher Pro es obligatorio cuando los artefactos tienen naturaleza comercial o se superan umbrales aplicables sin exención. No prometer gratuidad automática para un SDK comercial, generado o ligado a servicios. Verificar Publisher Tier, volumen y clasificación antes de elegir canal. [Tiers y uso comercial](https://central.sonatype.org/news/20260908_publisher_tiers_commercial_use/) · [límites](https://central.sonatype.org/publish/maven-central-publishing-limits/).

**Maven Central:** publicación habitual de JAR + POM con dependencias + `-sources.jar` + `-javadoc.jar` + firmas exigidas. Esos sources son **por módulo, preparados por el build**, no el ZIP completo de GitHub. Fuentes y documentación legítimas no son morralla. Central Portal usa su propio protocolo; no asumir que un `maven deploy` legacy a OSSRH todavía funciona.

**GHCR:** imágenes OCI por nombre/tag/digest; publicar multiarch manifest/index cuando se declaró. Los assets ZIP no sustituyen pulls OCI.

**Selección verificable:**

1. Inspeccionar contrato, coste/elegibilidad vigente, límites, condiciones comerciales y disponibilidad/credenciales del proveedor con fuentes oficiales vigentes. No asumir acceso al registro, namespace, dominio de Maven Central o cuenta.
2. Declarar por producto `primary` y opcional `mirror`; no inventar obligación de duplicación. Definir coordenadas/identidad exactas y mecanismo de instalación.
3. Comprobar `publishable`, versión/compatibilidad, metadatos, integridad, firma/SBOM si son normativos, dependencias y licencias.
4. Realizar staging local sin subir; comprobar el conjunto publicado y permitir únicamente las entradas normativas. Hash de un ZIP no prueba que las coordenadas Maven existan.
5. Tras publicación, consultar el **registro remoto**, resolver/instalar una dependencia limpia o hacer pull por digest y ejecutar un smoke relevante. Validar coordenadas de TODOS los módulos publicables.
6. Registrar `PUBLISHED` por producto/canal solo tras disponibilidad remota. `CERTIFIED` es autoridad separada. Fallo o ausencia en un canal obligatorio → release global no completada.

**No automatizar por adivinación:** publicar en registries remotos y crear cuentas, tokens, dominios o tags son operaciones sujetas a permisos y consentimiento del operador.

Fuentes oficiales: [GitHub Packages Maven](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-apache-maven-registry), [GitHub Packages billing](https://docs.github.com/en/billing/concepts/product-billing/github-packages), [Maven Central requirements](https://central.sonatype.org/publish/requirements/), [Gradle publishing](https://docs.gradle.org/current/userguide/publishing_maven.html).
