# PipelineK local: empaquetado y publicación por canal

**Responsabilidades separadas:** [distribution-first-release](../../../distribution-first-release/SKILL.md) descubre y gobierna productos/canales; esta skill ejecuta una pipeline local **real** con los comandos que el repositorio ya soporta. No inventar DSL de publish ni crear un segundo CI en GitHub Actions.

## Algoritmo

1. `pipelinek version`, `realpath`, `pipeline.kts` y `pipelinek validate` verificados. Inspeccionar build, publicaciones y tareas realmente existentes; `archiveArtifacts` no publica en Internet.
2. Recibir del router un inventario confirmado: producto + módulo + canal + coordenadas/variante + versión + condiciones normativas. No inferir que `build/libs/*.jar` es público.
3. Preparar `staging/<producto>/<version>/<channel>` fuera de Git para candidatos de UN SHA; build una vez, hashes y exact asset set. Usar tareas reales observadas: `./gradlew tasks --all`, `./mvnw help:effective-pom`, `cargo metadata`, `npm pack --dry-run`, etc. **Inspección no implica ejecutar publish**.
4. Ejecutar gates por momento: desarrollo afectado, merge contratos críticos y release distribución/compatibilidad. Probar cliente limpio desde el staging (Maven usando repository local temporal, CLI con install script, OCI digest).
5. Solicitar autorización y credenciales para cada canal remoto. Destinos: `gh release upload` para Releases, tareas `maven-publish`/Central Portal/Nexus para GAV, `podman push` o `docker push` para OCI, tooling oficial npm/PyPI/crates. Validar comandos y semántica REAL del proyecto antes de componer pipeline.
6. Ejecutar upload idempotente; no mutar bytes bajo una versión inmutable. Publicar artefactos en registros antes de anunciar release si el contrato lo exige. Reconciliar éxito parcial por canal.
7. Verificar **consumo remoto** por coordenadas Maven/NPM/PyPI, `podman pull image@sha256` o `gh release download` y smoke real. Solo entonces marcar cada ruta `PUBLISHED`.
8. Sin credenciales o proveedor inalcanzable: `BLOCKED_EXTERNAL`, estado por canal y siguiente acción; no prometer release completa ni rebajar pruebas.

## Ejemplo de responsabilidades, NO Kotlin DSL ejecutable

```text
PipelineK: verify affected → release gate → package once → stage → verify consumer
                                      |
                            release orchestration (approved)
                           /              |             \
                    GitHub Releases   Maven Central    GHCR
                         |                |             |
                   download+run       resolve GAV    pull digest
                           \              |            /
                       reconcile per-product release matrix
```

**No copiar este esquema como pipeline.kts.** El agente debe inspeccionar la DSL instalada, escribir el fichero operativo fuera del repo si esa es la política, pasar `pipelinek validate` y ejecutar positivos/negativos reales. Un stage remoto ligero no reejecuta la matriz de CI.

[Versiones y bootstrap](04-version-resolution.md) · [Autoría DSL](01-pipeline-authoring.md) · [Gates](02-agentic-loop.md) · [Decisión de destinos](../../../distribution-first-release/references/lenses/registry-contracts.md).
