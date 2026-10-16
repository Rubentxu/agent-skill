# Lente: publicar artefactos con PipelineK local CI

**Pregunta:** ¿Cómo automatizar publicaciones de producto sin crear un segundo CI ni dejar gates en 73 etapas?

1. Descubrir si existe y está disponible `pipelinek-local-ci`, qué versión de PipelineK está instalada, su `pipeline.kts` por proyecto (que puede estar FUERA del repo), las tareas y las normas `AGENTS/ADR`. Delegar `bootstrap|scaffold|review|run` en la skill observada; de lo contrario proponer comandos concretos sin afirmar que la integración funciona.
2. **CI local es autoridad de gates.** PipelineK ejecuta `affected verify` en desarrollo, `integration` en merge y `release gate` al preparar candidato. No duplicar la matriz en GitHub Actions. Un trigger remoto mínimo puede actuar como transporte, sin redefinir tests.
3. Flujo de publicación por revisión fija:
   `discover products → resolve routes → build once → stage and enumerate exact bytes → verify consumer → certify gate → request publish authorization → upload per channel → read remote → install/pull remote → reconcile global inventory`.
4. Staging por `<product>/<version>/<channel>` fuera del repositorio; evitar que `archiveArtifacts` se interprete como publicación externa. `archiveArtifacts` conserva artefactos locales, **no publica automáticamente en GitHub Packages, Maven Central o GHCR**. El adaptador del canal debe ser la herramienta real (`gradle publish...`, `mvn deploy`, `gh release upload`, `docker/podman push`, `npm publish`, etc.), y validar su disponibilidad y semántica de credenciales.
5. **Gates granulares:** fallo de un módulo Maven no obliga a recompilar todo el CLI; reintentos de red se limitan al upload/verify y no alteran bytes. No regenerar candidatos tras validar el checksum. Promocionar el MISMO digest.
6. **Credenciales:** inyectadas desde operador/secret store/bindings admitidos por PipelineK; nunca en DSL, archivos Git, logs, env dumps o argumentos impresos. Si no hay auth/namespace aprobado → `BLOCKED_EXTERNAL`, no simular publicación.
7. **Idempotencia:** si la coordenada/version ya existe, comparar hash y no sobrescribir versiones inmutables. Si los bytes difieren, requerir nueva versión/RC. Publicar notas/manifest de release solo cuando TODOS los canales obligatorios sean correctos; si hay éxito parcial, informar estados por canal y bloquear cierre global, no mentir con rollback mágico.
8. **Verificación remota:** GitHub Releases lista exacta de assets excluyendo source archives automáticos; Maven/Gradle resuelve GAV desde repo limpio; npm/PyPI instala versión exacta; OCI hace pull `@sha256` y comprueba arranque cuando aplique. Los resultados de publicación son evidencia; las pruebas UAT de sesión pueden desecharse, nunca la garantía permanente de consumo.
9. **No inventar DSL** para release ni reimplementar PipelineK en Python. Consultar el runtime, validar `pipelinek validate` y ejecutar gate real. Publicaciones o pushes solo tras autorización del usuario y normas del repositorio.

**Salida:** por producto, gate que lo creó, path/digest de staging, canal, comando real, resultado de upload, URI/coordenada remota, prueba consumer y estado. Estado global = agregación verificable de productos obligatorios.

PipelineK local CI: `skills/pipelinek-local-ci/SKILL.md` · Migración CI: `skills/pipelinek-local-ci/references/03-migration-hosted-ci.md`.
