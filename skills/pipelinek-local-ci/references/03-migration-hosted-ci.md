# Migrar desde GitHub Actions, Jenkins u otro CI

El objetivo no es convertir un archivo de CI en otro. Es trasladar **la política de entrega** a una pipeline local reproducible.

## 1. Inventario del CI existente

Por cada job/stage identifica:

| Elemento | Pregunta |
|---|---|
| Trigger | ¿qué evento lo inicia y sigue siendo necesario localmente? |
| Checkout | ¿PipelineK se ejecutará ya dentro del repo? |
| Toolchain | ¿lo gestiona el proyecto, mise/asdf/SDKMAN, contenedor o runner? |
| Build | ¿qué comando real se ejecuta? |
| Tests | ¿qué suites y filtros? |
| Matrix | ¿qué variaciones son contrato real? |
| Cache | ¿optimización o requisito semántico? |
| Secrets | ¿qué capacidad necesita el paso? |
| Artifacts | ¿qué se produce y quién lo consume? |
| Publish/deploy | ¿es reversible y debe seguir fuera del gate local? |

## 2. Eliminar plumbing del proveedor

Normalmente NO se migra como Step de PipelineK:

- `actions/checkout` cuando el agente ya trabaja sobre el checkout;
- setup actions que sólo esconden un wrapper/version manager existente;
- upload/download de artefactos cuyo consumidor es el propio workflow alojado;
- sintaxis de matrices del proveedor;
- expresiones `${{ ... }}` o Groovy del controller;
- badges y metadatos del proveedor.

Migra la capacidad subyacente, no el wrapper.

## 3. Diseñar la autoridad local

Ejemplo conceptual:

```text
GitHub Actions antiguo:
checkout → setup-java → gradle build → upload artifact

PipelineK local:
Build: ./gradlew build
Verify artifact: test -f ...
```

Si la publicación requiere credenciales o es irreversible, mantenla en un release train/harness explícito. No escondas publicación bajo una condición DSL no certificada.

## 4. Reparto recomendado

```text
developer/coding agent
      ↓
PipelineK local (autoridad CI)
      ↓
artifact/evidence
      ↓
opcional trigger remoto fino
      ↓
release harness / distribution / deploy
```

El trigger remoto puede seguir existiendo para ejecutar PipelineK en otra plataforma, certificar un SHA externo, publicar artefactos o integrar infraestructura ausente localmente. No debe duplicar la selección de tests ni contener una segunda política CI divergente.

## 5. Sustitución segura

No borres workflows existentes hasta demostrar:

1. nuevo `pipeline.kts` valida;
2. escenario verde real;
3. escenario negativo falla correctamente;
4. artefactos/gates necesarios siguen cubiertos;
5. agentes y humanos pueden reproducirlo localmente;
6. cualquier responsabilidad que queda remota está documentada.

Si el usuario pide sustituir GitHub Actions completamente, elimina/desactiva sólo después de esa equivalencia observada.

## 6. Jenkins

Para Jenkins, separa:

- semántica portable: `sh`, stages, retry/timeout, filesystem, artifacts;
- semántica de controller: `node`, remote agents, `build(job)`, Jenkins credentials/plugins.

No finjas paridad donde PipelineK local no posee controller/scheduler. Rediseña el flujo hacia capacidades locales reales y deja lo remoto como integración externa cuando sea necesario.
