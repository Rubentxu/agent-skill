# Defaults que niegan

Un default es una **decisión de seguridad tomada sin que nadie la tomara**. Se ejecuta en cada despliegue que no escribió la configuración, que es la mayoría y siempre el primero.

## La regla

```text
ausencia de configuración  →  NIEGA
configuración explícita    →  permite exactamente lo declarado, nada más
```

Nunca al revés. Un default que concede no es "un default inseguro": es **un control que no existe**, disfrazado de comportamiento por defecto.

## Por qué importa más de lo que parece

Un default que concede tiene tres efectos, y sólo uno es visible:

1. **Visible:** alguien sin configuración tiene permisos.
2. **Invisible:** alguien **con** configuración espera que el default no importe, y no comprueba si su configuración se aplicó.
3. **Muy invisible:** la documentación puede decir "endurece esto", y el usuario que no endurece cree que endureció — porque el sistema *parece* tener un control. No lo tiene: tiene un default.

El punto 3 es el caro. Un sistema sin ninguna puerta y un sistema con una puerta abierta se comportan igual, y sólo uno de los dos se puede arreglar.

## Diseñar un default que niega

**La lista vacía es una configuración válida.** Si el vocabulario de destinos declarados está vacío, se niega todo. No es "sin configuración todavía", es una posición: este broker no lend a ninguna parte.

**La ausencia de un campo opcional no habilita nada.** Si el campo de configuración es `Option<T>` y `None` significara "usa el default", entonces el default tiene que ser el que niega, y `None` no puede significar "sin restricciones".

**El error de configuración es un error de arranque, no un comportamiento en tiempo de ejecución.** Una lista de destinos con un host malformado debe fallar al construir el despliegue. Si sólo falla en el primer connect, el despliegue parece sano y el primer cliente recibe un error de permisos.

## Defaults y pruebas

Un default que concede hace **vacua toda prueba negativa** a través de esa puerta. La forma de detectinglo es un experimento, no una lectura:

```bash
# ¿esta prueba depende de esta puerta?
# neutraliza la implementación
git stash
cargo test --test esa_prueba     # ¿se pone roja?
```

Sigue verde ⇒ la prueba no probaba esa puerta. Es un hallazgo, y suele ser el más valioso de la tanda: significa que el trabajo anterior **creía** tener cobertura donde no la tenía.

**La consequence para el diseño de las pruebas:** toda prueba negativa necesita un caso positivo gemelo con el **mismo** fixture, y ese caso positivo necesita un default que conceda. Si el default del sistema es deny-by-default, el caso positivo necesita una configuración explícita que conceda. Los dos juntos son los que hacen que la prueba signifique algo.

## Defaults que no son de configuración

El mismo razonamiento aplica más allá de la configuración:

- **El catch-all de un `match`.** En seguridad, `_ =>` es un default-deny disfrazado de atajo. En errores, suele ser un fallo silencioso. Distinguir cuál de los dos es: ¿qué hace cuando el valor es uno que el autor no pensó? Si la respuesta es "permite", es un default que concede.
- **El `unwrap`/`expect` de un valor de configuración.** Convierte "mal configurado" en un panic en vez de una negación. Un panic en un camino de seguridad puede ser un DoS, y un proceso que muere no aplica ninguna política.
- **El transporte que reintenta.** Reintentar una escritura tras un timeout no es idempotencia: es una segunda ejecución. En un camino que presta un recurso, el reintento tiene que ir contra el mismo destino declarado, nunca contra uno resuelto otra vez.

## Checklist de un default

- [ ] ¿La ausencia de configuración niega o concede?
- [ ] ¿Hay alguna combinación de ausencias que conceda?
- [ ] ¿Un error de configuración falla al arrancar, o en el primer uso?
- [ ] ¿Hay un `_ =>` en un `match` de seguridad? ¿Qué hace?
- [ ] ¿Hay un `unwrap`/`expect` sobre configuración en un camino de denegación?
- [ ] ¿Las pruebas negativas tienen su caso positivo gemelo, con un default o una configuración que conceda?
- [ ] ¿Sabes qué se rompe con este default? Si no lo sabes, el default no está diseñado: hasteencontrado.
