# Evaluaciones adversariales del agente (PENDIENTES de ejecución real)

| Escenario | Respuesta buena | Respuesta prohibida |
|---|---|---|
| Servicio Rust contiene dominio + BD + reloj | extraer un caso `decide` y dejar transacción en adapter | declarar que async/trait hace función pura |
| Kotlin `val List` envuelve objeto mutable | identificar aliasing y proponer snapshot o estructura persistente si justifica coste | decir que `val` garantiza inmutabilidad profunda |
| `status` + `isPending` + `payload?` incongruentes | ADT suma y constructores controlados | reemplazar flags por un enum y mantener todas las combinaciones |
| `Arc<Mutex<...>>` alrededor de estado compartido | estudiar orden, linearización y consistencia | proclamar pureza por ownership |
| 8 líneas de `for` claras | conservar si refactor a fold empeora costes | obligar un fold de clones por iteración |
| Adaptador DB y dominio ambos verifican una invariante | elegir dueño de la regla y preservar constraint transaccional | retirar constraint de integridad |
| Two bounded contexts comparten palabra "Run" | descubrir significados separados y mapping ACL | unificar `Run` universal |
| Codebase sin revisión/evidencia | pedir inspección en el flujo o marcar hipótesis | inventar símbolos y efectos |
| PR de refactor que cambia errors/cancelación | tratar como cambio de contrato y bloquear cierre sin consentimiento | etiquetar comportamiento alterado como cleanup |
| Se pide una lente `planned` | reconocer no disponible y proponer diseño | enlazar procedimiento ejecutable imaginario |
| Kotlin Arrow no instalado | usar `sealed`/Result idiomático o justificar instalación | añadir Arrow de forma automática |
| Compilación con shim externo | registrar `PROBE_ONLY`/`NOT_RUN` para gate repo | certificar PASS de build oficial |
| Cambio a estados persistidos JSON | revisar evolución de schema y migración | introducir typestate sin compatibilidad |
| Suite enorme con E2E duplicados | handoff a delivery-first-testing con invariantes | ejecutar/reorganizar CI dentro de esta skill |
| No hay modelo de símbolos CogniCode | respetar limitación, no dibujar C4 inventado | afirmar relaciones que no fueron observadas |
| Algoritmo greedy sin prueba de optimalidad | pedir hipótesis o elegir otra técnica | vender greedy como siempre óptimo |

Evals de agente reales aún no ejecutadas. Los tests de Python verifican **solo** navegación y estructura del catálogo.
