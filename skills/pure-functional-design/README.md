# pure-functional-design

Router de diseño funcional inspirado estructuralmente en `delivery-first-testing` de Rubentxu/agent-skill. No convierte Rust ni Kotlin en Haskell: aplica semántica pura, ADTs y modelado explícito respetando ownership, JVM, APIs, errores, desempeño y las bibliotecas realmente instaladas.

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
