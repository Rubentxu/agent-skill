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

## Evals R1–R3 (pendientes de agente real)

1. El usuario menciona “fold” y muestra un bucle Rust lineal eficiente: recomendar `KEEP_AS_IS` o inspección, no convertirlo automáticamente.
2. Servicio enorme pero con una responsabilidad cohesionada: no sugerir dividir en diez servicios.
3. Dos validadores similares pertenecen a bounded contexts con invariantes distintas: rechazar deduplicación semántica falsa.
4. El agente no puede inspeccionar base de datos ni orden de efectos: `INSPECT_MORE`, sin declarar equivalencia.
5. Un cambio que requiere compatibilidad de dos esquemas serializados: preferir `parallel-change` y no romper la lectura antigua.
6. La fase inicial menciona Kotlin pero no pide implementación: no cargar las ocho recetas ni el perfil Kotlin hasta planificar.
7. La conversación cambia de optimización a mantenimiento: recalcular el catálogo; no conservar una lente por inercia.
8. Handoff a skill no instalada: ausencia de `delegate-skill`, aunque figure en el registro como relacionada.
9. Un ADT mejora estados pero empeora compatibilidad JSON: reportar bloqueo o proponer migración explícita, no etiquetar refactor.
10. `APPLY` en selector es propuesta, no permiso para escribir ni `PASS`; verificar comandos reales y artefactos con skill de testing si disponible.
