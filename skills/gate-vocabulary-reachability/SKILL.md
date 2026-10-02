---
name: gate-vocabulary-reachability
description: "Audita que cada elemento del vocabulario declarado por un sistema de autorización sea realmente alcanzable desde el código de producción, y que los defaults sean fail-closed. Enumera acciones, verbos, roles, permisos, destinos y códigos de error declarados; prueba cuáles se construyen en producción y cuáles sólo existen en el mapeo, en las reglas o en tests. Úsala al diseñar o revisar una pasarela de autorización, un motor de políticas, un catálogo de permisos o cualquier sistema donde una regla sobre un valor que nadie construye pretende ser un control."
metadata:
  version: "1.0.0"
---

# Alcanzabilidad del vocabulario de una puerta

> **Una regla sobre un valor que nadie construye no es un control.** Es texto.

Un sistema que declara un vocabulario —acciones, verbos, roles, permisos, destinos, puertos, códigos de error— y un motor que lo evalúa tiene una propiedad que casi nunca se comprueba: **todo elemento del vocabulario debería poder ser producido por el código de producción**. Los que no pueden son decorativos, y son los más peligrosos porque parecen controles: aparecen en la documentación, en la política del operador y en el nombre del permiso que购买 el usuario.

Esta skill produce esa lista, y para cada elemento dead dice **quién debería construirlo y por qué no lo hace**.

## Procedimiento

### 1. Extraer el vocabulario declarado

Localiza la fuente única de verdad: el `enum`, el esquema, el catálogo, el fichero de reglas. No uses los `grep` sueltos como fuente; necesitas **la lista completa**, incluida la variante que nadie usa.

```bash
# el enum que mapea a nombres de motor
grep -n -A80 "fn action_name" src/policy.rs
# las reglas del motor
grep -n "permit\|forbid" src/policy.rs
```

Anota el total. El número importa: "3 de 13 verbos muertos" es un recibo; "hay verbos muertos" no lo es.

### 2. Enumerar los sitios de evaluación

**Este es el paso que encuentra el hallazgo.** Lista cada llamada al motor en código de producción —no en tests— y anota qué valor evalúa cada una.

```bash
grep -rn "\.authorize(\|evaluate(\|check(\|enforce(" src/ --include=*.rs | grep -v "/tests/"
```

Una tabla de dos columnas. En un proyecto real de autorización esta tabla suele tener entre 2 y 6 filas, frente a una lista de declarados que suele pasar de diez.

### 3. La intersección

Un elemento es **vivo** si aparece en la columna de la tabla. Todo lo demás es:

- **mapped-only**: sólo en el `match` que le da nombre. El motor lo soporta; nadie lo pide.
- **rule-only**: sólo en una regla de política. Una regla sobre un verbo que nadie construye no se puede disparar nunca.
- **test-only**: sólo en tests. Cobertura de algo que producción no hace.

Los tres son el mismo defecto con distinta gravedad, y la gravedad la decide el default.

### 4. El default decide la urgencia

Antes de calificar nada, responde: **¿qué pasa por defecto cuando este valor se pide?**

- Si el default **concede**, el elemento no es sólo decorativo: es un **falso control**. El operador cree que puede negar algo que no se puede negar. HIGH.
- Si el default **niega**, el elemento es inerte pero inofensivo. MEDIUM.
- Si el default es fail-closed y el elemento está en un camino que sí se ejecuta, es correcto. NONE.

### 5. Defaults: la segunda auditoría

Un default que concede convierte en vacua **toda** prueba negativa a través de esa puerta. Compruébalo:

- ¿El permiso por defecto concede? ¿La política por defecto permite? ¿El flag por defecto está on?
- Y la pregunta experimental: **borra la implementación y ejecuta la prueba.** Si sigue verde, la prueba no dependía de la puerta.

Un default que concede es un hallazgo por sí mismo, independiente de la puerta.

### 6. El caso del destino

Si el sistema presta un **recurso** a algo, y el *destino* de ese algo viene en el request, entonces el solicitante elige adónde va el recurso. Este caso merece su propia pasada porque la forma habitual de arreglarlo está incompleta.

**Peligro: un allowlist sobre la mitad del par.** Si el par es `(host, address)` y el allowlist comprueba `host`, el solicitante conserva el nombre declarado y cambia la dirección. El control pasa las pruebas y no cierra el agujero.

Regla: **la declaración ata el par completo, y el sistema usa el valor declarado —no el del request— para todo lo que sigue.** Si el nombre que se comprueba contra el certificado viene del request, el atado no existe.

## Reglas de defaults

1. **Fail-closed por omisión.** La ausencia de configuración niega, permite. Nunca al revés: "sin allowlist, permito lo que me pidan" es un default que concede.
2. **El valor declarado gana.** Cuando un request propone algo y una declaración lo autoriza, lo que se usa para el trabajo real es lo declarado.
3. **Sintaxis antes que configuración.** Una petición malformada se rechaza como malformada, sea cual sea la configuración. Al revés responde a una pregunta que no se ha hecho y filtra el estado del despliegue.
4. **La negación es observable antes del coste.** Una destino no declarado debe negarse antes de cualquier evaluación de política, cualquier toma de credencial y cualquier socket. Si el rechazo cuesta trabajo caro, el coste se paga en cada intento.
5. **Un no-op que devuelve éxito no es fail-closed.** Una función que devuelve `Ok` sin hacer nada satisface cualquier contrato que sólo compruebe el retorno. Pruébalo preguntando qué devuelve si todo lo demás falla.

## Qué produce esta skill

Una tabla con una fila por elemento declarado:

| elemento | declarado en | construido en | veredicto | severidad |
|---|---|---|---|---|

Y para cada `mapped-only` o `rule-only`, el sitio donde **debería** construirse. Eso último es la parte accionable: saber que un verbo está muerto no sirve de nada si no dices qué handler debería pedirlo.

## Referencia rápida

- `references/00-decision-tree.md` — cuándo aplicar esta auditoría
- `references/01-extracting-the-vocabulary.md` — extraer sin perder la variante que nadie usa
- `references/02-proving-reachability.md` — la intersección y cómo no engañarse
- `references/03-destination-binding.md` — el caso de las credenciales y los destinos
- `references/04-fail-closed-defaults.md` — cómo se diseña un default que niega
- `scripts/audit_gate_vocabulary.py` — extractor automático paravocabularios de tipo enum
- [`worked-example.md`](worked-example.md) — tres verbos muertos de trece, y el agujero de destino que salió al revisar el release
