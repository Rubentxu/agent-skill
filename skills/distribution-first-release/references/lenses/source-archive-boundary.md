# Lente: archivos fuente automáticos

1. Diferenciar `/archive/refs/tags/` o `/zipball/` (source archive generado por GitHub) de `/releases/download/TAG/asset` (asset subido). El primero **no es** un ejecutable y GitHub lo añade automáticamente.
2. No prometer que AGENTS.md o una API de assets elimina esos enlaces de un repositorio público.
3. GitHub documenta que los archivos fuente se generan con `git archive`. `.gitattributes export-ignore` (COMMITTEADO EN EL TAG) excluye paths de nuevos source archives. Comprobar `git archive --format=tar REF | tar -tf -` y luego descargar el ZIP del tag remoto. No atribuir efecto a tags existentes.
4. `.gitignore` afecta archivos nuevos no rastreados; `.gitattributes` reduce exportación, no checkout/clon ni historia pública. No considerarlo mecanismo de seguridad. Mantener LICENSE/NOTICE, scripts/build wrappers y elementos necesarios para el consumidor.
5. `-sources.jar` Maven no es el source archive automático: normalmente ES obligatorio junto al JAR principal; suprimirlo rompe el SDK.
6. Separar repositorio de distribución o hacer código privado SOLO tras decisión explícita sobre autoridad de instaladores, licencias y enlaces públicos.

**Procedimiento con plantilla y contraejemplos:** [política de source archives](../source-archive-policy.md).

**Contraejemplo:** archivos fuente que los usuarios necesitan para compilación, auditoría de licencia o contribuciones NO son morralla. `export-ignore` no borra archivos históricos.
[Git attributes](https://git-scm.com/docs/gitattributes) · [GitHub source archives](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives).
