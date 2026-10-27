# Lente: núcleo funcional, puertos e intérpretes de efectos

**Pregunta:** ¿cuáles son reglas deterministas y cuáles requieren mundo externo? **Señales:** `side-effects`, `large-service`, `duplicate-logic`.

## Algoritmo de extracción

1. Dentro de un caso de uso observar red/BD/reloj/aleatoriedad/archivo/logging, lecturas de configuración, hilos y mutaciones compartidas. Marcar cada punto de efecto.
2. Extraer primero la parte más barata de la regla, **sin cambiar** secuencia de operaciones ni garantías. Identificar el contexto mínimo explícito (`now`, permisos, snapshot de inventario, configuración validada).
3. Diseñar `decide(state, command, context): Result<Decision, DomainError>`; `Decision` contiene `nextState`, `events` y, si es adecuado, intents (`ScheduleJob`) sin ejecutar nada.
4. Dejar al application handler: parsear, autenticar, cargar snapshot, aportar contexto, llamar al núcleo, persistir/emitir de forma transaccional si hace falta, traducir errores y responder. No introducir transacciones inexistentes.
5. Inspeccionar TOCTOU, concurrencia, idempotencia, reintentos y atomicidad: la pureza de una decisión no garantiza aislamiento. Situar chequeos bajo constraints/locks en la frontera cuando corresponda.
6. Evaluar si puertos por función o trait/interface pequeño mejoran testabilidad. Usar un "port" únicamente cuando una decisión necesita separar dependencia real; no crear una interfaz por clase.
7. Comparar antes/después por escenarios y invariantes, sin cambiar observación pública ni temporización relevante.

**Contrapruebas:** `suspend fun`/`async fn` pueden tener IO; pasar un repositorio a una función llamada `pureDecide` no la hace pura; leer `System.currentTimeMillis()` escondido en un singleton rompe determinismo.

**Resultado:** efecto→frontera→operación, firma del core, responsable de persistir/publicar, garantías de orden/transacción y tests selectivos.
