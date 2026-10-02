# Árbol de decisión

## ¿Debo aplicar esta auditoría?

```text
¿El sistema declara un vocabulario que evalúa un motor?
├─ no  → no aplica. Busca otra clase: quizá destellos de tipos,
│        o validación de entrada.
└─ sí
   └─ ¿Alguien puede escribir una política, regla o config que nombre
      un elemento de ese vocabulario?
      ├─ no  → el vocabulario es interno. Sigue aplicando, pero la
      │        severidad baja: es deuda interna, no falso control.
      └─ sí
         └─ ¿El elemento se puede构建 desde una petición o una config?
            ├─ no  → DECLARADO PERO INALCANZABLE. Sigue la auditoría.
            └─ sí
               └─ ¿Se prestará un recurso a un destino que pueda venir
                  del solicitante?
                  ├─ sí →References/03-destination-binding.md  (trátalo
                  │        primero: es el único caso que puede filtrar
                  │        un secreto)
                  └─ no → references/02-proving-reachability.md
```

## Cuándo es urgente

| Señal | Prioridad |
|---|---|
| El default concede y un operador puede escribir una política que niegue | **Bloquea un release** |
| Un recurso se presta a un destino del solicitante | **Bloquea un release** |
| El punto de evaluación descarta el resultado del motor | **Bloquea un release** |
| El vocabulario muerto tiene default-deny | deuda, se registra |
| El `_ =>` concede en un `match` de seguridad | **Bloquea un release** |
| Una variante existe sólo en el mapeo y en tests | deuda |

## Cuándo NO aplicar

- **Auditoría de un PR pequeño** que no toca el vocabulario ni los defaults. El coste no se paga solo, y la señal se pierde entre ruido. Aplázala a cuando toques el motor.
- **Un sistema sin motor**: un validador de esquemas, un parser. El mismo razonamiento aplica (todo lo declarado debería ser construible) pero la severidad es otra, y el vocabulario no lo escribe un usuario.
- **Como sustituto de una threat model.** Esta skill encuentra lo que el código contradice; no encuentra lo que nadie pensó. Son auditorías distintas y las dos hacen falta.

## El error de método que hay que evitar

**Empezar por el `grep` de usos.** Si la lista de "elementos vivos" sale de buscar dónde se usa cada elemento, los muertos no aparecen en la lista y la auditoría no encuentra nada.

Empieza siempre por la **declaración** (el `enum`, el esquema, el catálogo), haz el inventario completo, y sólo después busca usos. Un elemento que no aparece en la tabla de construcción es un **candidato**, y candidatos hay que refutarlos uno a uno antes de llamarlos hallazgo.

## Cuando termines

Entrega una tabla, no un adjectivo. Y para cada elemento muerto, tres cosas:

1. **Dónde se declara** — el fichero y la línea.
2. **Dónde debería construirse** — el handler o el punto de evaluación que falta.
3. **Qué podría hacer un atacante hoy** — la frase que separa la deuda del falso control.

Si no puedes escribir la tercera, todavía no has terminado la auditoría.
