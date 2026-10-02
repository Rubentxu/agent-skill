---
name: retrospective-cycle-audit
description: "Investiga un ciclo de desarrollo ya escrito antes de continuar: reconstruye qué se hizo, delimita el radio de impacto, formula hipótesis y las refuta primero, hunt de falsos éxitos y de tests que no pueden fallar, y corrige sólo lo confirmado con test rojo → fix mínimo → verde → commit atómico. Úsala al retomar trabajo de otro agente o tras una pausa, antes de escribir una línea, cuando un gate está verde y nadie sabe si algo se rompió de verdad."
metadata:
  version: "1.0.0"
---

# Auditoría retrospectiva de un ciclo

Investigar el trabajo anterior **no es hacer una review del diff**. Una review busca errores en lo que se ve; una retrospectiva busca lo que el diff **no muestra**: invariantes que nadie comprobó, reglas declaradas que nada ejecuta, y tests verdes que no pueden fallar.

> Esta skill es un router. Carga sólo la referencia del modo actual.

## Modos

| Modo | Cuándo | Referencias |
|---|---|---|
| `reconstruct` | Hay que saber qué se hizo realmente y con qué autoridad | `01-reconstructing-the-cycle.md` |
| `hunt-signals` | Ya sabes el alcance y buscas dónde puede estar roto | `04-signal-catalog.md` |
| `refute` | Tienes una hipótesis de defecto y quieres comprobar si es real | `02-falsification.md` |
| `false-success` | Todo está verde y la pregunta es si el verde significa algo | `03-false-successes.md` |
| `closeout` | Has corregido y hay que dejar trazabilidad y siguiente paso | `05-commit-and-closeout.md` |

## No negociables

1. **Nunca arregles antes de refutar.** Una hipótesis sin refutación intentada no es un hallazgo, es una corazonada. Escribe primero la operación que la tumbaría si fuera falsa.
2. **Un test que no has visto rojo no es evidencia.** Si no pudiste observar el fallo, no sabes si el test discriminaba. Di explícitamente "no pude refutar" cuando sea el caso.
3. **Un test verde en un default que permite todo no prueba nada.** Si la política, el flag o el permiso por defecto concede lo que quieres negar, toda prueba pasa exista o no la puerta. Instala un caso de control que niegue.
4. **Afirmación positiva sobre ausencia de error.** `code != Upstream` dentro de `if let Error` también pasa con un éxito. Prefiere `match` exhaustivo, o un marcador positivo que sólo el camino real produce.
5. **El control y el caso de denegación van juntos, mismo fixture.** Si el caso negativo puede explicarse por un vault cerrado, una sesión ajena o un argumento malformado, no midió la puerta que creías.
6. **Mide antes de atribuir.** Antes de decir que tu cambio rompió una puerta de rendimiento, mide la baseline en el commit anterior y compárala en la misma máquina, en el mismo momento. El historial de este repo ya tiene dos mediciones que no reproducen.
7. **Un comentario puede ser la única garantía de un invariante.** Si el código afirma en prosa que una comprobación ocurre "más abajo", verifícala. UnaGate inexistente descrita con seguridad es el hallazgo más caro que existe, porque un reviewer no tiene nada que revisar.
8. **El mínimo cambio seguro, no el mínimo cambio.** Un arreglo que arregla la mitad es un arreglo que se_docs_como completo.
9. **Nada de push, merge, tag ni publish sin autorización explícita en ese turno.** Autorizar un push anterior no autoriza el siguiente.
10. **Registra la desviación de protocolo, no la omitas.** Si una herramienta te obliga a saltarte un paso, el recibo dice por qué, con la evidencia de la herramienta.

## Flujo por defecto

```text
1. reconstruct   qué se hizo, con qué autoridad, y qué dice el roadmap
2. blast radius  módulos, contratos, estados, dependencias afectadas
3. hunt-signals  duplicidad, fallbacks silenciosos, typos, ramas sin cubrir
4. refute        hipótesis concretas, empezando por la más probable de ser falsa
5. false-success operaciones que devuelven OK sin cumplir su objetivo
6. corrige       sólo lo confirmado: test rojo → fix mínimo → verde → commit atómico
7. closeout      causa raíz, trazabilidad, apartado `siguiente`
```

Los pasos 1-5 no tocan código. El 6 sí, y sólo para lo confirmado.

## Cuándo NO usar esta skill

- El cambio es tuyo y aún no está commiteado: revísalo como revisión, no como retrospectiva.
- Hay un incidente en curso: arrests primero, audita después.
- El trabajo está sin autoridad de estado (sin ciclo, sin pre-flight, sin roadmap): establecer la autoridad es el primer paso, no un audit más.

## Referencias

- [`00-decision-tree.md`](references/00-decision-tree.md) — qué modo elegir
- [`01-reconstructing-the-cycle.md`](references/01-reconstructing-the-cycle.md) — reconstruir sin inventar
- [`02-falsification.md`](references/02-falsification.md) — refutar antes de creer
- [`03-false-successes.md`](references/03-false-successes.md) — falsos éxitos y tests ciegos
- [`04-signal-catalog.md`](references/04-signal-catalog.md) — dónde mirar primero
- [`05-commit-and-closeout.md`](references/05-commit-and-closeout.md) — atomicidad y recibo
- [`worked-example.md`](worked-example.md) — un ciclo real, hallazgo a hallazgo
