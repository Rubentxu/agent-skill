# Alcanzabilidad: extraer y probar

## Extraer el vocabulario sin perder la variante muerta

El riesgo de esta fase es perder exactamente lo que buscas. Si haces el listado desde los `grep` de uso, la variante que nadie usa desaparece del inventario — y la variante que nadie usa es el hallazgo.

**Fuente única de verdad:** el `enum`, el esquema o el catálogo. Nunca una búsqueda de usos.

```bash
# el enum completo, con sus variantes
sed -n '/pub enum Action {/,/^}/p' src/domain.rs

# el match que le da nombre al motor: SIEMPRE exhaustivo, y por eso es
# donde sobreviven las variantes muertas sin previo aviso
sed -n '/fn action_name/,/^}/p' src/policy.rs
```

Ese `match` que mapea cada variante a su nombre de motor tiene un detalle que lo hace peligroso: **es exhaustivo a propósito**, así que compila aunque nadie construya la variante. Un `_ => "unsupported"` que se coló en un sistema real hizo exactamente eso: colapsaba toda acción semántica a un nombre que ninguna regla podía autorizar, y el motor funcionaba perfectamente sobre un vocabulario que no tenía salida.

**Las reglas del motor.** Cada identificador que aparece en una regla debería aparecer en la columna de construcción. Los que no, son `rule-only`.

```bash
# qué identificadores nombra el motor
grep -oE '[a-z_]+::"[a-z_.]+"' src/policy.rs | sort -u
```

## Probar la alcanzabilidad sin engañarte

La intersección es mecánica. Lo que no lo es es la **interpretación de los falsos negativos**, y aquí está el error que hace que esta auditoría se descarte:

**"No aparece en producción" no significa "no se construye".** Puede que se construya en otro crate, o dinámicamente, o a través de una función que lo toma como parámetro. Antes de declarar algo muerto:

1. `grep` en **todo** el repo, no sólo en el crate del motor.
2. Busca el **tipo**, no el literal: `Action::` y no `"github_issue_create"`. El motor ve el enum; el código lo nombra como variante.
3. Mira si algún punto de evaluación **recibe la acción como parámetro** en lugar de construirla. Ése es el caso que salva más falsos positivos y el que más fácil se pasa por alto.
4. Si el punto de evaluación es una **explicación/diagnóstico** y no un camino de aplicación, no cuenta. Una pantalla de "por qué se denegó esto" puede nombrar cualquier acción sin que exista forma de pedirla.

## La intersección

```text
declarados  =  enum ∪ reglas del motor
construidos =  ⋃ { acciones que evalúa cada punto de evaluación en producción }
vivos       =  declarados ∩ construidos
```

Clasifica `declarados \ construidos` en tres, y anota el **sitio donde debería construirse** para cada uno:

| clase | aparece en | veredicto base |
|---|---|---|
| `mapped-only` | sólo el `match` nombre | el motor lo soporta; nadie lo pide |
| `rule-only` | sólo una regla | una regla que no puede dispararse |
| `test-only` | sólo tests | cobertura de algo que producción no hace |

El "sitio donde debería construirse" es la mitad accionable del informe. `github_issue_create` muerto **en el handler `CreateIssue`** es un arreglo local. Muerto en tres sitios sugiere un diseño que nadie terminő, y eso es un hallazgo de arquitectura.

## Casos borde que cambian el veredicto

- **El punto de evaluación es un único verbo representante.** Si el gate de emisión evalúa un verbo "read" como representativo de una familia de tres, los otros dos verbos de la familia están `mapped-only` **por diseño**, no por descuido. Eso es una decisión, y se escribe. Lo que sigue siendo un defecto es que **nadie lacribió** y el comentario afirmaba lo contrario. El bug no es la ausencia de evaluación por operación: es **afirmar que existe** cuando no.
- **El camino es inalcanzable por otra razón.** Una acción sólo se construye en un camino que ningún request alcanza. Está viva en el `grep` y muerta en la realidad. Para detectarlo: mira si el `enum` de requests tiene una variante que nadie construye, o si un handler tiene una guarda que siempre devuelve.
- **El motor lo evalúa, pero el resultado se ignora.** Un punto de evaluación que llama al motor y **no mira** la decisión. Búsqucalo: llamadas a `authorize` cuyo valor de retorno se descarta. Éste es el peor caso, porque el código *parece* autorizada.

## El pregunta que cierra la auditoría

Para cada elemento muerto, responde con una frase: **¿qué podría hacer un atacante que hoy no puede?**

- Si la respuesta es "nada, porque el default ya lo niega", es deuda: se registra, no se arregla.
- Si la respuesta es "concederse un permiso que el operador cree haber negado", es un falso control: HIGH, y es el único caso que justifica bloquear un release.

El 90% de los verbos muertos son el primer tipo. Ese uno solo justifica todo el trabajo.
