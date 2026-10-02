# Caso de estudio:Destination binding

Aplica cuando el sistema **presta un recurso a un destino** y el destino puede venir del solicitante. Es el caso donde esta clase de bug se convierte en exfiltración de credenciales, y donde la forma "obvia" de arreglarlo está incompleta.

## La forma del defecto

```text
Request { session, host, host_addr, port, database, role }
                              └───────┬────────┘
                                      │
                          ¿dónde se comprueba?
```

Tres síntomas que aparecen juntos, y que hay que buscar los tres:

1. **El recurso de política no tiene destino.** `Resource::Database { name, role }` — no hay `host` en él. Una política escrita con cuidado no puede decir "a este servidor", porque no hay dónde decirlo.
2. **El lookup de credencial no tiene destino.** `credential_for(database, role)` — la pareja identifica la credencial, y nada más.
3. **El nombre que se comprueba contra el certificado viene del request.** Con un campo de tipo `Option<String>` en `None` como default, el fallback es el host del solicitante.

Con los tres, un operador que concede `(database, role)` ha concedido **cualquier host**, y el sistema lo documenta como si hubiera concedido un servidor.

## Por qué el allowlist "obvia" no cierra el caso

```rust
// NO cierra el agujero.
fn allowed_hosts(&self) -> &[String] { &["db.internal"] }
// comprueba host == "db.internal" ... y usa host_addr del request
```

El solicitante conserva el nombre declarado y cambia la dirección:

```text
host:       "db.internal"    ← pasa el allowlist
host_addr:  "203.0.113.9"    ← el broker marca aquí
```

La credencial se presta, y el nombre del certificado sale del lado correcto mientras el socket va al lado equivocado. El control pasa todas las pruebas que se le escriban contra él.

**La forma que sí cierra:**

1. La declaración ata el **par completo** `(host canónico, dirección literal)`.
2. La resolución devuelve la **entrada declarada**, no la del request.
3. Todo lo que sigue — nombre del certificado, dirección marcada, SNI — usa **la entrada declarada**.
4. La comparación se hace sobre la forma **canónica** de ambos lados.

El paso 3 es el que la mayoría se salta. Si el resolvedor devuelve la entrada declarada pero el resto del código sigue leyendo `request.host`, el atado no existe.

## Las tres familias de Trucos de grafía

Un allowlist por comparación de cadenas tiene dos fallos opuestos:

**Acepta cosas que no debería** (comparación textual):
- `db.internal@attacker.example` — userinfo
- `db%2einternal` — percent-encoding
- `10.0.0.5` — literal IP donde se espera un nombre
- `evil.db.internal` — sufijo

**Rechaza cosas que debería** (comparación textual estricta):
- `DB.INTERNAL` — mayúsculas
- `db.internal.` — punto final
- espacios circundantes

La solución no es ajustar la comparación: es **canonicalizar ambos lados con la misma función** antes de comparar. Una función de canonicalización de autoridad que rechace userinfo, percent-encoding, literales IP y sufijos, y que normalice mayúsculas y punto final, cierra las dos direcciones a la vez. Si esa función no existe en el proyecto, es el primer trabajo.

## El orden de las comprobaciones

Es un invariante, y suele romperse sin que nadie lo note:

```text
1. propiedad de la sesión   (¿el solicitante posee esto?)
2. sintaxis de la petición  (¿esto es siquiera válido?)
3. configuración declarada  (¿tenemos un destino declarado?)
4. política                 (¿la política lo permite?)
5. coste                    (credencial, socket, red)
```

**Sintaxis antes que configuración.** Una dirección malformada es un hecho sobre la petición, y tiene que seguir siéndolo:

- Si el orden se invierte, un solicitante que manda basura recibe "este broker no tiene destinos declarados" — responde a una pregunta que no ha hecho y **describe la configuración del despliegue** a un par que elige su siguiente movimiento.
- Y desactiva silenciosamente una garantía existente: "una dirección malformada se rechaza como `InvalidRequest` antes de prestar la credencial" deja de ser cierta.

En un proyecto real este bug lo introdujo el propio arreglo de esta clase, y lo cazó un test que ya existía por otra razón. Los invariantes de orden sobreviven a los cambios porque están en tests que otras razones hicieron escribir.

## Fail-closed en el destino

El default de la declaración debe ser **negar todo**:

```text
sin destinos declarados  →  todo PostgresConnect se rechaza
```

Un default de "permito lo que me pidan" con la documentación de "configura esto para endurecerlo" es un default que concede, y un default que concede es un falso control: el operador cree que tiene una palanca que no existe hasta que lee el código.

## La prueba

El observable correcto **no es el código de error**. Es *"¿se pidió la credencial?"*:

- Instrumenta el puerto de secretos con un contador de `lend`.
- El caso denegado afirma `contador == 0`. Eso es "rechazado **antes** de tocar el secreto", que es la garantía.
- El caso permitido, con el **mismo** fixture, afirma `contador == 1`. Sin ese control, un cero en los denegados mide el fixture y no la puerta.

Y el caso que más se olvida, que es la mitad del agujero:

```text
mismo host declarado, dirección distinta  →  prestada: 0
```

Si el test sólo prueba "host no declarado → prestada: 0", pasa con un allowlist a medias, que es la forma más probable del arreglo.
