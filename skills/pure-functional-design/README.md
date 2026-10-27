# pure-functional-design

Router de diagnóstico y refactorización funcional **por problema arquitectónico** inspirado estructuralmente en `delivery-first-testing` de Rubentxu/agent-skill. No convierte Rust ni Kotlin en Haskell: aplica semántica pura, ADTs y modelado explícito respetando ownership, JVM, APIs, errores, desempeño y las bibliotecas realmente instaladas.

## Activaciones habituales

- "Descubre el dominio y las invariantes de este módulo"
- "Refactoriza este servicio grande por vertical slices, sin añadir features"
- "Modela esta máquina de estados con ADTs Rust"
- "Separa los efectos de este caso de uso Kotlin"
- "¿Es mejor fold, reduce, iterator, recursion, dynamic programming o mutable local?"
- "Revisa duplicidades de reglas y errores semánticos"

## Estructura

- `SKILL.md`: contrato de la skill y router humano/agentic.
- `references/lens-registry.json`: procedimientos disponibles, señales y estado ready/planned.
- `references/lenses/`: playbooks de decisión, no ejecutores ni herramientas mágicas.
- `references/languages/`: traducción idiomática Rust/Kotlin, no duplicados del dominio.
- `scripts/affordances.py`: recomienda acciones en JSON sin efectos externos.
- `tests/`: tests baratos del router y evals adversariales manuales.
- `examples/`: sesiones de entrada y dos implementaciones autocontenidas equivalentes.

## Nuevas capacidades R1–R3

- **Diagnóstico diferencial:** siete problemas tipados, evidencia observada/inferida, alternativas y opción `KEEP_AS_IS`.
- **Refactor incremental:** ocho recetas con precondiciones, bloqueos, riesgo, coste y reversibilidad. Se consideran contratos de IO, datos, concurrencia y migración.
- **Navegación progresiva:** fases `diagnose → plan → verify`, sin leer recetas durante el diagnóstico; no se delega a skills no declaradas en `available_skills`.
- **Abstención explícita:** `APPLY` significa *recomendar* transformación, nunca ejecutarla; `INSPECT_MORE` requiere evidencia adicional; `BLOCKED` limita una receta.

Catálogos: [problemas](references/problems.json), [recetas](references/recipe-registry.json), [navegación](references/navigation.md).

## Uso local

```bash
python3 skills/pure-functional-design/scripts/affordances.py skills/pure-functional-design/examples/refactor-rust.json
python3 -m unittest discover -s skills/pure-functional-design/tests -p 'test_*.py' -v
```

Instalación una vez integrado en el repositorio de skills:

```bash
npx skills add Rubentxu/agent-skill --skill pure-functional-design --agent opencode
```

Este paquete es una **propuesta inicial local**; no está publicado en GitHub ni acreditado en los repositorios de producción. Evaluaciones del agente y compilación de ejemplos se declaran por separado de los tests del selector.

## Convivencia

`delivery-first-testing` sigue siendo dueño de elección de tests, UAT efímero, regresiones, gates y certificación. `cognicode-diagrams` puede ayudar al descubrimiento de símbolos y relaciones cuando está disponible y sus precondiciones se cumplen. Esta skill no introduce su propio sistema de auditoría ni mezcla capacidad de observar con la de cambiar código.

Ejemplos contextualizados: [refactor Rust](examples/refactor-existing-rust.json) y [refactor Kotlin](examples/refactor-existing-kotlin.json).
