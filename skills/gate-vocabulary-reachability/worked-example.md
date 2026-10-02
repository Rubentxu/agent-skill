# Ejemplo trabajado

Proyecto real: un broker de credenciales en Rust con Cedar. Tres hallazgos en un ciclo, el tercero encontrado al intentar cerrar la release.

## El inventario

`POLICY_TEXT` declara trece acciones. Trece, de un `enum` exhaustivo:

```text
GitFetch · GitPush · SshConnect · HttpRequest · PostgresConnect
GitHubIssueCreate · GitHubIssueRead · GitHubReleaseCreate
PostgresRead · PostgresInsert · PostgresCreateTable
PostgresDropTable · PostgresAlterTable
```

Y el motor tiene **cuatro** puntos de evaluación en todo el broker:

| # | sitio | qué evalúa |
|---|---|---|
| 1 | explicación de auditoría | la que trae la petición |
| 2 | gate de emisión | `github_issue_read` o `postgres_read` |
| 3 | gate de sentencia | la que clasifique el SQL |
| 4 | puente TLS | — (otro tipo, sin acción Cedar) |

## La intersección

Tres acciones no aparecen en ninguna fila: `github_issue_create`, `github_release_create`, `postgres_connect`.

Se refutó antes de creerlo. Tres intentos:

1. *¿En otro crate?* `grep` de las tres en todo el repo: sólo el `match` que las mapea a nombre, las reglas del motor, y tests.
2. *¿Hay un punto genérico que las cubra?* El único que recibe la acción del request es la explicación de auditoría, que no es un camino de aplicación.
3. *¿El default lo delata?* La política por defecto **permite** las tres. Bajo el default no hay diferencia observable — y por eso ningún test podía detectarlo.

El tercer intento es el que clasifica: el default concede, así que no es deuda inerte. Es un **falso control**: el operador puede escribir una política que niegue `github_issue_create`, y el broker se la queda.

## El comentario

El código afirmaba, junto al gate de emisión:

> The per-verb decisions still happen at the operation itself, where the verb is known exactly.

Era falso, y era la **única** garantía del invariante: no había rama, ni llamada, ni diff que lo respaldara. Un revisor no tenía nada que revisar. Por eso sobrevivió a un ciclo entero y a una release.

## El arreglo, y el conflicto

El arreglo natural —evaluar el verbo exacto en cada operación— puso rojo el gate de rendimiento:

```text
baseline p95 5146-6196us  →  con Cedar por operación 6311-6489us   (presupuesto 6000us)
```

Rojo 3 de 3, y la medición **reproducible**: `PolicySet` ya venía precompilado, así que ese coste era del motor y no había nada que optimizar. La razón original de_no evaluar por operación ("cuesta caro") era correcta; lo que estaba mal era la premisa escrita que la acompañaba.

La regla que quedó:

> la puerta de emisión es la concesión de capacidad, y todo lo que la excede se re-verifica donde se usa.

El verbo que la emisión ya preguntó no se vuelve a preguntar. Sólo lo que la excede.

## Lo que encontró la suite

El arreglo traía un defecto de orden propio: comprobaba "no hay destinos declarados" **antes** de validar la sintaxis del request. Lo cazó un test que ya existía por otra razón —"una dirección malformada se rechaza antes de prestar la credencial"— y que se puso rojo.

Corregirlo fue una línea conceptual: **sintaxis antes que configuración**. Una dirección malformada es un hecho sobre la petición y tiene que seguir siéndolo, porque al revés respondes a una pregunta que no se ha hecho y describes la configuración del despliegue a un par que elige su siguiente movimiento.

## El tercero: el destino

Al revisar la release, el camino de base de datos mostró que su petición **sí** acepta `host` y `host_addr`:

```text
Request { session, host, host_addr, port, database, role }
```

Y que:

- el recurso de política es `Database { name, role }` — **no hay `host` en él**;
- el lookup de credencial es `credential_for(database, role)` — **no hay host**;
- el nombre que se comprueba contra el certificado venía del request, porque el campo de configuración que lo sobrescribía estaba en `None` — su default.

Un operador que concedía `postgres_read` sobre `app`/`readonly` había concedido **cualquier host**, y el sistema lo documentaba como si hubiera concedido un servidor.

Y el UAT que describía esa amenaza apuntaba a la ruta donde **no puede ocurrir**, porque esa petición no tiene campo `host`. El test estaba en el sitio imposible, y el agujero en el posible.

Eso convirtió la release de "nota de versión" en "esto no es production ready todavía".

## Las tres propiedades transferibles

1. **La intersección es barata y es el hallazgo caro.** Cuatro `grep` encontraron tres verbos muertos que nadie había visto en dos ciclos.
2. **Un default que concede convierte la deuda en mentira.** Es lo que separa "inerte" de "falso control", y es una columna de una tabla.
3. **El release depende de lo que no sabes.** Los dos primeros hallazgos seстяan cerrado en verde. El tercero salió al preguntar qué se iba a publicar como "production ready", y entera la afirmación.
