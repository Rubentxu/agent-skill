---
name: distribution-first-release
description: "Orquesta releases de aplicaciones orientadas al consumidor: descubre lentes HATEOAS-like para higiene Git, selección de binarios usables, exclusión de fuentes/ruido, instalación real, integridad, procedencia y publicación; bloquea falsos verdes, sin crear pipelines paralelos ni ejecutar borrados."
---

# Distribution-First Release — una entrada, lentes bajo demanda

**Misión:** identificar y publicar **todos los productos reales** (ejecutables, librerías, SDK, plugins, imágenes) en el **canal nativo de cada consumidor**; nunca confundir GitHub source ZIP con entrega. Optimizar los source archives sin ocultar el código de un repositorio público y reutilizar PipelineK local como autoridad CI.

## Ontología

- **Source tree**: código, tests y contratos permanentes, versionados en Git.
- **Product artifact**: distribución ejecutable, componente de librería o SDK instalable como dependencia por coordenadas, imagen OCI o plugin; nunca el `git archive`.
- **Product portfolio**: inventario completo de artefactos públicamente consumibles por módulo, no solo producto principal.
- **Distribution route**: canal específico y contrato de instalación (GitHub Releases, Maven Central/GitHub Packages/Nexus, GHCR, npm, PyPI, crates.io, etc.).
- **Registry publication**: artefacto + metadata + identidad versionable + prueba de resolución remota; publicar un ZIP no equivale a subir una librería a Maven.
- **Integrity artifact**: checksum, SBOM, firma, manifiesto o atestación exigidos por la autoridad del producto.
- **Internal evidence**: logs, handoffs, inventarios, XML, trazas y probes: conservar en su autoridad, no publicarlos como paquete del usuario.
- **Release asset**: archivo subido expresamente por el publicador; distinto del `Source code (zip/tar.gz)` creado automáticamente por GitHub.
- **Candidate**: bytes inmutables con revisión, versión, digest y estados de gates; `PUBLISHED` nunca significa `CERTIFIED`.
- **Lens**: pregunta especializada y playbook de decisión. **Affordance**: enlace `rel + href` local a una guía; no es un endpoint ni una acción ejecutada.

## Router: observar → descubrir → actuar → reobservar

1. [Descubrir TODOS los productos publicables](references/lenses/product-discovery.md) por módulo desde los manifiestos y el build real, consumidores, contratos de versión, SDK, plugins y exclusiones explícitas. Helper local conservador opcional: `python3 scripts/product_candidates.py --repo /ruta/al/proyecto` (no compila, no certifica). **Nunca inferir producto público solo por extensión `.jar`**.
2. [Enrutar producto → registro](references/lenses/registry-contracts.md): biblioteca/SDK JVM preferentemente Maven Central público; GitHub Packages/Nexus por contrato o mirror; binarios CLI en Releases; OCI en GHCR. Distinguir `-sources.jar` normativos del source ZIP GitHub. Inspeccionar autorización, cuotas, credenciales, formatos y permisos antes de seleccionar.
3. Descubrir situación con [navegación](references/navigation.md) y [lens-registry.json](references/lens-registry.json). Seleccionar lentes `ready`. Router puro: `python3 scripts/affordances.py examples/session-release.json`. `product_set` y `route_set` deben ser completos antes de DONE, pero son afirmaciones del agente que requieren evidencia externa.
4. Inspeccionar **cuatro inventarios distintos**: (a) Git versionado/historial; (b) paquetes locales reales; (c) assets de GitHub Releases; (d) publicaciones en registros externos POR coordenada/versión/digest. No confundir tag o checksum correcto con completitud.
5. Definir allowlist mínima **por canal** desde especificación normativa: artefactos, plataformas, coordenadas y metadatos obligatorios. No eliminar POM, module metadata, fuentes/javadoc Maven, SBOM, checksum, firma, licencia o NOTICE exigidos.
6. [Podar ZIP automático de GitHub](references/source-archive-policy.md): `.gitattributes export-ignore` por ruta contrastada y en tag para próximos source archives; `.gitignore` solo para ficheros no rastreados. `export-ignore` no reduce historial ni oculta código público. Nunca excluir runtime, licencias, wrappers o scripts requeridos; `git rm --cached` solo con aprobación y copia autoritativa.
7. [Delegar el release gate y la publicación a PipelineK](references/lenses/publishing-pipelinek.md) cuando esté disponible. Reutilizar `pipelinek-local-ci`, sin inventar DSL ni duplicar CI en GitHub Actions. Construir UNA VEZ por revisión, verificar ABI/OS/dependencias y probar desde bytes de candidato en consumidor limpio.
8. Verificar por producto lista exacta de assets de Releases y coordenadas publicadas en registros, hashes de binarios, firmas/atestaciones cuando correspondan, versionado, documentación de consumo y pruebas independientes. Publicación y certificación externa son estados distintos.
9. Publicar por canal autorizado. Nunca subir manualmente source ZIP de workspace, dumps, handoffs o duplicados; sí fuentes empaquetadas exigidas por la norma del registro. Descargar desde Releases/registries remotos y resolver dependencias/instalar/pull; faltantes, errors o stale → `BLOCKED/FAILED`. Registrar éxito parcial por canal sin declararlo DONE global.
10. Solo proponer limpieza de historial mediante plan excepcional: **nunca reescribir tags/releases publicados ni force-push por defecto**. Tras cada acción, descubrir nuevas affordances y continuar.

