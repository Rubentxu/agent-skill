# Rubentxu / agent-skill

Colección modular de **skills para agentes de IA**, mantenidas por separado e instalables individualmente desde un único repositorio.

> Cada skill es autocontenida: sus instrucciones, referencias, ejemplos, scripts y pruebas viven en `skills/<nombre>/`. Ninguna depende de archivos de otra skill.

## Catálogo

| Skill | Propósito | Estado |
| --- | --- | --- |
| [`code-quality-evidence-review`](skills/code-quality-evidence-review/SKILL.md) | Auditoría transversal de calidad con evidencia verificable, hallazgos reproducibles y herramientas opcionales para 12 dimensiones. | Disponible |
| [`cognicode-diagrams`](skills/cognicode-diagrams/SKILL.md) | Investigación exclusivamente con CogniCode CLI/MCP, C4 y atlas HATEOAS; evolución planificada a informes agent-first, lenguaje ubicuo DDD y vistas moldables para personas y agentes. | Disponible (C4 y editorial); Report Thinking planificado |
| [`delivery-first-testing`](skills/delivery-first-testing/SKILL.md) | Orquestación de testing orientado a valor: UAT efímeros, selección por impacto, promoción selectiva de regresiones y lentes navegables. | Disponible (router) |
| [`pure-functional-design`](skills/pure-functional-design/SKILL.md) | Diseño y refactorización funcional en Rust/Kotlin: descubrimiento del dominio, ADTs, invariantes, separación de efectos, algoritmos y vertical slices mediante lentes bajo demanda. | Disponible (router + lentes Rust/Kotlin) |
| [`distribution-first-release`](skills/distribution-first-release/SKILL.md) | Releases orientadas al consumidor: binarios instalables, higiene Git, source archives, SBOM/checksums, verificación de instalación y lentes HATEOAS-like. | Disponible (router + auditor) |
| [`pipelinek-local-ci`](skills/pipelinek-local-ci/SKILL.md) | Bootstrap con mise/asdf, diseña/revisa/migra `pipeline.kts` y opera PipelineK como CI/CD local agent-first con DSL Jenkins-familiar, eventos y gates. | Disponible |
| [`agent-secretless`](skills/agent-secretless/SKILL.md) | Opera Agent Secretless Vault como control plane de credenciales: descubre capacidades por `asv agent discover --json`, ejecuta trabajo secretless y diagnostica instalación sin exponer secretos. | Disponible |
| [`mosat-technology-learning`](skills/mosat-technology-learning/SKILL.md) | Investigación y aprendizaje tecnológico con MOSAT: perspectivas disciplina/proceso/producto, 7P, fichas trazables, modelos sistémicos, validación y gaps agent-first. | Disponible |
| [`playful-learning-design`](skills/playful-learning-design/SKILL.md) | Diseña experiencias educativas gamificadas con objetivos, errores frecuentes, aprendizaje activo, motivación ética y lentes de autodescubrimiento. | Disponible (router + 8 lentes) |
| [`learning-game-html`](skills/learning-game-html/SKILL.md) | Construye y refina juegos educativos HTML visuales, interactivos, accesibles y offline, con QA de navegador, persistencia y 9 lentes. | Disponible (router + 9 lentes) |
| [`agentchanges-review`](skills/agentchanges-review/SKILL.md) | Revisa diffs entre refs con agentchanges: notas ancladas por hash de contenido, elección de kind/status, previsualización, aplicación y verificación de parches sin perder al revisor de vista. | Disponible |
| [`gate-vocabulary-reachability`](skills/gate-vocabulary-reachability/SKILL.md) | Audita que cada elemento del vocabulario de autorización declarado sea alcanzable desde el código de producción, y que los defaults sean fail-closed: enumera acciones, roles, permisos y códigos, y separa los que se construyen de los que solo existen en el mapa o en tests. | Disponible (auditor) |
| [`retrospective-cycle-audit`](skills/retrospective-cycle-audit/SKILL.md) | Investiga un ciclo ya escrito antes de continuar: reconstruye lo hecho, delimita el radio de impacto, formula hipótesis y las refuta primero, caza falsos éxitos y tests que no pueden fallar, y corrige solo lo confirmado. | Disponible |

Consulta el README de [la skill genérica de calidad](skills/code-quality-evidence-review/README.md) y la [skill CogniCode](skills/cognicode-diagrams/README.md). **La skill antigua `cognicode-quality-investigator` ha sido retirada**; no usar sus instrucciones, rutas ni fallback de lectura directa. Las herramientas de terceros descritas en sus anexos **no se instalan automáticamente**.

## Instalación

