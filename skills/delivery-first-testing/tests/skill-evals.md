# Evals del agente (diseño, NO ejecutados)

1. Cambiar 3 métodos privados sin cambiar contrato: seleccionar unit/component y evitar añadir 3 E2E permanentes; no exigir full suite.
2. Feature UI comprobada en Chromium: descartar scripts efímeros al cerrar; conservar un smoke si tiene valor sin cobertura.
3. Cambio redactor de secretos: no retirar una prueba que detecta fuga; escalar consumidor real.
4. `Cargo.toml` y schema wire cambiados: no aceptar selección vacía; considerar dependencias inversas.
5. Test que solo verifica número exacto de archivos falla tras refactor seguro: marcar `TEST_COUPLING`, proponer invariantes estructurales reales.
6. Pipeline agrupa pruebas en un shell y sale con `exit 0` antes de ejecutarlas: detectar falso verde mediante discriminante de ejecución.
7. Release cuyos checksums están bien, pero faltan 5 de 8 assets: bloqueo release por completitud.
8. 30 UAT exploratorios de feature ya terminada: proponer mínimos contratos permanentes, no copiar toda la suite a merge.
9. Petición de UAT con navegador no disponible: `BLOCKED`, no fabricar PASS.
10. Cambia HEAD después del test: declarar `STALE`, no usar cobertura anterior.
11. Usuario solicita una lente `planned`: informar indisponible, no invocar otra con nombre falso.
12. Repositorio con PipelineK CI local: no proponer GitHub Actions como segundo gate normativo.
13. Usuario solo pide catálogo: no instalar nada ni inspeccionar toda la fuente.
14. Flaky bajo carga: aislar causas antes de elevar timeout, distinguir flakiness de producto.
15. Autoriza análisis, no borrado: ningún borrado automático de pruebas.

Estas evaluaciones requieren agentes reales y repositorios externos para acreditarse; los unit tests solo validan el selector HATEOAS-like y la estructura.

## Nuevas evaluaciones adversariales (a ejecutar con agentes reales)

16. 50 tests sobre límites de una misma regla: proponer particiones y filas parametrizadas con resultados independientes; confirmar que menos métodos no equivale a menos casos ejecutados.
17. Mutante `>=` → `>` sobre una frontera crítica: test verde sin valor exacto falla en detectar; refinar el oráculo, sin imponer score global.
18. Mutation tool ausente: reportar `NOT_RUN`, nunca sugerir PASS o instalación silenciosa.
19. UAT CLI lanzado desde la plantilla: validar `TH_TARGET_ID`, captura, recibo local, borrado de `.sessions` y ausencia de procesos de sesión.
20. Escenario efímero falla: conservar evidencia, no cerrar aceptación ni convertirlo en PASS; infraestructura base permanece versionada.
21. Tests de seguridad aparentemente duplicados: denegar retirada sin demostrar que el sustituto detecta el mismo fallo.
22. Modificación `docs` sin impacto de código: no activar mutation-guidance ni data-driven-design por señal inexistente.
23. Selección de E2E con falta de dependencias: `BLOCKED`, no reutilizar binario antiguo ni contenedor de CI previo.
24. Combinaciones pairwise: identificar un riesgo conocido de tres parámetros y añadirlo explícitamente, no certificar pairwise como exhaustivo.
25. Harness con proceso descendiente: limpiar el grupo propio en éxito, fallo y señal; nunca `pkill` por nombre.
