# distribution-first-release

Skill portable para **publicar aplicaciones y CLIs como productos consumibles**, sin ZIP/JAR compilados en Git ni assets públicos de fuentes, tests y handoffs. Inspirada en el patrón de router + lentes + descubrimiento de `delivery-first-testing`; **no depende de esa skill ni instala nada**.

## Activación

«¿Por qué aparece Source code (zip)?», «publica solo el binario usable», «limpia morralla de releases», «Git está engordando con ZIP de candidates», «audita assets de una RC», «prepara distribuciones JVM/Rust/Node», «compara firma/digest/SBOM».

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
- En SDK/bibliotecas, archivos fuente o documentación pueden formar parte legítima del contrato del ecosistema: no aplicar la política de aplicaciones a ciegas.
- GitHub añade *Source code* automáticamente. Reducir el tamaño del árbol con `.gitattributes export-ignore` y dejar de versionar binarios nuevos resuelve el coste principal; no elimina la UI.
- Evidencias completas en certifier/storage; assets de consumidor y metadatos **normativos** en release; notas breves y digests en texto.
- No tocar tags publicados ni reescribir historial sin autorización excepcional.

Ver [navegación](references/navigation.md), [lentes](references/lens-registry.json), [evaluaciones](tests/skill-evals.md) y [fuentes oficiales](references/community-sources.md).