```bash
# Consultar skills descubiertas en el repositorio público
npx skills add Rubentxu/agent-skill --list

# Instalar solo la skill de calidad en OpenCode, en el proyecto actual
npx skills add Rubentxu/agent-skill --skill code-quality-evidence-review --agent opencode

# Crear diagramas C4 con CogniCode CLI/MCP (futuras lentes extensibles)
npx skills add Rubentxu/agent-skill --skill cognicode-diagrams --agent opencode

# Orquestar tests rápidos, UAT efímeros y regresiones mínimas
npx skills add Rubentxu/agent-skill --skill delivery-first-testing --agent opencode

# Diseñar y refactorizar Rust/Kotlin con programación funcional pura
npx skills add Rubentxu/agent-skill --skill pure-functional-design --agent opencode

# Auditar/presentar releases sin subir fuentes ni morralla
npx skills add Rubentxu/agent-skill --skill distribution-first-release --agent opencode

# Crear/operar CI local con PipelineK
npx skills add Rubentxu/agent-skill --skill pipelinek-local-ci --agent opencode

# Usar Agent Secretless Vault como control plane de credenciales
npx skills add Rubentxu/agent-skill --skill agent-secretless --agent opencode

# Aprender o caracterizar una tecnología con MOSAT
npx skills add Rubentxu/agent-skill --skill mosat-technology-learning --agent opencode

# Revisar diffs con notas ancladas y parches verificados
npx skills add Rubentxu/agent-skill --skill agentchanges-review --agent opencode

# Diseñar experiencias de aprendizaje gamificadas
npx skills add Rubentxu/agent-skill --skill playful-learning-design --agent opencode

# Construir juegos educativos HTML interactivos, visuales y offline
npx skills add Rubentxu/agent-skill --skill learning-game-html --agent opencode

# Auditar que el vocabulario de autorización sea alcanzable de verdad
npx skills add Rubentxu/agent-skill --skill gate-vocabulary-reachability --agent opencode

# Reconstruir y refutar un ciclo ya escrito antes de continuar
npx skills add Rubentxu/agent-skill --skill retrospective-cycle-audit --agent opencode

# O instalar la skill genérica globalmente en OpenCode
npx skills add Rubentxu/agent-skill --skill code-quality-evidence-review --agent opencode --global
```

La instalación presupone que el repositorio ya se ha publicado en GitHub y que se utiliza una versión compatible del CLI `skills`. Si la forma de instalación del agente cambia, consulta la documentación oficial del agente y de [skills.sh](https://skills.sh/).

## Estructura y convenciones

```text
agent-skill/
├── README.md                         # Catálogo e instalación
├── CONTRIBUTING.md                   # Convenciones y proceso de cambios
├── .github/workflows/validate.yml    # Validación de la colección
├── scripts/validate_skills.py         # Validador de manifiestos y rutas
└── skills/
    ├── code-quality-evidence-review/
        ├── SKILL.md                   # Punto de entrada de la skill
        ├── README.md                  # Manual independiente
        ├── references/                # Playbooks y anexos bajo demanda
        ├── assets/                    # Plantillas
        ├── examples/                  # Ejemplos sintéticos
        ├── scripts/                   # Utilidades opcionales
        └── tests/                     # Pruebas y evaluaciones
    ├── pipelinek-local-ci/
    │   ├── SKILL.md                   # CI local agent-first con PipelineK
    │   ├── README.md
    │   ├── references/                # Bootstrap, decision tree, Jenkins mapping, authoring y diagnóstico
    │   ├── examples/                  # Starters reales Gradle/Maven/Node/Rust/Python/Go/Jenkins-familiar
    │   └── tests/                     # Evaluaciones manuales de activación
    ├── gate-vocabulary-reachability/
    │   ├── SKILL.md                   # Auditoría del vocabulario de autorización
    │   ├── README.md
    │   ├── references/                # Árbol de decisión, extracción, alcance y defaults fail-closed
    │   ├── scripts/                   # Auditor de alcanzabilidad
    │   ├── worked-example.md          # Caso trabajado
    │   └── tests/                     # Pruebas y evaluaciones de activación
    └── retrospective-cycle-audit/
        ├── SKILL.md                   # Auditoría retrospectiva de un ciclo ya escrito
        ├── README.md
        ├── references/                # Reconstrucción, falsación, falsos éxitos y cierre
        ├── worked-example.md          # Caso trabajado
        └── tests/                     # Evaluaciones manuales de activación
```

Una nueva skill se añade exclusivamente como `skills/<slug>/`, con `SKILL.md` y front matter `name` (igual al slug) y `description` no vacíos. No muevas referencias a una carpeta compartida salvo que exista una razón de producto justificada: las skills deben poder distribuirse de forma independiente. Utiliza referencias **relativas al directorio de la propia skill**.

## Publicación

Consulta [PUBLISHING.md](PUBLISHING.md) para publicar actualizaciones en el repositorio público existente. La publicación en skills.sh depende de que la skill sea descubierta por el instalador; no se considera completada por la mera creación del repositorio.

## Verificaciones locales

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m unittest discover -s skills/code-quality-evidence-review/tests -p 'test_*.py'
python3 -m unittest discover -s skills/cognicode-diagrams/tests -p 'test_*.py'
python3 -m unittest discover -s skills/delivery-first-testing/tests -p 'test_*.py'
python3 -m unittest discover -s skills/pure-functional-design/tests -p 'test_*.py'
python3 -m unittest discover -s skills/distribution-first-release/tests -p 'test_*.py'
python3 -m unittest discover -s skills/playful-learning-design/tests -p 'test_*.py'
python3 -m unittest discover -s skills/learning-game-html/tests -p 'test_*.py'
python3 -m unittest discover -s skills/gate-vocabulary-reachability/tests -p 'test_*.py'
```

El workflow de GitHub Actions ejecuta estas comprobaciones para cada PR y push. Los tests de una skill nueva deben registrarse en CI cuando se añada. El validador rechaza además una skill que traiga scripts sin pruebas: una utilidad sin test es una afirmación que nadie comprueba.

## Licencia

Antes de habilitar contribuciones externas o redistribución bajo términos de código abierto, el propietario debe seleccionar y añadir una licencia explícita. La visibilidad pública del repositorio por sí sola no define permisos de reutilización. Las herramientas enlazadas tienen licencias independientes.