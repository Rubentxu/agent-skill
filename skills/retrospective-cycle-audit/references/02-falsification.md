# Falsificación

Una hipótesis de defecto es una **afirmación refutable**. Si no puedes escribir la operación que la tumbaría, no tienes una hipótesis: tienes una corazonada. Esta referencia es el procedimiento para convertir una en la otra.

## La forma de una hipótesis

```text
SI   <se rompe esta propiedad>
ENTONCES <esta entrada concreta> produce <este resultado observable>
Y     esa entrada es alcanzable desde <esta superficie pública>
```

Si no puedes rellenar las tres, todavía no es una hipótesis. "El código parece que no valida X" no es una hipótesis: es una sospecha sobre una línea.

## Refutar ANTES de creerse

Esto no es ceremonía. Refutar primero es lo que evita spends de una hora arreglando algo que ya funcionaba, y —más importante— lo que evita **dar por bueno un defecto que en realidad no lo es**, y "arreglarlo" con un cambio que rompe otra cosa.

Tres desenlaces, los tres legítimos:

| Desenlace | Qué significa | Qué escribes |
|---|---|---|
| **Refutada** | la entrada produjo el resultado correcto | "descartada, y esto es lo que la habría refutado" |
| **Confirmada** | la entrada produjo el fallo | "confirmada, y esto es lo que la habría refutado" |
| **No observable** | no puedes construir la entrada | "no pude refutar: falta X" |

El tercero es el que más se omite y el más caro de saltarse. Un hallazgo no reproducible no es un hallazgo; es una sospecha conPR de peso.

## La falsificación que más se olvida: el default que permite

Antes de escribir la prueba negativa, responde a esto: **¿qué hace el sistema por defecto en el caso que quieres negar?**

- Si el permiso por defecto concede, la política por defecto permite, o el flag por defecto está on, entonces **toda prueba a través de esa puerta pasa exista o no**. Borrar la puerta entera deja la suite verde.

Éste es el fallo de prueba más caro que existe, porque se presenta como cobertura. Se detecta con un experimento: **borra o neutraliza la implementación y mira si la prueba se pone roja.** Si sigue verde, la prueba no probaba esa puerta.

```bash
# el experimento que convierte una sospecha en evidencia
git stash            # o:checkout el commit anterior
# ejecuta la prueba que crees que cubre la propiedad
# ¿se pone roja?
```

Si la respuesta es "no se pone roja", has descubierto dos cosas: o la propiedad ya estaba cubierta por otro sitio, o la prueba no la cubría. Ambas son hallazgos. La segunda es la que importa.

## Casos contrafactuales

Una corrección se prueba con la misma disciplina que un hallazgo. Antes de dar por buena una pieza nueva, ejecuta al menos estos ocho. Los que importan son los que nadie pidió:

1. **Vacío** —集合 vacía, lista vacía, config ausente. El default.
2. **Duplicado** — la misma entrada dos veces. ¿Doble efecto o idempotencia?
3. **Reintento** — la misma entrada después de un fallo transitorio.
4. **Cancelación** — el consumidor abandona a mitad. ¿Queda estado a medias?
5. **Restart** — el estado no persistido se pierde. ¿El sistema re-degrada o se rompe?
6. **Orden distinto** — dos operaciones que se presuponen, en el orden contrario.
7. **Fallo intermedio** — el tercer paso de cinco falla. ¿Los dos primeros dejaron rastro?
8. **Datos antiguos** — un registro escrito antes de que el campo existiera. ¿Se lee?

El sexto y el séptimo son los que casi nadie hace, y son los que más quebran.

## Cuándo no tocar producción

Un hallazgo confirmado **no** autoriza un arreglo. Autoriza un arreglo *si* se cumplen las tres:

1. Escribiste el test rojo y **lo viste fallar** con el síntoma original, no con un error de compilación.
2. El arreglo mínimo que lo pone verde no toca nada fuera del radio de impacto medido.
3. Tienes el comando que demuestra que no rompiste el resto.

Si falta la primera, estás escribiendo un test nuevo, no verificando un defecto. Eso también es legítimo, pero es otro trabajo y hay que decirlo así.
