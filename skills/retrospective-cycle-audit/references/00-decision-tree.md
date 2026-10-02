# Árbol de decisión

Elige el modo por la **pregunta que te estás haciendo**, no por el fichero que vas a abrir.

```text
¿Existe una autoridad de estado (ciclo, pre-flight, roadmap, ADR)?
├─ no  →，你先 establecerla. Una retrospectiva sin autoridad no sabe qué
│        debía haber pasado. Registra el hueco y para.
└─ sí
   └─ ¿Sabes qué cambió desde el último punto verificable?
      ├─ no  → reconstruct
      └─ sí
         └─ ¿Tienes una hipótesis concreta de defecto?
            ├─ no  → hunt-signals, y de ahí a refute
            └─ sí
               └─ ¿La has refutado al menos una vez?
                  ├─ no  → refute
                  └─ sí
                     └─ ¿Está todo verde y no sabes si el verde significa algo?
                        ├─ sí → false-success
                        └─ no → corrige (test rojo → fix → verde), luego closeout
```

## Atajos que fallan

**"El CI está verde, así que el ciclo anterior está bien."** El CI verde es una afirmación sobre la suite, no sobre el invariante. Hay ciclos enteros que pasan el CI con una puerta que no existe. Ve a `false-success`.

**"Voy a mirar el diff."** El diff muestra lo que se escribió. Los hallazgos caros están en lo que el diff *no* contiene: un verbo de política que nadie evalúa, un destino que el=request elige, un comentario que promete una comprobación que no está. Empieza por `hunt-signals`.

**"El test ya existe, así que está cubierto."** Muéstralo rojo. Si no pudiste, no sabes si discriminaba. Un test que nunca se vio fallar en la dirección que importa es una hipótesis, no una garantía.

**"Es una mejora, no un defecto."** Fixture: la mejora es un defecto con menos impacto. Se corrige igual si es barata, y se registra igual si no lo es.

## Cuándo parar

Detente y reporta si:

- El defecto confirmado requiere una decisión de producto (cambiar qué puede hacer una instalación por defecto).
- La herramienta que debe proporcionar la autoridad del estado está rota, y el arreglo está fuera del repositorio.
- El arreglo mínimo seguro exige tocar un invariante que otro componente depende, y no puedes medir el radio de impacto.

En esos tres casos el recibo dice qué se confirmó, qué falta por decidir y qué evidencia hay. Un hallazgo confirmado y sin corregir, con la causa raíz escrita, vale más que un arreglo a medias.
