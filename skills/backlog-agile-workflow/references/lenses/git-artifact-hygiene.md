# Lente: detectar y retirar documentación de gestión del índice Git

**Cuándo:** antes de iniciar Backlog.md, antes de generar documentación de proyecto, al preparar commits o al revisar un repositorio con ADR/ROADMAP/SPEC/ZIP rastreados.

**Navegación:**
1. Consultar [política completa](../repository-hygiene.md) y configuración local de Backlog.md.
2. Ejecutar **solo la auditoría de lectura** `scripts/git_artifact_guard.py --repo . --check` en la aplicación consumidora. Clasificar ZIP y documentos por función, sin asumir que todos los Markdown son privados.
3. Presentar inventario, copias de seguridad/colaboración y cambios de `.gitignore` propuestos; `git rm --cached` nunca se ejecuta sin consentimiento específico.
4. Verificar `git status`, `git diff --cached`, `git ls-files`; bloquear publicación/commit si quedan artefactos sin resolver.
5. Si el origen estuvo rastreado antes, indicar exposición histórica. Ningún script de la skill borra bytes ni reescribe historia.

**Salida:** `CLEAN | REVIEW_REQUIRED | BLOCKED`, rutas, tipo, acción propuesta, aprobación necesaria y riesgos de historial/sincronización.
