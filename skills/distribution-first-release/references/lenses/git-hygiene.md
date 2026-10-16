# Lente: higiene Git

**Pregunta:** ¿Por qué crece el repositorio si el producto ya se publica en Releases?

1. Medir por separado el árbol versionado (`git ls-files` y tamaños), el historial (`git count-objects -vH`) y los archives; no confundir suma de tamaños con bytes de pack.
2. Clasificar cada entrada: fuente permanente, fixture pequeña imprescindible, distribución generada, evidencia interna o requisito normativo. No borrar por extensión sin revisar consumidores.
3. Mantener outputs en staging excluido de Git; emplear patrones `.gitignore` concretos para nuevas distribuciones (no `*.zip` global). Verificar `git check-ignore`.
4. Para ZIP/JAR ya rastreados, verificar primero copia autoritativa, digest, referencias y contratos; proponer `git rm --cached` tras autorización, como commit normal.
5. Nunca reescribir tags o releases publicados por defecto. Limpiar árbol actual no limpia historia.

**Salida:** rutas, bytes, dueño, destino, hashes, decisión, riesgo. Sin copia acreditada → BLOCKED.
[GitHub large files](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).
