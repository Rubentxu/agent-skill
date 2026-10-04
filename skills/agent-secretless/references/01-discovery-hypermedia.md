# Discovery e hipermedia

## Entrada

```bash
asv agent discover --json
```

## Comprobar

1. `schema` es `asv.agent/v1`.
2. `status` es `ok`, o entiendes por qué no lo es.
3. `data.capabilities` si está presente, y `data.broker` /
   `data.installation` para saber de quién es la instalación.
4. `links`: la lista real de lo que esta máquina puede hacer.

## Selección

Escoge por `rel`/`operation`, no por texto de `description`.

El runtime publica seis relaciones: `asv://rels/status`,
`asv://rels/doctor`, `asv://rels/setup`, `asv://rels/capabilities`,
`asv://rels/credentials/list` y `asv://rels/session/run`. Son las únicas que
pueden aparecer en `links`.

El producto declara además relaciones de GitHub, PostgreSQL, firma SSH,
approvals y audit, pero están **withheld**: no se publican, y una relación
withheld no es una opción. No la busques en `links` ni la reemplaces por un
camino propio.

Nunca asumas que una capability documentada existe en esta máquina. El runtime
manda.

## Ejecución

Un `invoke` se ejecuta como proceso + argv. No concatenes una shell.

Si la operación necesita argumentos del usuario, añádelos como elementos argv
después de validar que corresponden al contrato del comando.

## Stop conditions

- schema desconocido;
- `requires_human=true`;
- relation ausente;
- estado `blocked` sin recovery link;
- runtime informa incompatibilidad.
