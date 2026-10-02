# Commit y cierre

## Atomicidad

Un commit = una idea que se puede revertir sin arrastrar otra. El criterio practical: **¿puedo revertir esto y que el repositorio siga teniendo sentido?**

En una corrección de seguridad, el orden importa porque el test rojo es evidencia:

```text
1  test(...)   el test que falla, con el síntoma original en el mensaje
2  fix(...)    el cambio mínimo que lo pone verde
3  docs(...)   la fila de puerta, la causa raíz, la corrección de trazabilidad
```

El commit 1 sin el 2 deja el repo en rojo, y eso es intencionado: es el **registro de la evidencia**. Si prefieres no publicar un repo rojo, commitea 1 y 2 juntos y pega en el mensaje de 2 la salida del fallo que observaste. Lo que no se puede es no tener el fallo registrado en ninguna parte.

Un commit que mezcla el fix con una reformateación, un bump de versión y una actualización de documentación es imposible de revisar y imposible de revertir parcialmente. Divídelo aunque "sea rápido".

## El mensaje

Conventional Commits estricto, en inglés, y el cuerpo explica **por qué**, no **qué**:

- Malo: `fix: add authorize_github_write and pg_destinations, refactor helpers, bump to 0.25`
- Bueno: título del problema; cuerpo con el síntoma, la causa, la decisión y la medición.

El cuerpo debe llevar la evidencia que hace el cambio creíble sin tener que ejecutarlo:

```text
Observed red, 4 of 4, every one with lends == 1:
  a_host_the_deployment_never_declared_is_refused
and in each case the response was a real TCP attempt:
"postgres transport io failed: Connection timed out (os error 110)".
```

Un mensaje que dice "arregla el problema" obliga al revisor a reconstruir el diagnóstico. Uno que pega la salida del fallo le ahorra el trabajo y le deja verificar.

## El recibo de cierre

Todo hallazgo confirmado, con o sin corrección, se registra donde el proyecto lo leerá después. Si el proyecto tiene una autoridad de estado funcionando, ahí. Si no la tiene, en el documento firmado del proyecto — porque una fila en una tabla de puertas que nadie puede chequear sigue siendo mejor que nada, siempre que su número se derive y no se teitee.

Campos, en este orden:

- **alcance** — qué se investigó y qué queda fuera
- **hallazgos** — clasificados, cada uno con su evidencia
- **corregido** — el commit, o "no, y por qué"
- **evidencia** — el comando y la salida, no la descripción
- **causa raíz** — por qué era posible, no sólo qué se rompió
- **riesgos pendientes** — lo que sigue abierto, con su radio
- **sorpresas** — lo que contradecía lo que se creía
- **siguiente** — accionable, ordenado por valor

## La sección `siguiente`

Un `siguiente` útil tiene tresProperties:

1. **Una acción concreta con un nombre de fichero o comando.** "Revisar la pasarela de auth" no es una acción; "enumerar las 13 acciones y probar cada una en producción" sí.
2. **Un orden por valor, no por comodidad.** Lo que desbloquea a más gente primero.
3. **La razón por la que sigue pendiente**, si sigue pendiente. Un follow-up sin causa anotada se re-descubre en tres meses y se vuelve a ignorar.

## Lo que nunca se hace en el cierre

- Declarar algo "hecho" sin el comando que lo demuestra.
- Corregir una cifra en un documento sin derivarla antes, y sin comprobar que el gate que dice vigilarla la habría detectado.
- Declarar cerrado un hallazgo "porque es una decisión de producto". Se registra la decisión que falta y quién la toma.
- Un handoff paralelo cuando la autoridad de estado ya existe. Dos fuentes de verdad divergen, y la segunda es la que nadie lee.
