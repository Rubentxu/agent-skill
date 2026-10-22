# Criterios de evidencia y anti-falsos verdes

Antes de aceptar un PASS comprobar: qué comando o interacción se ejecutó, qué fuente/HEAD o artefacto concreto, salida y exit/evento, tests seleccionados frente a tests realmente ejecutados, skips, entorno y versión relevante, y un caso negativo que confirme que el observador detecta errores cuando esa garantía está en riesgo.

Un `exit 0` de shell puede ocultar un fallo por `|| true`, pipe sin `pipefail`, `exit` prematuro o pruebas omitidas. Una compilación contra binario antiguo no valida un commit reciente. Un checksum de assets existentes no garantiza completitud de una release. Un assert de existencia sin comprobar contenido puede pasar aunque el producto esté roto. No multiplicar pruebas anti-vacuidad: una comprobación discriminante sobre la frontera correcta basta si protege varias suites.

### Comprobación de reducción y aceptación

Antes de retirar una prueba, identificar la garantía, un fallo que ella detectaba, qué test restante la detecta y la comparación rojo/verde o mutación focalizada cuando aporte valor. La reducción se mide por tiempo y mantenimiento recuperado, no por cantidad de métodos. Parametrización no reduce automáticamente ejecuciones.

En UAT efímero registrar el ID de sesión, artefacto/commit, escenario y aserción discriminante, salida/errores y prueba permanente sustituta cuando exista. Registrar la aceptación *antes* de borrar escenarios; nunca versionar logs sensibles. El harness puede conservar recibos locales ignorados por Git, y el proyecto puede trasladar las evidencias sanadas a su registro autorizado.

### Recibo mínimo (texto, no ledger nuevo)

```text
Capacidad: ... / Garantías: ...
Fuente/artefacto: SHA + clean/dirty o digest
Comprobación: comando real y escenario observable
Resultado: PASSED | FAILED | BLOCKED | NOT_RUN
Cobertura: casos que corrieron; skips y exclusiones
UAT efímero: run_id, qué comprobó; decisión RETIRE | PROMOTE | REPLACE | DEFER
Evidencia permanente: test y garantía (si procede)
Riesgos residuales / siguiente acción de entrega: ...
```

Guardarlo en el sistema de registro ya existente si el proyecto lo exige. No crear un directorio de recibos dentro del repo de forma automática. Sin recolección real, informar `NOT_RUN`.

## Pruebas parametrizadas y límites de evidencia

- Reportar **número esperado, seleccionadas, ejecutadas, fallidas y saltadas** por *revisión exacta*; una factoría que produce cero casos no acredita la garantía. Los ID de los casos deben permitir identificar cuál quedó rojo.
- Una reproducción aislada con compilador, JUnit simulado o stubs ajenos al build sirve para explorar el oráculo, pero su estado es **PROBE_ONLY**; el gate oficial permanece `NOT_RUN`. No convertir una prueba de sintaxis o mutación local en resultado Gradle/JUnit certificado ni fusionar bajo esa premisa.
- La mutación `KILLED` exige que el runner llegara al test y **fallara una aserción relacionada**; un error de compilación, dependencia ausente, timeout no explicado o suite no descubierta es `INVALID/NOT_MEASURED`, no mutante eliminado.
