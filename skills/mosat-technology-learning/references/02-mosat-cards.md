# Fichas MOSAT

## Función

Una ficha convierte lectura en conocimiento interrogable. No es un resumen de documento: responde una propiedad/aspecto de la tecnología y conserva evidencia suficiente para revisar la respuesta.

## 7P como primera cobertura

Para cada tecnología evalúa, con la profundidad necesaria:

- **Problema**: ¿qué necesidad o limitación resuelve?
- **Propósito**: ¿qué objetivo persigue?
- **Principios**: ¿qué leyes, modelos, estándares o ideas la sustentan?
- **Procesos**: ¿qué ciclo de vida o procesos tecnológicos existen?
- **Prácticas**: ¿qué prácticas regulan o hacen viable esos procesos?
- **Personal**: ¿qué roles/actores intervienen?
- **Productos**: ¿qué artefactos, sistemas o resultados produce?

## Plantilla mínima de ficha

```yaml
id: card-...
perspective: discipline | process | product
property: ...
question: ...
answer: ...
claims:
  - text: ...
    evidence: ...
    source: ...
    scope_or_version: ...
    confidence: high | medium | low
status: known | unknown | assumed | contradicted | unverified | obsolete
open_questions: []
model_implications: []
```

`confidence` y los estados ampliados son extensiones agent-first, no campos originales de MOSAT.

## Preguntas por perspectiva

### Disciplina

- ¿A qué clase de tecnología pertenece?
- ¿Qué la diferencia de alternativas próximas?
- ¿Qué problema y propósito explican su existencia?
- ¿Qué conceptos y relaciones forman su vocabulario esencial?
- ¿Qué principios, estándares o cuerpos de conocimiento la sustentan?
- ¿Cómo ha evolucionado y qué variantes importan hoy?

### Proceso

- ¿Cómo se crea/desarrolla?
- ¿Cómo se instala, opera y utiliza?
- ¿Cómo se mantiene, mejora y desincorpora?
- ¿Qué roles y prácticas intervienen en cada etapa?
- ¿Qué artefactos entran/salen de cada proceso?

### Producto

- ¿Cuáles son sus componentes y fronteras?
- ¿Qué tecnologías base necesita?
- ¿Qué funciones/capacidades ofrece y a qué roles?
- ¿Qué workflows materializan esas capacidades?
- ¿Qué estados y eventos gobiernan su comportamiento?
- ¿Qué atributos de calidad, restricciones y límites tiene?

## Regla de calidad

Una ficha está madura cuando otra persona/agente puede distinguir claramente:

1. qué pregunta se respondió;
2. qué parte es hecho y qué parte es interpretación;
3. de dónde sale la respuesta;
4. bajo qué versión/contexto es válida;
5. qué incertidumbre sigue abierta.
