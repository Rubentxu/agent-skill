# Lente: descubrir productos publicables

**Pregunta:** ¿Qué se entrega de verdad desde este commit, a quién y mediante qué coordenada instalable?

1. Inspeccionar TODOS los módulos y subproyectos desde el código y el build real, no los `docs/roadmap`, extensiones ni nombres de archivos aislados. Recorrer `settings.gradle(.kts)`, `build.gradle(.kts)`, `pom.xml` y módulos Maven, `Cargo.toml` (workspace + `publish = false`), `package.json` (`private`, `bin`, `exports`), `pyproject.toml`, `go.mod`, manifiestos OCI y scripts de empaquetado. Incluir plugins y SDK publicables independientes.
2. Inspeccionar salidas, tareas y publicaciones REALES: `maven-publish` + `MavenPublication` / `components`, `mvn help:effective-pom`, `gradle outgoingVariants` donde exista, `cargo metadata`, `npm pack --dry-run --json`, `python -m build` cuando el proyecto lo admita. No ejecutar builds, tareas de publish o instalaciones como parte de la inspección de solo lectura sin autorización.
3. Cada candidato debe declarar **ID de producto**, módulo, tipo (`cli|application|library|sdk|plugin|container`), consumidores, artefactos primarios, variantes de SO/arquitectura, identificador de consumo (coordenadas Maven, paquete npm, tag OCI, comando instalador…), versión, canal principal y dependencias de runtime.
4. Separar **candidato observado** de **producto contractual**. Encontrar un JAR en `build/libs` NO prueba que sea una biblioteca pública: puede ser un módulo interno, fixture, fat JAR de aplicación o tarea abandonada. Una regla `publish = false` o `private: true` impide asumir publicación.
5. Reconciliar con especificaciones/ADRs y publicaciones previas. Para un monorepo, usar un inventario POR PRODUCTO; un solo `product=cli` no acredita el SDK y las librerías que también deban distribuirse.
6. Cada candidato queda `confirmed|excluded|uncertain`, con evidencia (ruta/tarea/contrato). Resolver incertidumbres antes de `DONE`. Para `excluded`, conservar motivo: módulo interno, demo, tests, producto retirado o no distribuible.
7. Emitir inventario de productos **y matriz de versiones**. Release de aplicación y publicación de SDK pueden compartir SHA pero no se pueden sustituir mutuamente.

**FAIL:** publicar solo el ZIP de aplicación cuando existen SDK/JAR explícitamente publicables; asumir que todo `*.jar` debe publicarse; transformar módulos internos en API pública.

**Salida:** matriz `producto → módulo → contrato consumidor → artefacto → versión → canal → evidencia → estado`.

**Autoridad:** el build + contratos existentes; esta lente no crea una segunda fuente de verdad.
