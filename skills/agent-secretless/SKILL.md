---
name: agent-secretless
description: "Opera Agent Secretless Vault (ASV) sin exponer credenciales: descubre capacidades reales mediante la CLI agent-facing, ejecuta trabajo secretless, diagnostica instalación y sesiones, y respeta los human gates. Úsala cuando un agente necesite Git, SSH, GitHub, PostgreSQL u otras operaciones soportadas por ASV sin recibir el secreto, o cuando haya que instalar, comprobar o diagnosticar ASV."
metadata:
  version: "0.2.0"
  asv-agent-schema: "asv.agent/v1"
---

# Agent Secretless — router agent-first

ASV es la autoridad determinista. Esta skill **navega** el producto; no reimplementa vault, policy ni workflows.

> Entrada canónica: `asv agent discover --json`.

## Modos

| Modo | Cuándo | Referencia |
|---|---|---|
| `discover` | saber si ASV está disponible y qué puede hacer | [`references/01-discovery-hypermedia.md`](references/01-discovery-hypermedia.md) |
| `setup` | instalar/bootstrap, broker ausente, instalación legacy | [`references/02-install-setup.md`](references/02-install-setup.md) |
| `execute` | ejecutar trabajo protegido por ASV | [`references/03-execution.md`](references/03-execution.md), y sólo si hace falta `04-integrations.md` |
| `diagnose` | error, schema/protocol mismatch, estado degraded/blocked | [`references/06-diagnostics.md`](references/06-diagnostics.md) |
| `operator` | approvals/audit/metadata con intervención humana | [`references/05-approvals-audit.md`](references/05-approvals-audit.md) |

Si la intención es ambigua, empieza por `discover`. Carga `00-decision-tree.md` sólo al decidir el modo.

## El sobre que devuelve el runtime

Cada respuesta agent-facing es el mismo sobre. Estos son los ocho campos y
ninguno más; lo que no está aquí no viene del producto.

```text
schema            asv.agent/v1
product_version   versión del producto instalado
protocol_version  entero del protocolo de enlace
status            ok | blocked | degraded
data              carga útil de la respuesta
error             { code, message }, presente cuando status no es ok
links             relaciones que el runtime ofrece ahora
warnings          [{ code, message }], no bloquean
```

`data` lleva `broker`, `installation` y `capabilities` en discovery, y el
resultado de la operación cuando invocaste un `link`. El `result` de la
aplicación (`ok` o `refused`) lleva en su `data` las `entries` de una lista.

## Relaciones publicadas

El runtime publica trece y sólo trece. Si una no aparece en `links`, no existe
para ti en esta máquina.

| Rel | Para qué |
|---|---|
| `asv://rels/status` | estado del broker y de la instalación |
| `asv://rels/doctor` | salud de instalación y broker |
| `asv://rels/setup` | crear layout runtime, vault y servicio |
| `asv://rels/capabilities` | capacidades reales, no documentadas |
| `asv://rels/credentials/list` | metadatos de credenciales almacenadas |
| `asv://rels/session/run` | ejecutar un programa dentro de una sesión |
| `asv://rels/github/issue/read` | leer un issue con credencial prestada por el broker |
| `asv://rels/github/issue/create` | crear un issue con credencial prestada por el broker |
| `asv://rels/github/release/create` | crear un release con credencial prestada por el broker |
| `asv://rels/registry/manifest/read` | leer un manifiesto OCI |
| `asv://rels/registry/blob/read` | leer un blob por su digest |
| `asv://rels/registry/manifest/push` | subir un manifiesto OCI |
| `asv://rels/registry/blob/push` | subir un blob; el CLI calcula el digest |

Las tres de GitHub son el camino fuerte: el token nunca entra en un proceso que
tú controlas. El broker lo presta a una cabecera HTTP durante una petición y lo
devuelve, así que **no** debes sustituirlas por `gh` con `GITHUB_TOKEN` en el shell.

Las cuatro de registry hacen lo mismo, con una diferencia que no lo es. Al
**leer** un blob se verifica el `--digest` que se pasó, y la cabecera
`Docker-Content-Digest` que lo nombra se ignora en vez de creerse. Al **subir** no
se pasa `--digest`: lo calcula el CLI desde los bytes.

`--credential` es un **id del vault**, nunca el token. `asv credentials` imprime
los ids; ése es el valor que se pasa.

El producto declara más relaciones —PostgreSQL, firma SSH, approvals y audit—
pero **no las publica todavía**: aparecen como *withheld*. No las sigas ni las
simules con otro camino.

## Reglas no negociables

1. No pidas, leas, exportes, imprimas ni copies material secreto.
2. No inspecciones el vault, `/proc`, environment, argv ni logs para recuperar credenciales.
3. No inventes un comando ASV cuando exista un `link` anunciado.
4. Ejecuta `invoke.program` + `invoke.argv` como argv estructurado; no lo conviertas en `sh -c`.
5. Valida `schema`. Si no soportas la versión, detente y diagnostica.
6. Una capability disponible no equivale a autorización. El broker decide.
7. `requires_human=true` es un stop: no autoapruebes ni busques bypass.
8. No ejecutes `asv-brokerd` directamente salvo diagnóstico explícito; para producto usa `asv setup/status/doctor` y los links anunciados.
9. Si ASV no anuncia una operación, no la simules con un secreto de otra vía.
10. Reporta hechos observados: versión/schema, status, operación, resultado y bloqueo; nunca atribuyas una verificación que no ejecutaste.

## Flujo mínimo

```text
intención
  ↓
asv agent discover --json
  ↓
validar schema/status
  ↓
seleccionar rel compatible
  ↓
ejecutar invoke estructurado
  ↓
leer nueva respuesta
  ├─ success → cerrar/reportar
  ├─ link seguro → continuar
  ├─ requires_human → detener
  └─ error/unknown → diagnose
```

## Definition of Done

- la operación se realizó mediante una capability anunciada por ASV, o quedó bloqueada/no soportada;
- el agente nunca recibió secret material;
- no se ejecutaron comandos ASV inventados para sortear una relación;
- cualquier human gate quedó en manos humanas;
- el resultado distingue success, blocked, degraded y unsupported.
