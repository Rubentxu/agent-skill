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

Requiere pruebas agenticas externas; tests de scripts solo acreditan decisiones locales.
