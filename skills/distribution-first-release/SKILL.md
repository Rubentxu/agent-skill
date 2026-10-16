---
name: distribution-first-release
description: "Orquesta releases de aplicaciones orientadas al consumidor: descubre lentes HATEOAS-like para higiene Git, selección de binarios usables, exclusión de fuentes/ruido, instalación real, integridad, procedencia y publicación; bloquea falsos verdes, sin crear pipelines paralelos ni ejecutar borrados."
---

# Distribution-First Release — una entrada, lentes bajo demanda

**Misión:** entregar al consumidor **artefactos instalables o ejecutables reales**, completos, verificables y pequeños, sin meter distribuciones compiladas, recibos voluminosos ni morralla en Git o en los assets públicos. No equivale a esconder el código fuente de un repositorio público.

## Ontología

- **Source tree**: código, tests y contratos permanentes, versionados en Git.
- **Product artifact**: distribución instalable/ejecutable que el usuario consume, no el `git archive`.
- **Integrity artifact**: checksum, SBOM, firma, manifiesto o atestación exigidos por la autoridad del producto.
- **Internal evidence**: logs, handoffs, inventarios, XML, trazas y probes: conservar en su autoridad, no publicarlos como paquete del usuario.
- **Release asset**: archivo subido expresamente por el publicador; distinto del `Source code (zip/tar.gz)` creado automáticamente por GitHub.
- **Candidate**: bytes inmutables con revisión, versión, digest y estados de gates; `PUBLISHED` nunca significa `CERTIFIED`.
- **Lens**: pregunta especializada y playbook de decisión. **Affordance**: enlace `rel + href` local a una guía; no es un endpoint ni una acción ejecutada.

## Router: observar → descubrir → actuar → reobservar

1. Inspeccionar **tipo de producto**: `application | cli | library | sdk | container | plugin`, canales existentes, requisitos de instalación, política del repositorio (AGENTS/ADRs), CI/harness y consumidor real. **No aplicar una allowlist de aplicaciones a Maven Central, npm, crates.io u otros ecosistemas de librerías**: sus contratos pueden exigir source jars, POM, manifests, licencias o documentación.
2. Descubrir la situación observada con [navegación](references/navigation.md) y [lens-registry.json](references/lens-registry.json). Seleccionar exclusivamente lentes `ready` cuya pregunta aporte valor; `planned` no se ejecuta. Helper opcional **puro**: `python3 scripts/affordances.py examples/session-release.json`. Si no está disponible, seguir el mismo algoritmo manualmente.
3. Inspeccionar **tres inventarios distintos**: (a) ficheros grandes/versionados en Git; (b) contenido efectivo del paquete de distribución; (c) lista **completa** de assets de la release. No confundir presencia del tag o checksum correcto con completitud.
4. Definir la **allowlist mínima** antes de publicar, desde especificación normativa: artefactos de producto por plataforma/arquitectura y metadatos obligatorios. Toda exclusión de SBOM, checksum, firma, licencia, NOTICE o manifiesto exige verificar consumidores y decisiones vigentes.
5. Prevenir nuevo ruido Git: outputs compilados fuera del árbol versionado; `.gitignore` para **nuevos** archivos, `.gitattributes export-ignore` para próximos archives generados por `git archive`. `export-ignore` **no reduce historial ni suprime enlaces automáticos de GitHub**. Para archivos ya rastreados, `git rm --cached` solo previa verificación de copia autoritativa y aprobación.
6. Construir UNA VEZ por revisión, comprobar identidad de producto, contenido/ABI/OS/arquitectura y dependencias; instalar/ejecutar **esos mismos bytes** en un entorno de consumidor limpio. Nada de pasar solo tests unitarios o simular ejecución por inspección del nombre.
7. Verificar lista exacta de assets, hashes **de todos los binarios requeridos**, material normativo, firma/atestación cuando exista, digest del candidato, notas e instrucciones de actualización/rollback. Candidata publicada y certificación externa son estados distintos.
8. Publicar por canal/permiso real. No subir ZIP de fuentes manuales, dumps de workspace, handoffs ni duplicados; no ocultar licencias ni requisitos legales. Revisar inventario remoto y descargar/instalar el asset público. Errores, skips, artefactos ausentes o stale → `BLOCKED/FAILED`.
9. Solo proponer limpieza de historial mediante plan excepcional: **nunca reescribir tags/releases publicados ni force-push por defecto**. Tras cada acción, descubrir nuevas affordances y continuar.

## Comportamiento seguro

- **No borrar, cambiar historial, cambiar visibilidad, publicar, instalar ni hacer push sin autorización.** Los helpers son exclusivamente lectura y no crean workflows, catálogos normativos o estados de sesión.
- GitHub incluye *automáticamente* source archives para releases de repos públicos: no existe una regla `AGENTS.md` para desactivarlos. Evitar **subir** ZIP de fuentes como asset no equivale a eliminar esos enlaces. Separar repositorio de distribución/privatizar código son decisiones distintas y explícitas.
- No excluir del paquete licencias, NOTICE, módulos de runtime, plugin descriptors, schemas, service providers, resources o scripts necesarios. `-sources.jar` puede ser obligatorio/convencional en bibliotecas: clasificar por producto.
- No usar Git LFS como solución automática a distribuciones por release: elegir Releases/registry/object storage; LFS solo para activos que DEBEN estar versionados.
- No inventar una firma/SLSA level ni confundir hash sin autenticidad con procedencia criptográfica. Un SHA256SUMS generado del propio ZIP solo prueba integridad respecto a ese manifiesto.
- No forzar `SOURCE_DATE_EPOCH` ni borrar timestamps indiscriminadamente; habilitar reproducibilidad cuando tooling/contrato lo soporten, medir outputs.
- Un archive vacío, paquete que no arranca, fuente-only, release incompleta o evidencia de otro SHA **no es DONE**.
- Si hay bloqueo, investigar causa y alternar con acciones independientes; `BLOCKED_EXTERNAL` no es éxito global.

## Lentes

| Señal | Lente |
|---|---|
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

**Salida mínima:** producto/consumidor, revisión/tag, distribución y origen, allowlist, assets remotos, digest, comprobación de instalación, fuentes/ruido evitado, pruebas PASS/FAIL/NOT_RUN, certificador, riesgos y próxima acción. El helper no acredita una publicación.
