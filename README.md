# Rubentxu / agent-skill

Colección modular de **skills para agentes de IA**, mantenidas por separado e instalables individualmente desde un único repositorio.

> Cada skill es autocontenida: sus instrucciones, referencias, ejemplos, scripts y pruebas viven en `skills/<nombre>/`. Ninguna depende de archivos de otra skill.

## Catálogo

| Skill | Propósito | Estado |
| --- | --- | --- |
| [`code-quality-evidence-review`](skills/code-quality-evidence-review/SKILL.md) | Auditoría transversal de calidad con evidencia verificable, hallazgos reproducibles y herramientas opcionales para 12 dimensiones. | Inicial |

Consulta el [README de la skill](skills/code-quality-evidence-review/README.md) para ver cobertura, usos y precauciones. Las herramientas de terceros descritas en sus anexos **no se instalan automáticamente**.

## Instalación

```bash
# Consultar skills descubiertas en el repositorio público
npx skills add Rubentxu/agent-skill --list

# Instalar solo la skill de calidad en OpenCode, en el proyecto actual
npx skills add Rubentxu/agent-skill --skill code-quality-evidence-review --agent opencode

# O instalarla globalmente en OpenCode
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
    └── code-quality-evidence-review/
        ├── SKILL.md                   # Punto de entrada de la skill
        ├── README.md                  # Manual independiente
        ├── references/                # Playbooks y anexos bajo demanda
        ├── assets/                    # Plantillas
        ├── examples/                  # Ejemplos sintéticos
        ├── scripts/                   # Utilidades opcionales
        └── tests/                     # Pruebas y evaluaciones
```

Una nueva skill se añade exclusivamente como `skills/<slug>/`, con `SKILL.md` y front matter `name` (igual al slug) y `description` no vacíos. No muevas referencias a una carpeta compartida salvo que exista una razón de producto justificada: las skills deben poder distribuirse de forma independiente. Utiliza referencias **relativas al directorio de la propia skill**.

## Publicación

Consulta [PUBLISHING.md](PUBLISHING.md) para publicar actualizaciones en el repositorio público existente. La publicación en skills.sh depende de que la skill sea descubierta por el instalador; no se considera completada por la mera creación del repositorio.

## Verificaciones locales

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m unittest discover -s skills/code-quality-evidence-review/tests -p 'test_*.py'
```

El workflow de GitHub Actions ejecuta estas comprobaciones para cada PR y push. Los tests de una skill nueva deben registrarse en CI cuando se añada.

## Licencia

Antes de habilitar contribuciones externas o redistribución bajo términos de código abierto, el propietario debe seleccionar y añadir una licencia explícita. La visibilidad pública del repositorio por sí sola no define permisos de reutilización. Las herramientas enlazadas tienen licencias independientes.
