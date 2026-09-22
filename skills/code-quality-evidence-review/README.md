# code-quality-evidence-review

Skill reutilizable de auditoría de calidad de código de **cualquier proyecto, lenguaje o arquitectura**, con 12 dimensiones y contrato de hallazgos `Severidad / Ubicación / Evidencia / Impacto / Recomendación`.

Inspirada en el enfoque de instrucciones predecibles y referencias bajo demanda de [writing-great-skills](https://www.skills.sh/mattpocock/skills/writing-great-skills) de Matt Pocock; **no** es copia de su contenido ni redistribuye su skill.

## Qué contiene

- `SKILL.md`: activación, procedimiento y decisiones obligatorias, sin vinculación a repositorios concretos.
- `references/01-evidence-workflow.md`: procedencia, etiqueta y calidad de evidencia; severidad y cierre.
- `references/02-dimensions-playbook.md`: **cómo conseguir y validar información** en las doce dimensiones.
- `references/03-architecture-connascence.md`: técnicas de arquitectura, SOLID, tipos, acoplamiento y connascence.
- `references/04-language-recipes.md`: recetas de Java/Kotlin, Rust, Go, Python, TS/JS, .NET, PHP y C/C++.
- `references/05-tool-catalog.md`: anexo amplio de herramientas, **enlaces a sus proyectos/documentación oficiales**, utilidad, límites y criterios de selección; ninguna es dependencia obligatoria.
- `references/08-installation-managers.md`: **cómo elegir e instalar de manera opcional y reproducible** CLIs y runtimes mediante asdf-vm, mise o Homebrew; comprobaciones de disponibilidad, políticas de autorización, tablas de rutas y alternativas nativas.
- `references/06-test-ci-performance.md`: estrategia por momento/riesgo, CI por SHA, benchmarks y señales de operación.
- `references/07-security-supply-chain.md`: amenazas y SBOM, privacidad y relevancia de CVEs.
- `assets/report-template.md` y `examples/example-audit.md`: formato de informe y ejemplo claramente ficticio.
- `scripts/context_inventory.py`: inventario local opcional, de lectura, sin ejecutar código del repositorio.
- `tests/skill-evals.md` y `tests/test_context_inventory.py`: casos de evaluación del comportamiento de la skill y del script opcional.

## Instalación opcional de herramientas de análisis

La skill por sí misma **no requiere asdf-vm, mise ni Homebrew** y no instala nada. Si falta una CLI concreta, el agente consulta `references/08-installation-managers.md`, examina el entorno y presenta una ruta de instalación **solo para el análisis necesario**. Los SDK, librerías, test runners y plugins pertenecientes a la aplicación se gestionan con sus manifests/lockfiles, no como CLIs globales. Los ejemplos no deben ejecutarse indiscriminadamente.

## Instalación y uso

Coloca **la carpeta completa** `code-quality-evidence-review/` en el directorio de skills que admita tu agente (p. ej. `.opencode/skills/` en versiones compatibles de OpenCode) y conserva la estructura `references/`, `assets/`, `scripts/`. La discovery/invocación varía según host: consulta su documentación actual.

Ejemplo de invocación: «Usa `code-quality-evidence-review` para revisar esta PR. Analiza las dimensiones relacionadas con el diff y los contratos afectados; si faltan evidencias, marca qué no has medido; genera hallazgos con los cinco campos obligatorios y un plan de tests proporcional al riesgo».

Auditoría global: «Aplica las 12 dimensiones a este repositorio. Reutiliza las herramientas y tests ya instalados; para cada afirmación indica ruta, SHA, comando/resultados o documentación, y verifica el CI del SHA exacto si es accesible».

Script local opcional: `python3 scripts/context_inventory.py --repo /ruta/al/repo` (imprime JSON; **no** instala herramientas ni ejecuta scripts del proyecto). La salida es inventario, no una evaluación de calidad.

## Alcance y cautelas

No implica ejecución automática de los scanners enumerados ni verificación de un repositorio particular. Si el proyecto usa capas, reglas o herramientas especiales, el auditor las descubre y aplica solo donde corresponde. El anexo se revisó documentalmente el 22 de septiembre de 2026: comprobar cambios de sintaxis, versiones y licencias en las páginas oficiales antes de integrarlo en CI.