## Comportamiento seguro

- **No borrar, cambiar historial, cambiar visibilidad, publicar, instalar ni hacer push sin autorización.** Los helpers son exclusivamente lectura y no crean workflows, catálogos normativos o estados de sesión.
- GitHub genera automáticamente source archives mediante `git archive`: `.gitattributes export-ignore` en el tag puede podar su contenido; NO existe un ajuste en AGENTS para esconder los enlaces. Para esos archives, no se publica un segundo ZIP a mano. Ver [política](references/source-archive-policy.md).
- No excluir del paquete licencias, NOTICE, módulos de runtime, plugin descriptors, schemas, service providers, resources o scripts necesarios. `-sources.jar` puede ser obligatorio/convencional en bibliotecas: clasificar por producto.
- No usar Git LFS como solución automática a distribuciones por release: elegir Releases/registry/object storage; LFS solo para activos que DEBEN estar versionados.
- No inventar una firma/SLSA level ni confundir hash sin autenticidad con procedencia criptográfica. Un SHA256SUMS generado del propio ZIP solo prueba integridad respecto a ese manifiesto.
- No forzar `SOURCE_DATE_EPOCH` ni borrar timestamps indiscriminadamente; habilitar reproducibilidad cuando tooling/contrato lo soporten, medir outputs.
- Un archive vacío, paquete que no arranca, fuente-only, release incompleta o evidencia de otro SHA **no es DONE**.
- Si hay bloqueo, investigar causa y alternar con acciones independientes; `BLOCKED_EXTERNAL` no es éxito global.

## Lentes

| Señal | Lente |
|---|---|
| Qué módulos, JAR, SDK y binarios son realmente productos | [product-discovery](references/lenses/product-discovery.md) |
| Qué repositorio versionable necesita cada producto | [registry-contracts](references/lenses/registry-contracts.md) |
| Automatizar publicación con CI local sin duplicar gates | [publishing-pipelinek](references/lenses/publishing-pipelinek.md) |
| ZIP/JAR compilados en Git, checkout enorme | [git-hygiene](references/lenses/git-hygiene.md) |
| Molestan los `Source code (zip/tar.gz)` | [source-archive-boundary](references/lenses/source-archive-boundary.md) |
| Muchos assets/duplicados/SBOM mal ubicado | [asset-selection](references/lenses/asset-selection.md) |
| ZIP/paquete no instalable o con basura | [package-composition](references/lenses/package-composition.md) |
| No existe prueba de instalación/actualización | [consumer-verification](references/lenses/consumer-verification.md) |
| SHA, signatures, provenance y SBOM | [integrity-provenance](references/lenses/integrity-provenance.md) |
| Handoffs, logs, recibos y suites de sesión | [evidence-separation](references/lenses/evidence-separation.md) |
| Publicación/RC/falso verde de assets | [release-publication](references/lenses/release-publication.md) |
| Historial Git inflado | [history-remediation](references/lenses/history-remediation.md) |

[Fuentes contrastadas](references/community-sources.md) · [Autodescubrimiento](references/extend-lenses.md) · [Delegación opcional](references/related-skills.md) · [Evals](tests/skill-evals.md)

**Salida mínima:** TODOS los productos con módulo/consumidor/coordenadas/versiones, canal primario y mirrors obligatorios, revisión/tag, allowlist por canal, SHA/digest, assets/registries remotos, instalación real, exclusiones de archive, gates PASS/FAIL/NOT_RUN, certificador y siguiente acción. Un helper no acredita publicación.
