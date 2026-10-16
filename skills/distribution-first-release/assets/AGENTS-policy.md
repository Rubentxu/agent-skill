# Política para AGENTS.md de repositorios de APLICACIÓN / CLI

> Plantilla **opt-in**: contrastar con ADR, SPEC y leyes de publicación existentes. No insertar ciegamente en una biblioteca/SDK o sin autoridad. No añade una nueva autoridad de publicación.

## Consumer-ready distribution — release y limpieza

1. **DONE significa distribución que se instala y funciona** desde los bytes del asset público, asociada a un tag/SHA/version/digest de producto. Tag, código fuente automático y checksum aislado **no** son una entrega.
2. **Git versiona** fuente, contratos, tests permanentes y recetas del build. No versionar ZIP/JAR de release, SBOM binarios, cachés, outputs ni evidencias pesadas en `docs/` o `evidence/`. Outputs en staging ignorado; `.gitattributes export-ignore` para próximos source archives. No borrar rastreados/historia sin autorización, digest y copia externa.
3. **Release pública**: solo paquete(s) de producto instalable por plataforma y checksum, SBOM, firma, manifiesto, licencia o NOTICE requeridos por el contrato. Lista explícita de assets esperados y comprobación de completitud *y* integridad. No adjuntar `HANDOFF.md`, XML JUnit, logs, clasificaciones, dumps de workspace, ZIP de fuentes manuales o ZIP de otros tags.
4. **Fuente automática de GitHub**: reconocer que `Source code (zip/tar.gz)` aparece por diseño, no es asset subido ni instalador. Los agentes no lo pueden «desactivar» con AGENTS.md. Enlaces del instalador apuntan a `/releases/download/<TAG>/<ASSET>`.
5. **Fronteras normativas**: preservar autenticidad, licencias, recursos runtime, SDK metadata y metadatos obligatorios. Certifier externo conserva sus recibos; no se finge `CERTIFIED` localmente.
6. **Gate antes de publicación**: examinar contenido por leaks/source/Zip Slip, comprobar binario, lanzar versión + smoke funcional en ambiente limpio, verificar checksum y versión exacta, cotejar assets remotos. En ausencia de evidencia → `NOT_RUN/BLOCKED`.
7. **No duplicar autoridad**: mantener CI/harness existente, no crear workflows paralelos ni forzar publicación o merge por estar el test verde. Una release incorrecta requiere una candidata nueva, sin reescribir artefactos inmutables.

**Higiene de decisión:** reducir ruido sin sacrificar garantías; source JAR de librería, SDK compilado independiente, LICENSE/NOTICE y SBOM normativo son casos que pueden ser legítimos. Un release de aplicación y un publish de librería son productos distintos.

Aplicar con la skill `distribution-first-release`; su router solo recomienda acciones, y `artifact_audit.py` es de solo lectura, no un certificador.
