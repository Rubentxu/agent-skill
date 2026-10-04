# Diagnostics

Este documento es el destino cuando el runtime no deja continuar. Carga
`06-diagnostics.md` desde el router, no desde un camino de ejecución que
funciona.

## Leer el sobre antes de interpretar nada

```text
schema            asv.agent/v1
product_version   versión del producto instalado
protocol_version  entero del protocolo de enlace
status            ok | blocked | degraded
data              carga útil
error             { code, message }
links             relaciones disponibles ahora
warnings          [{ code, message }]
```

Tres preguntas, en este orden:

1. ¿`schema` es `asv.agent/v1`? Si no, la respuesta no es para ti: para.
2. ¿`status` es `ok`? Si no, `error.code` dice por qué y `links` dice qué
   hacer. No interpretes el resto.
3. ¿`warnings` está vacío? Un warning no bloquea, pero un
   `data.capability_derivation` con valor UNKNOWN significa que la lista de
   capacidades no es una lista real.

## Códigos de `error.code`

| Código | Qué significa | Qué hacer |
|---|---|---|
| `SETUP_REQUIRED` | esta instalación no se ha configurado: no hay layout runtime, ni vault, ni servicio | invoca el `link` `asv://rels/setup` una vez, y reintenta discovery |
| `BROKER_UNAVAILABLE` | el broker no responde: no hay socket, el servicio está caído, o el uid no coincide | `asv://rels/doctor` para el detalle; no reintentes en bucle |
| `CAPABILITIES_UNKNOWN` | la lista de capacidades está vacía porque **no se pudo preguntar al broker**, no porque este build no tenga ninguna | trátalo como "no se sabe", nunca como "no hay" |
| `PROTOCOL_MISMATCH` | el `protocol_version` del runtime no es el que este cliente habla | no lo fuerces ni lo parchees; repórtalo como incompatibilidad |
| `SCHEMA_UNSUPPORTED` | el runtime sirve un `schema` que este cliente no implementa | para; una versión de cliente distinta es la respuesta |

`CAPABILITIES_UNKNOWN` aparece en `warnings`, no en `error`, y esa distinción
importa: un warning no detiene nada, pero un array `data.capabilities` vacío
significa dos cosas distintas según cuál de los dos campos lo produjo.

## Datos que ayudan a decidir

`data.broker` dice si el broker es alcanzable, si su versión es compatible, y
qué endurecimiento e identidad reporta. `data.installation` dice si la
instalación está lista, por qué canal se hizo y quién la actualiza. Un
`data.installation` con `installed_via_source` igual a `no-record` significa que
nadie sabe quién posee esos ficheros: trátalos como tuyos antes de
sobrescribirlos.

## Qué no hacer aquí

No resuelvas un `BROKER_UNAVAILABLE` cambiando socket, uid o destino para
llegar al mismo resultado por otro camino. Eso convierte una incidencia de
configuración en un bypass silencioso de la frontera. No reintentes un
`SETUP_REQUIRED` si el código dice que el servicio ya existe: lee el
`error.message`, que nombra qué falta.

## Evidencia que debes reportar

`schema`, `product_version`, `protocol_version`, `status`, el `error.code` que
leíste, y qué `link` seguiste a continuación. Un diagnóstico sin esos campos no
es un diagnóstico: es una interpretación.
