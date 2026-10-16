# Lente: descontaminar Git con seguridad

1. Medir por separado árbol actual, pack histórico y archivos source ZIP. `git ls-files`, `git count-objects -vH` y `git-sizer` si está disponible.
2. Localizar copias únicas y dependencias históricas; validar antes de retirar un ZIP que exista en Release/registry/storage, con digest y referencia estable.
3. `.gitignore` impide nuevas altas; `git rm --cached` retira archivos **rastreados del árbol actual** tras autorización, sin borrarlos localmente. Un commit normal respeta tags.
4. `.gitattributes export-ignore` puede reducir archivos Git archivados **desde refs futuros**; no reduce historial/clones ni cambia tags pasados.
5. Reescritura por `git filter-repo`, force push o eliminación de tags publicados requiere plan excepcional, backups, consumidores identificados y autorización explícita. Por defecto: prohibida.

**Salida:** ahorro proyectado, riesgos, referencias, pasos reversibles y estado BLOCKED si falta copia validada.
