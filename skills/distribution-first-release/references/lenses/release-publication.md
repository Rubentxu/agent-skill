# Lente: publicación sin falsos verdes

1. Comprobar permisos, gates y `main/tag/SHA` normativos. No publicar desde checkout sucio o candidato distinto al construido.
2. Definir allowlist exacta; comprobar **completitud** antes de publicar y **después** sobre GitHub/registry. Un SHA256SUMS de 3 archivos es válido pero NO prueba que no falten otros cinco.
3. Si GitHub tiene «immutable releases», crear draft, adjuntar todo, comprobar y publicar al final. Si hay un error tras la publicación, usar una nueva RC en vez de mutar bytes inmutables.
4. No subir ZIP de fuentes manuales, HANDOFF, inventarios, XML, caches o duplicados como assets de usuario.
5. Descargar asset remoto y probar instalación mínima; comprobar digest remoto, enlace real y metadatos. `gh release create` con exit 0 no basta.
6. Estados independientes: `CANDIDATE_PUBLISHED`, `CERTIFIED`, `STABLE`; solo el certifier correspondiente certifica.

**Salida:** URL, SHA, lista exacta de assets, digest y resultado de instalación.

[GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) · [Gestionar releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).
