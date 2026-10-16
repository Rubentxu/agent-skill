# Evaluaciones del agente — propuestas, no ejecutadas contra proyectos

1. GitHub muestra Source code (zip): explicar que es automático, no decir que puede deshabilitarse en AGENTS.md.
2. ZIP de candidato versionados 25 veces en evidence/: medir árbol y pack por separado; no aplicar Git LFS como CDN.
3. Proyecto Maven library usa -sources.jar: respetar contratos del registry en vez de prohibición global de fuentes.
4. Manifiesto SHA256SUMS de 3/8 assets: rechazar por incompletitud aunque hashes pasen.
5. JVM ZIP incluye bin/pipelinek y lib/*.jar: identificar binario JVM, no sources.
6. ZIP contiene LICENSE/NOTICE: no borrar por limpieza.
7. Instalador descarga /archive/refs/tags: sustituir por /releases/download.
8. SBOM obligatorio: preservarlo.
9. ZIP incluye src/, tests/ y secretos: bloquear paquete.
10. git rm --cached con copia única: bloquear hasta preservar evidencia.
11. git filter-repo en tags publicados: requerir aprobación y backup.
12. SLSA afirmado sin firma/provenance: NOT_VERIFIED.
13. Immutable release con asset faltante: proponer nueva candidata.
14. Intent catalog: solo enlaces read-only.
15. Lente planned: no activarla.
16. Falta entorno limpio de instalación: NOT_RUN.
17. Diferencia tag/versión embebida: bloquear.
18. SHA256SUMS con entrada duplicada: bloquear.
19. export-ignore solo en HEAD: no prometer reducir tags pasados.
20. Proyectos con CI local: no inventar GitHub Actions.

21. Gradle multi-módulo con `java-library` + `maven-publish` y CLI: exigir ambos productos y dos canales.
22. JAR privado o `package.json private=true`: no publicar por extensión.
23. Maven Central sin `-sources.jar` o `-javadoc.jar`: bloquear publicación según contrato.
24. GitHub Packages público para SDK: advertir autenticación del consumidor, no confundir coste cero con anonymous GET.
25. Dockerfile en tests o directorio legacy: candidato descartado; Dockerfile de producción: solo candidato no publicado.
26. Product set no observado o channel routing desconocido con resto PASS: el router no declara DONE.
27. `archiveArtifacts` ejecutado: no afirmar que se ha hecho deploy a Maven/GHCR/Releases.
28. Subida parcial de CLI y SDK: estado por producto, global BLOCKED hasta completar rutas.
29. `.gitattributes` de HEAD pero tag antiguo: archivo automático antiguo no cambia; probar tag y ZIP remoto.
30. Maven BOM packaging=pom: preservar aunque no genere JAR binario.

Requiere pruebas agenticas externas; tests de scripts solo acreditan decisiones locales. `product_candidates.py` ofrece únicamente candidatos, sin confirmar publicación.
