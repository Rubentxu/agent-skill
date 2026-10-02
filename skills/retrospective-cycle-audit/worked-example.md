# Ejemplo trabajado

Un ciclo real de un proyecto real (un broker de credenciales, Rust/Cedar), comprimido a lo esencial. Los nombres están abreviados; la estructura no.

## Contexto

Un ciclo anterior cerró dos hallazgos de seguridad, H1 y H2, y una/release 0.24.0. Todo el CI verde. La retrospectiva empieza sin ninguna sospecha concreta: el trabajo estaba "hecho".

## Paso 1 — reconstrucción

`git log` muestra 13 commits. El diff toca cuatro cosas: un tipo nuevo en el dominio, un cambio de firma en el registro de surrogates, tres handlers, y un script de gobernanza.

El hallazgo aparece al **cruzar** la tabla de puertas con el código, no al leer ninguno de los dos. La fila de H2 dice, en su propia prosa:

> The per-verb decisions still happen at the operation itself, where the verb is known exactly.

## Paso 2 — blast radius

Seis sitios de `policy.authorize` en todo el broker. Se listan, y para cada uno se anota qué acción Cedar evalúa:

| sitio | acción evaluada |
|---|---|
| explicación de auditoría | la que trae la petición |
| gate de emisión | `github_issue_read` o `postgres_read` |
| gate de sentencia | la que clasifique el SQL |
| puente TLS | — (otro tipo, `ConnectPolicy`) |

Cuatro sitios. Trece acciones declaradas.

## Paso 3 — refutar

La enumeración da tres acciones que no aparecen en ningún sitio: `github_issue_create`, `github_release_create`, `postgres_connect`.

Antes de escribir nada, se intenta refutar la conclusión con tresrifugios:

1. *¿Están en otro crate?* `grep` de las tres en todo el repo: sólo aparecen en el `match` que las mapea a su nombre, en las reglas del motor, y en tests.
2. *¿Hay un `authorize` genérico que las cubra?* No: el único sitio que recibe una acción del request es la explicación de auditoría, que no es un camino de aplicación.
3. *¿El default lo delata?* La política por defecto **permite** las tres. Así que bajo el default no hay diferencia observable — y por eso ningún test podía detectarlo.

La tercera es la que importa. Refuta la urgencia, no el defecto: el fallo sólo muerde a quien endurece la política, que es justo la postura que el spec recomienda.

## Paso 4 — el test rojo

Siete tests, cada uno con un control de permiso. El arnés:

- Una factoría de conectores falsa que **falla con un marcador reconocible**. Así "llegó al conector" es una afirmación positiva, no `code != Denied`.
- Un vault **abierto y vacío**. Vacío para que `lend` no pueda ser la explicación de ningún rechazo.

Observado rojo: **4 de 7**. Los mensajes de fallo fueron la prueba:

```text
Upstream, "gate-probe answered without h3-probe: the request left the policy gate"
```

Es decir: bajo una política que sólo permite lectura, la escritura **salió del gate y llegó al conector**. Positivo, no inferido.

## Paso 5 — falso éxito encontrado por el camino

Un cuarto caso falló por un motivo que no era el esperado: lo rechazó el *class binding* de H2, no la política. El mensaje:

```text
Denied, "surrogate stands for a credential of the wrong class for this operation"
```

Eso es un hallazgo en sí mismo y está en el mensaje del commit: en ese brazo, la única puerta que existía era la de clase, y era la correcta **por un motivo no relacionado**.

## Paso 6 — el fix, y un conflicto real

La primera versión del fix metió una evaluación Cedar en el camino de lectura. El gate de rendimiento se puso rojo:

```text
baseline p95 5146-6196us  →  con Cedar 6311-6489us   (presupuesto 6000us)
```

Rojo 3 de 3. Y la Measurement era **reproducible**: `PolicySet` ya está precompilado, así que ese coste es del motor y no había nada que optimizar.

Eso obligó a una decisión de diseño real: el verbo que la emisión ya preguntó **no** se vuelve a preguntar en la operación; sólo lo que excede la capacidad aceticada se re-chequea donde se usa. La regla quedó escrita:

> la puerta de emisión es la concesión de capacidad, y todo lo que la excede se re-verifica donde se usa.

## Paso 7 — la suite caza un defecto propio

El arreglo introducido traía un error de orden: comprobaba "no hay destinos declarados" **antes** de validar la sintaxis del request. Un test que ya existía —"una dirección malformada se rechaza antes de prestar la credencial"— se puso rojo.

El arreglo es de una línea conceptual: **sintaxis antes que configuración**. Una dirección malformada es un hecho sobre el *request*, y tiene que seguir siéndoloReply whatever the deployment esté configurado. Además, responder "no tengo destinos" a quien mandó basura describe la configuración del broker a un par que elige su siguiente movimiento.

Este momento vale más que el hallazgo original: demuestra que el orden de las comprobaciones es un invariante, y que la suite ya lo defendía.

## Paso 8 — el hallazgo que bloquea la release

Al intentar cerrar la release, la revisión del camino de base de datos encontró que `PostgresConnect` **sí** acepta `host` y `host_addr` del request, que la credencial se busca por `(database, role)`, y que el recurso de política `Database{name, role}` **no tiene destino**. Con `server_name` en `None` — su default — el nombre TLS esperado también venía del request.

O sea: la misma amenaza del hallazgo anterior, en la ruta donde el campo de destino sí existe. Y el UAT que la describía apuntaba a la ruta donde **no** puede ocurrir, porque esa petición no tiene campo `host`.

Eso cambió la release de "0.25 con notas" a "esto no es production ready todavía".

## Lo que este ejemplo demuestra

1. El defecto más caro apareció al **cruzar** dos fuentes, no al leer una.
2. Una afirmación en prosa dentro de un comentario es evidencia, y hay que verificarla.
3. Un default que concede hace que todo test negativo sea vacuo — y por eso la detección depende de instalar un caso que niegue.
4. Un test que falla por un motivo **distinto** del esperado es un hallazgo, no una molestia.
5. La suite debe poder cazarte a ti. Si nunca te ha señalado nada, comprueba que tiene algún caso que debería.
6. Un arreglo de seguridad puede chocar con un requisito no funcional. Cuando eso pasa, el número manda, y la medición se hace en la máquina y en el momento — no se cita de un commit anterior.
7. La<Vec> release depende de qué no sabes, no sólo de qué está verde. Y un porcentaje de avance que no distingue "ejercitado" de "cumplido" es una forma de falso éxito con formato de tabla.
