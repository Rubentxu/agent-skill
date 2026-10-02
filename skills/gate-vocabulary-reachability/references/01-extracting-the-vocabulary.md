# Extraer el vocabulario

## La fuente, y por qué no otra

El inventario sale del **`enum` / esquema / catálogo**, nunca de los usos. Un `grep` de usos por definición no devuelve lo que nadie usa, y lo que nadie usa es el objeto de la auditoría.

Orden de可靠度:

1. El `enum` que el motor consume.
2. El `match` que mapea cada variante a su nombre de motor. **Exhaustivo a propósito**, así que compila aunque una variante sea inalcanzable.
3. Las reglas del motor: cada identificador nombrado en un `permit`/`forbid`/condición.
4. Los tipos de recurso y de contexto de la política: un recurso sin un campo que una regla pueda filtrar es un recurso que **ninguna política puede restringir por ese campo**.

El cuarto es el que nadie mira y el que produce los hallazgos caros.

## Los tres millares de "elementos inertes"

| # | Qué lo delata | Por qué es peligroso |
|---|---|---|
| 1 | variante en el `enum` y en el mapeo, sin ninguna construcción | el motor lo soporta; el sistema no lo pide |
| 2 | identificador sólo en una regla del motor | **una regla que no puede dispararse**; y si el default concede, es un falso control |
| 3 | tipo de recurso sin campo que una regla pueda comparar | el operador **no puede escribir** la política que se le pide escribir |

El 3 no aparece en ningún `grep` de acciones, porque no es una acción: es una **carencia en un tipo**. Se detecta leyendo la definición del recurso y preguntando, para cada atributo que un operador querría filtrar, si existe.

Para un sistema de credenciales, la pregunta es: **¿puede un operador decir "a este servidor"?** Si el recurso es `Database { name, role }` y no tiene `host`, la respuesta es no. Y esa es la primera mitad de un agujero de exfiltración.

## Normalización: canonicaliza antes de comparar

Antes de poder afirmar que un valor "coincide" con otro, necesitas una noción de "el mismo valor". Si no existe en el proyecto, ese es el primer trabajo, y es más barato que cualquier arreglo de allowlist.

Una función de canonicalización de autoridad que debe:

- rechazar mayúsculas mixtas → no, **normalizarlas**
- normalizar mayúsculas y el punto final
- rechazar espacios circundantes (en vez de recortarlos: un espacio nunca es una grafía legítima de un host)
- rechazar userinfo (`@`), percent-encoding (`%`), separadores de ruta y de puerto
- rechazar literales IP donde se espera un nombre

La misma función se aplica a los dos lados de **toda** comparación de una lista de permitidos. Aplicada a un solo lado, deja huecos; aplicada a los dos, cierra las dos direcciones a la vez.

## Inventario de defaults, en la misma pasada

Para cada control que hayas encontrado, anota su default antes de seguir. Es el dato que convierte una lista de Observationes en una lista de severidades:

```text
elemento          declarado en      construido en     default      veredicto
Action::Foo       policy.rs:34      broker.rs:926     concede      FALSO CONTROL
Action::Bar       policy.rs:34      —                 concede      FALSO CONTROL
Action::Baz       policy.rs:40      broker.rs:926     niega        deuda
```

La cuarta columna es la que se lee primero, y es la que decide si algo bloquea un release.

## Formato de salida

Una fila por elemento declarado, incluidas las variantes que nadie usa. Si el total no cuadra con el `enum`, el inventario está mal y hay que rehacerlo antes de sacar conclusiones. Este控制 lo hapillado antes: un `range` reconstruido a mano que se quedó corto y dejó dos elementos vivos marcados como ausentes.
