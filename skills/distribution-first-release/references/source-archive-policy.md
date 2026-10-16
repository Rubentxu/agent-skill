# Source archive GitHub: política de poda segura

## Separar tres superficies

- `git clone`: conserva checkout e historia; **no usa `export-ignore`**. Los archivos ya commiteados siguen siendo públicos.
- GitHub `Source code (zip/tar.gz)`: snapshot del **tag**, generado mediante `git archive`; respeta los atributos de exportación de esa revisión. No es un asset manual. Los enlaces automáticos no se desactivan por editar AGENTS, README o un archivo de ignore.
- `-sources.jar` en un registro Maven: artefacto normativo de biblioteca con fuentes del módulo publicado. No es ni el source archive de GitHub ni el ZIP de workspace. No prohibirlo.

## Aplicar `.gitattributes` por proyecto, nunca indiscriminadamente

Ejemplo para un repo donde estos paths estén demostrados como ajenos a los **snapshots de fuente para consumidor**:

```gitattributes
docs/** export-ignore
test-harness/** export-ignore
tests/** export-ignore
legacy/** export-ignore
.github/** export-ignore
```

Es una **propuesta**, no plantilla de ejecución automática. Preservar código productivo, LICENSE, NOTICE, esquema/runtime resources, build scripts, wrapper, generación de código y submódulos de distribución necesarios para reconstruir/consumir la fuente. Un `docs/` con documentación requerida o `test-harness/` que genere fuentes productivas NO se excluye a ciegas. `/src/test/` se evalúa por módulo y consumidores. Los patrones `foo/**` relativos al `.gitattributes` de raíz afectan a los archivos de ese directorio; comprobar expresamente paths anidados y usar reglas lo más estrechas posible.

Comprobar desde el commit/tag del candidato:

```sh
git archive --format=tar HEAD | tar -tf -
git check-attr export-ignore -- docs/legacy.md
```

Comparar listado con allowlist requerida; examinar contenido de `https://github.com/OWNER/REPO/archive/refs/tags/TAG.zip` **tras publicar el tag** para confirmar funcionamiento remoto. Un cambio en `.gitattributes` no cambia un tag inmutable previo.

La poda no protege secretos ni restringe acceso al código de un repo público. Para desindexar ficheros sensibles o historia antigua seguir procedimiento específico de seguridad/historial, con aprobación. Evitar `git filter-repo` y force-push por defecto.

La reducción de tamaño de archivo **no** equivale a reducción del tamaño de repositorio: identificar archivos grandes activos con `git ls-files` y tamaño histórico con `git count-objects -vH`. Para outputs futuros ajustar `.gitignore`; para archivos ya versionados, decisión revisada sobre `git rm --cached` y respaldo.

Fuentes: [GitHub: source archives](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives), [Git: gitattributes](https://git-scm.com/docs/gitattributes).
