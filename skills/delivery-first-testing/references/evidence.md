# Criterios de evidencia y anti-falsos verdes

Antes de aceptar un PASS comprobar: qué comando o interacción se ejecutó, qué fuente/HEAD o artefacto concreto, salida y exit/evento, tests seleccionados frente a tests realmente ejecutados, skips, entorno y versión relevante, y un caso negativo que confirme que el observador detecta errores cuando esa garantía está en riesgo.

Un `exit 0` de shell puede ocultar un fallo por `|| true`, pipe sin `pipefail`, `exit` prematuro o pruebas omitidas. Una compilación contra binario antiguo no valida un commit reciente. Un checksum de assets existentes no garantiza completitud de una release. Un assert de existencia sin comprobar contenido puede pasar aunque el producto esté roto. No multiplicar pruebas anti-vacuidad: una comprobación discriminante sobre la frontera correcta basta si protege varias suites.

### Recibo mínimo (texto, no ledger nuevo)

```text
Capacidad: ... / Garantías: ...
Fuente/artefacto: SHA + clean/dirty o digest
Comprobación: comando real y escenario observable
Resultado: PASSED | FAILED | BLOCKED | NOT_RUN
Cobertura: casos que corrieron; skips y exclusiones
UAT efímero: qué comprobó; decisión RETIRE | PROMOTE | REPLACE
Evidencia permanente: test y garantía (si procede)
Riesgos residuales / siguiente acción de entrega: ...
```

Guardarlo en el sistema de registro ya existente si el proyecto lo exige. No crear un directorio de recibos dentro del repo de forma automática. Sin recolección real, informar `NOT_RUN`.
