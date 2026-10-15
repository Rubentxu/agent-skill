# cognicode-diagrams

Skill instalable para investigar repositorios y producir representaciones diagramáticas utilizando **CogniCode CLI/MCP + interpretación de agentes**, sin alterar CogniCode. Orquestación HATEOAS-like (estado observado → enlaces a procedimientos locales) con carga gradual de referencias.

## Qué aporta

- Entrada única: `SKILL.md`.
- Workspace externo obligatorio `~/.cognicode-diagrams/workspaces/<repo-name>--<id>/`, vinculado a cada raíz Git sin contaminar el repositorio; resolver con `scripts/workspace.py`.
- Bootstrap de `cogh`/CLI/MCP y verificación real de la instalación, solo si procede y con autorización.
- Escaneo mínimo de símbolos y grafos por alcance, sin imponer indexación completa a cada petición.
- Catálogo de lentes en `references/lens-registry.json`; la única lente actualmente `ready` es **C4**.
- C4 en Mermaid (`C4Context`, `C4Container`, `C4Component`), Structurizr DSL y LikeC4 `.c4`; el agente produce el protocolo desde las evidencias de CogniCode.
- Puntos de extensión documentados para `use-case`, `class`, `vertical-slice`, sin duplicar la skill orquestadora ni crear un nuevo servidor.
- Tres proyectores locales opcionales: **Kroki** (SVG/PNG), **LikeC4** (visor interactivo `.c4`) y **Structurizr Local** (navegador C1/C2/C3 `.dsl`), sin servicios públicos ni alterar CogniCode. El gestor prioriza Podman y acepta Docker.
- Pruebas de selección de acciones y de compatibilidad con salidas.

## Directorio de proyecto (fuera de Git)

```bash
python3 scripts/workspace.py inspect --repo /ruta/a/pipelinek
python3 scripts/workspace.py init --repo /ruta/a/pipelinek
python3 scripts/workspace.py init-lens --repo /ruta/a/pipelinek --lens c4
python3 scripts/workspace.py path --repo /ruta/a/pipelinek --relative lenses/c4/sources/context.mmd
```

Todos los `.dsl`/`.mmd`/`.c4`, renders SVG/PNG, informes, pruebas y sesiones se guardan en la ruta devuelta. La ruta de CogniCode para consultar sigue siendo la raíz Git. No añadir `.gitignore` ni carpetas dentro del repo. Ver [el contrato del workspace](references/workspace.md).

## Reglas de formatos

**Lente != formato.** Una lente establece qué entidades/relaciones tienen sentido; los renderizadores expresan lo que cada lenguaje admite. Mermaid tiene `classDiagram`, pero Structurizr DSL no equivale a UML class diagrams. Structurizr tiene vistas dinámicas, pero requieren una semántica ordenada; el grafo de llamadas no basta para inferirla. Nunca convertir "aproximadamente" sin declararlo.

## Visualización con Kroki

Para previsualizar Structurizr basta `docker run -d --name kroki -p 127.0.0.1:8000:8000 yuzutech/kroki` (con autorización). Para Mermaid **hace falta además `kroki-mermaid`**; seguir [la guía Kroki](references/kroki.md) o usar [`assets/kroki-compose.yml`](assets/kroki-compose.yml).

Con Kroki ya iniciado, ejecutar desde la carpeta de la skill:

```bash
python3 scripts/render_kroki.py assets/example-workspace.dsl /tmp/c4-context.svg --type structurizr --view-key Context
python3 scripts/render_kroki.py assets/example-c4.mmd /tmp/c4-mermaid.svg --type mermaid
```

Las imágenes son vistas derivadas: no sustituyen al DSL/Mermaid editable ni validan fidelidad al código. Se conserva fuente local y el helper **rechaza destinos remotos y redirecciones**.

## Visualizadores interactivos gestionados con Podman/Docker

Cuando el agente haya generado `workspace.dsl` y `model.c4` **en `lenses/c4/sources/` del workspace externo**, podrá comprobar y arrancar los visores por separado:

```bash
python3 scripts/projectors.py status --repo /ruta/a/repo --projector structurizr --engine podman
python3 scripts/projectors.py start  --repo /ruta/a/repo --projector structurizr --engine podman
# Abrir http://127.0.0.1:8080/

python3 scripts/projectors.py status --repo /ruta/a/repo --projector likec4 --engine podman
python3 scripts/projectors.py start  --repo /ruta/a/repo --projector likec4 --engine podman
# Abrir http://127.0.0.1:5173/
```

`start` es una operación explícita y puede descargar una imagen de contenedor; no se ejecuta durante una simple consulta. Ver [guía de proyectores](references/projectors.md), [LikeC4](references/projectors/likec4.md) y [Structurizr Local](references/projectors/structurizr-local.md). Los visores no analizan repositorios: interpretan exclusivamente los DSL escritos por el agente. `status --check-http` verifica la respuesta web local, pero **no** constituye revisión visual.

## Ejemplos de peticiones

- "Prepara CogniCode localmente y escanea este repositorio para hacer diagramas más tarde".
- "Usa CogniCode MCP para descubrir los límites reales de mi sistema y generar C4 C1/C2/C3 en Mermaid y Structurizr".
- "Interpreta este workspace.dsl y tradúcelo a Mermaid C4, preservando el significado".
- "Revisa el C4 del repositorio contra HEAD y señala relaciones inventadas".
- "Enumera las lentes disponibles y dime cuáles están por implementar".
- "Investiga el código con CogniCode, crea un `.c4` y ábrelo con LikeC4 en Podman".
- "Abre el Structurizr DSL generado en Structurizr Local y revisa los límites C1/C2/C3".
- "Previsualiza en local con Kroki todas las vistas de workspace.dsl y corrige si hay errores de sintaxis, sin tocar CogniCode".

## Integrar / instalar

La ruta de integración es `skills/cognicode-diagrams/` dentro de `Rubentxu/agent-skill`, sin depender de ninguna otra skill para sus archivos. Tras integrar y publicar en el repositorio externo:

```bash
npx skills add Rubentxu/agent-skill --skill cognicode-diagrams --agent opencode
```

Para OpenCode, el runtime `cognicode-mcp` y sus skills de acompañamiento se instalan con `cogh`; usar la guía oficial en `https://github.com/Rubentxu/CogniCode/blob/main/docs/distribution/INSTALL.md`. Para Claude Code u otros agentes, adaptar la configuración MCP existente sin sobrescribirla y utilizar el catálogo runtime `tools/list`.

## Pruebas locales

```bash
python3 -m unittest discover -s skills/cognicode-diagrams/tests -p 'test_*.py' -v
# Incluye pruebas de aislamiento y resolución de workspace bajo HOME
python3 skills/cognicode-diagrams/scripts/affordances.py skills/cognicode-diagrams/examples/session-c4.json
python3 skills/cognicode-diagrams/scripts/affordances.py skills/cognicode-diagrams/examples/session-preview.json
# pruebas mock HTTP de Kroki y de comandos Podman/Docker incluidas en test_*.py
```

El helper es una **referencia pura opcional**, no una dependencia necesaria para el agente. No ejecuta CogniCode, no escribe archivos y no utiliza red. Las pruebas no sustituyen UAT con agente, CogniCode real y validadores de los diagramas.

## Límites

No se ha incluido un nuevo motor de grafos, ontología persistida genérica, LLM interno, parser de Structurizr, CLI nuevo ni modificaciones del repositorio CogniCode. Los documentos de futuras lentes no equivalen a funcionalidades activas. No se afirma que los UAT de integración con los agentes se hayan ejecutado.
