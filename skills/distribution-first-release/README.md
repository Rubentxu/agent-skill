# distribution-first-release

Skill portable para **detectar y publicar binarios, bibliotecas, SDK, plugins y contenedores como productos consumibles** en sus canales nativos (GitHub Releases, Maven Central/GitHub Packages, OCI, etc.). El ZIP de fuentes que GitHub genera automáticamente **no es el producto**. Inspirada en el patrón de router + lentes + descubrimiento de `delivery-first-testing`; **no depende de esa skill ni instala nada**.

## Activación

«¿Por qué aparece Source code (zip)?», «publica solo el binario usable», «limpia morralla de releases», «Git está engordando con ZIP de candidates», «audita assets de una RC», «prepara distribuciones JVM/Rust/Node», «compara firma/digest/SBOM».

## Detección real de productos (solo lectura)

```bash
python3 skills/distribution-first-release/scripts/product_candidates.py --repo /ruta/al/proyecto
```

Inspecciona manifiestos Gradle, Maven, Cargo, npm, Python y Docker para proponer **candidatos** por módulo. No ejecuta comandos del proyecto ni afirma que un módulo sea público: el agente debe confirmar tareas, coordenadas, consumidores y rutas usando [product-discovery](references/lenses/product-discovery.md) y [registry-contracts](references/lenses/registry-contracts.md). Una release multi-producto solo está completa con la matriz de canales obligatorios verificada desde remoto.

Para el ZIP automático de GitHub, consultar [source-archive-policy](references/source-archive-policy.md): `.gitattributes export-ignore` excluye basura de source archives de **nuevos tags**, pero no elimina los enlaces ni oculta código del repositorio.

## Uso sin efectos

~~~bash
python3 skills/distribution-first-release/scripts/affordances.py \
  skills/distribution-first-release/examples/session-release.json

# Auditoría de solo lectura: lista EXPLÍCITA de assets esperados;
# no sube, borra, compila ni instala nada.
python3 skills/distribution-first-release/scripts/artifact_audit.py \
  --dist-dir /tmp/candidate \
  --allow pipelinek-0.62.0.zip \
  --allow SHA256SUMS \
  --allow pipelinek-0.62.0.sbom.json \
  --runtime-zip pipelinek-0.62.0.zip

python3 -m unittest discover -s skills/distribution-first-release/tests \
  -p 'test_*.py' -v
~~~

El auditor exige checksum válido de los binarios de distribución presentes en `SHA256SUMS` cuando se declara dicho manifiesto, detecta faltantes/inesperados, comprueba contenido ZIP básico y no ejecuta código. **No demuestra instalación, compatibilidad ni certificación.**

## Instalación

~~~bash
npx skills add Rubentxu/agent-skill --skill distribution-first-release --agent opencode
~~~

Publicación GitHub ≠ descubrimiento confirmado en skills.sh. El CLI no debe considerarse validado sin ejecutarlo.

## Principios de uso

- La distribución JVM canónica puede incluir `bin/` + `lib/*.jar` (bytecode, no fuente); el JDK requerido puede ser externo.
- En SDK/bibliotecas, Maven Central exige habitualmente JAR principal, POM, `-sources.jar`, `-javadoc.jar` y firmas. El ZIP de fuentes completo de GitHub NO sustituye esos artefactos.
- GitHub Packages es gratuito para paquetes públicos pero el registro Maven/Gradle exige credenciales de consumo; para librerías públicas con consumo anónimo priorizar Maven Central.
- Para múltiples productos distinguir `product_set`, `route_set`, `asset_set` y verificación remota. No llamar DONE al CLI cuando falla el SDK.
- GitHub añade *Source code* automáticamente. `.gitattributes export-ignore` puede podar su contenido sin reducir el tamaño real del checkout o historial; no elimina la UI.
- Evidencias completas en certifier/storage; assets de consumidor y metadatos **normativos** en release; notas breves y digests en texto.
- No tocar tags publicados ni reescribir historial sin autorización excepcional.

Para automatizar con CI local, [publishing-pipelinek](references/lenses/publishing-pipelinek.md) delega los gates en la skill `pipelinek-local-ci` y separa transportes externos sin duplicar tests.

Ver [navegación](references/navigation.md), [lentes](references/lens-registry.json), [evaluaciones](tests/skill-evals.md) y [fuentes oficiales](references/community-sources.md).
