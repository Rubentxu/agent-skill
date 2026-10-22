# Rubentxu / agent-skill

Colección modular de **skills para agentes de IA**, mantenidas por separado e instalables individualmente desde un único repositorio.

> Cada skill es autocontenida: sus instrucciones, referencias, ejemplos, scripts y pruebas viven en `skills/<nombre>/`. Ninguna depende de archivos de otra skill.

## Catálogo

| Skill | Propósito | Estado |
| --- | --- | --- |
| [`code-quality-evidence-review`](skills/code-quality-evidence-review/SKILL.md) | Auditoría transversal de calidad con evidencia verificable, hallazgos reproducibles y herramientas opcionales para 12 dimensiones. | Disponible |
| [`cognicode-quality-investigator`](skills/cognicode-quality-investigator/SKILL.md) | Adaptación de la skill de calidad: mismas doce dimensiones y evidencias, con CogniCode para descubrir símbolos, relaciones e impacto. | Disponible |
| [`pipelinek-local-ci`](skills/pipelinek-local-ci/SKILL.md) | Bootstrap con mise/asdf, diseña/revisa/migra `pipeline.kts` y opera PipelineK como CI/CD local agent-first con DSL Jenkins-familiar, eventos y gates. | Disponible |
| [`agent-secretless`](skills/agent-secretless/SKILL.md) | Opera Agent Secretless Vault como control plane de credenciales: descubre capacidades por `asv agent discover --json`, ejecuta trabajo secretless y diagnostica instalación sin exponer secretos. | Disponible |
| [`mosat-technology-learning`](skills/mosat-technology-learning/SKILL.md) | Investigación y aprendizaje tecnológico con MOSAT: perspectivas disciplina/proceso/producto, 7P, fichas trazables, modelos sistémicos, validación y gaps agent-first. | Disponible |
| [`agentchanges-review`](skills/agentchanges-review/SKILL.md) | Revisa diffs entre refs con agentchanges: notas ancladas por hash de contenido, elección de kind/status, previsualización, aplicación y verificación de parches sin perder al revisor de vista. | Disponible |
| [`cognicode-diagrams`](skills/cognicode-diagrams/SKILL.md) | Investiga la arquitectura realmente implementada con CogniCode CLI/MCP y produce Mermaid, Structurizr, LikeC4 y atlas en workspace externo, con evidencia estructurada por término y vista. | Disponible |
| [`delivery-first-testing`](skills/delivery-first-testing/SKILL.md) | Enruta la verificación por riesgo: lentes de impacto, UAT efímero, decisión de regresión, triaje de fallos, economía del harness y certificación de release, sin exigir la suite completa en cada iteración. | Disponible |

Consulta los README de [la skill genérica](skills/code-quality-evidence-review/README.md) y [la alternativa CogniCode](skills/cognicode-quality-investigator/README.md) para ver cobertura, usos y precauciones. Las herramientas de terceros descritas en sus anexos **no se instalan automáticamente**.

## Instalación

```bash
# Consultar skills descubiertas en el repositorio público
npx skills add Rubentxu/agent-skill --list

# Instalar solo la skill de calidad en OpenCode, en el proyecto actual
npx skills add Rubentxu/agent-skill --skill code-quality-evidence-review --agent opencode

# Instalar únicamente la alternativa basada en CogniCode
npx skills add Rubentxu/agent-skill --skill cognicode-quality-investigator --agent opencode

# Crear/operar CI local con PipelineK
npx skills add Rubentxu/agent-skill --skill pipelinek-local-ci --agent opencode

# Usar Agent Secretless Vault como control plane de credenciales
npx skills add Rubentxu/agent-skill --skill agent-secretless --agent opencode

# Aprender o caracterizar una tecnología con MOSAT
npx skills add Rubentxu/agent-skill --skill mosat-technology-learning --agent opencode

# Revisar diffs con notas ancladas y parches verificados
npx skills add Rubentxu/agent-skill --skill agentchanges-review --agent opencode

# Investigar la arquitectura implementada y producir diagramas verificables
npx skills add Rubentxu/agent-skill --skill cognicode-diagrams --agent opencode

# Verificar por riesgo: impacto, UAT efímero, regresión y release
npx skills add Rubentxu/agent-skill --skill delivery-first-testing --agent opencode

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
    ├── cognicode-quality-investigator/
    │   ├── SKILL.md                   # Procedimiento CogniCode; independiente
    │   ├── README.md
    │   ├── references/                # Consultas CogniCode y criterios de calidad
    │   ├── assets/                    # Plantilla de informe
    │   ├── examples/                  # Caso sintético
    │   └── tests/                     # Evaluaciones manuales de activación
    ├── pipelinek-local-ci/
    │   ├── SKILL.md                   # CI local agent-first con PipelineK
    │   ├── README.md
    │   ├── references/                # Bootstrap, decision tree, Jenkins mapping, authoring y diagnóstico
    │   ├── examples/                  # Starters reales Gradle/Maven/Node/Rust/Python/Go/Jenkins-familiar
    │   └── tests/                     # Evaluaciones manuales de activación
    ├── cognicode-diagrams/
    │   ├── SKILL.md                   # Diagramas de la arquitectura implementada
    │   ├── README.md
    │   ├── references/                # Contrato de investigación, formatos, lentes y proyectores
    │   ├── assets/                    # Fuentes de ejemplo y plantillas
    │   ├── examples/                  # Sesiones sintéticas
    │   ├── scripts/                   # Proyectores, atlas y utilidades de contexto
    │   └── tests/                     # Pruebas y evaluaciones de activación
    └── delivery-first-testing/
        ├── SKILL.md                   # Router de verificación por riesgo
        ├── README.md
        ├── references/                # Router, catálogo de lentes y playbooks
        ├── examples/                  # Sesiones sintéticas de estado
        ├── scripts/                   # Cálculo de affordances
        └── tests/                     # Pruebas y evaluaciones de activación
```

Una nueva skill se añade exclusivamente como `skills/<slug>/`, con `SKILL.md` y front matter `name` (igual al slug) y `description` no vacíos. No muevas referencias a una carpeta compartida salvo que exista una razón de producto justificada: las skills deben poder distribuirse de forma independiente. Utiliza referencias **relativas al directorio de la propia skill**.

## Publicación

Consulta [PUBLISHING.md](PUBLISHING.md) para publicar actualizaciones en el repositorio público existente. La publicación en skills.sh depende de que la skill sea descubierta por el instalador; no se considera completada por la mera creación del repositorio.

## Verificaciones locales

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -p 'test_*.py'
for dir in skills/*/tests; do
  compgen -G "$dir/test_*.py" > /dev/null || continue
  python3 -m unittest discover -s "$dir" -p 'test_*.py'
done
```

El workflow de GitHub Actions ejecuta estas mismas comprobaciones en cada PR y push. Los tests de una skill nueva quedan registrados en CI sin tocar el workflow: basta con dejarlos en `skills/<slug>/tests/`.

## Licencia

Antes de habilitar contribuciones externas o redistribución bajo términos de código abierto, el propietario debe seleccionar y añadir una licencia explícita. La visibilidad pública del repositorio por sí sola no define permisos de reutilización. Las herramientas enlazadas tienen licencias independientes.