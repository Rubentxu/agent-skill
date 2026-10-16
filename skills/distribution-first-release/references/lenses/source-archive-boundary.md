# Lente: archivos fuente automáticos

1. Diferenciar `/archive/refs/tags/` o `/zipball/` (source archive generado por GitHub) de `/releases/download/TAG/asset` (asset subido). El primero **no es** un ejecutable y GitHub lo añade automáticamente.
2. No prometer que AGENTS.md o una API de assets elimina esos enlaces de un repositorio público.
3. `.gitattributes` con `export-ignore` excluye directorios de `git archive` futuro. Verificar desde ref de prueba con `git archive --format=tar REF | tar -tf -`, no atribuir efecto retroactivo a tags antiguos.
4. `.gitattributes` no reduce clones ni historial; conservar LICENSE/NOTICE u otros requisitos de redistribución.
5. Separar repositorio de distribución o hacer código privado SOLO tras decisión sobre autoridad de instaladores y enlaces públicos.

**Contraejemplo:** fuentes que el proyecto quiera ofrecer por licencia/comunidad no son morralla.
[Git attributes](https://git-scm.com/docs/gitattributes) · [GitHub releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases).
