---
name: mosat-technology-learning
description: "Investiga, aprende y caracteriza una tecnología digital con MOSAT: delimita el objetivo de aprendizaje, organiza fuentes por perspectivas disciplina/proceso/producto, construye fichas trazables, sintetiza modelos conceptuales/estructurales/funcionales/dinámicos y valida vacíos, contradicciones y evidencia antes de concluir. Úsala cuando haya que comprender una tecnología en profundidad para adoptarla, integrarla, compararla o enseñar cómo funciona."
metadata:
  version: "1.0.0"
---

# MOSAT technology learning

Usa MOSAT para **comprender** una tecnología, no para producir un resumen largo. El resultado debe ser un modelo verificable de qué es, cómo se construye/opera, de qué está hecha, cómo se comporta y qué conocimiento sigue faltando.

> Esta skill es un router metodológico. Carga sólo las referencias necesarias para el estado actual de la investigación.

## Modos

| Modo | Señal observable | Referencia |
|---|---|---|
| `scope` | No está claro qué decisión, profundidad o entregable debe soportar el aprendizaje | [`00-process-and-routing.md`](references/00-process-and-routing.md) |
| `collect` | Faltan fuentes primarias o la bibliografía está mezclada sin criterio | [`01-source-strategy.md`](references/01-source-strategy.md) |
| `cards` | Hay material, pero el conocimiento aún vive como notas o resúmenes sin preguntas/evidencia | [`02-mosat-cards.md`](references/02-mosat-cards.md) |
| `model` | Las fichas existen, pero no hay una representación sistémica coherente | [`03-system-models.md`](references/03-system-models.md) |
| `validate` | Hay modelos, pero pueden contener huecos, contradicciones o afirmaciones no sustentadas | [`04-validation-and-gaps.md`](references/04-validation-and-gaps.md) |
| `control` | La investigación se expande sin límite o no converge hacia un producto útil | [`05-learning-project-control.md`](references/05-learning-project-control.md) |
| `provenance` | Hay afirmaciones fuertes sin origen, confianza, alcance o versión verificable | [`06-provenance-and-confidence.md`](references/06-provenance-and-confidence.md) |

Si varias señales aparecen a la vez, empieza por la que invalide más decisiones posteriores: `scope → collect → cards → model → validate`. Repite el ciclo cuando la validación revele vacíos relevantes.

## Núcleo MOSAT

Conserva explícitamente estas ideas del método original:

1. **Tres perspectivas complementarias**: tecnología como `disciplina`, como `proceso` de creación/ingeniería y como `producto` usado por personas.
2. **Propiedades esenciales**: problema, propósito, principios, procesos, prácticas, personal y productos (7P).
3. **Dos clases de artefactos**: fichas textuales para propiedades/aspectos y modelos/diagramas para representar relaciones y comportamiento.
4. **Proceso iterativo**: recopilar → organizar → analizar/seleccionar → leer → elaborar fichas → elaborar modelos → validar → refinar.
5. **Aprender mientras se modela**: no pospongas la síntesis hasta “haber leído todo”. Los modelos deben descubrir qué falta investigar.

## Extensiones agent-first

Estas reglas **no se atribuyen al MOSAT original**; son una adaptación para agentes:

- Cada afirmación relevante mantiene `claim → evidence → source → confidence → scope/version`.
- Los vacíos se clasifican como `unknown`, `assumed`, `contradicted`, `unverified` u `obsolete`.
- Prioriza un vacío por `incertidumbre × impacto × relevancia para la decisión`, no por curiosidad.
- `UNKNOWN` es un resultado válido. No completes huecos con inferencias presentadas como hechos.
- El estado actual del conocimiento debe exponer la siguiente acción válida; evita workflows rígidos cuando la evidencia indique otra ruta.

## No negociables

1. **Fuente primaria primero.** Especificación, documentación oficial, código fuente o publicación original tienen prioridad sobre resúmenes y contenido derivado.
2. **No confundas perspectiva con lista de enlaces.** Cada fuente debe aportar a preguntas concretas de disciplina, proceso o producto.
3. **No modeles sin evidencia.** Un diagrama elegante sin fichas/evidencia detrás es decoración.
4. **No copies taxonomías sin verificar alcance y versión.** Las tecnologías cambian; registra versión/fecha cuando afecte al significado.
5. **No conviertas MOSAT en documentación infinita.** Define antes el nivel de comprensión y la condición de parada.
6. **No mezcles hecho, inferencia y recomendación.** Etiquétalos.
7. **No fuerces UML/BPMN si una notación más simple expresa mejor la relación.** El modelo manda sobre la herramienta.
8. **No investigues todas las perspectivas con la misma profundidad por defecto.** Pondera según el objetivo.

## Flujo por defecto

```text
1. goal/scope      decisión, audiencia, profundidad, restricciones y entregables
2. perspectives   ponderar disciplina / proceso / producto
3. collect         fuentes primarias y secundarias relevantes
4. cards           responder preguntas MOSAT con evidencia y vacíos explícitos
5. models          conceptual + estructural + funcional + dinámico/contextual
6. validate        coherencia, cobertura, contradicciones, actualidad y trazabilidad
7. gaps            priorizar sólo los huecos que cambian comprensión o decisión
8. iterate         investigación dirigida por gaps
9. deliver         modelos + fichas decisivas + incertidumbres + fuentes
```

## Definition of Done

- [ ] El objetivo de aprendizaje y la condición de parada están escritos.
- [ ] Las tres perspectivas fueron consideradas y su profundidad está justificada.
- [ ] Las 7P relevantes tienen respuesta o un vacío explícito.
- [ ] Las afirmaciones decisivas son trazables a evidencia y fuente.
- [ ] Existe al menos un modelo conceptual y los modelos adicionales necesarios para el objetivo.
- [ ] Componentes, capacidades, estados/eventos o procesos críticos no están sólo narrados: aparecen en el modelo correspondiente.
- [ ] Las contradicciones y `UNKNOWN` de alto impacto siguen visibles; no se ocultaron para “cerrar” el informe.
- [ ] La validación produjo una lista priorizada de gaps o confirmó que los gaps restantes no cambian la decisión.
- [ ] El entregable distingue claramente núcleo MOSAT de extensiones agent-first.
