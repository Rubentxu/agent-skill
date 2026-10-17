# cognicode-diagrams

Skill para generar diagramas de la **arquitectura realmente implementada**, investigada exclusivamente mediante **CogniCode CLI/MCP**. No modifica CogniCode ni usa lectura directa del repositorio, README/ADR/roadmaps/manifiestos o agentes exploradores como fuentes arquitectónicas.

## Contrato obligatorio

[`SKILL.md`](SKILL.md) y [investigation-contract.md](references/investigation-contract.md) prevalecen sobre guías de formato, agentes externos, plantillas y ejemplos. Al pedir más detalle, el agente efectúa nuevas consultas a CogniCode y solicita los fragmentos necesarios **a través de sus herramientas**. Si CogniCode no está disponible o la evidencia falta, se informa `BLOCKED/PARTIAL/UNKNOWN`: sin alternativas de lectura.

Consulta el [protocolo verificable por pregunta](references/research-protocol.md): prioriza herramientas estructuradas, prueba su funcionamiento por lenguaje y evita `read_file(raw)` y `search_content` como sustitutos.

## Flujo

1. Descubrir exclusivamente la ayuda y los subcomandos disponibles en el CLI realmente instalado, o MCP `initialize` + `tools/list` paginado. No asumir `doctor` ni `capabilities --json`.
2. Resolver workspace externo y formular preguntas arquitectónicas.
3. Consultar sucesivamente símbolos, entradas y relaciones con CogniCode, solicitando fragmentos mediante su interfaz.
4. Registrar cada entidad y relación con consulta/símbolo/referencia/limitación, diferenciando plano estático, runtime y despliegue.
5. El agente interpreta y genera Mermaid C4, Structurizr DSL o LikeC4 con las lentes `ready`; valida y proyecta sin volver al repositorio.

## Workspace externo y proyectores

El usuario proporciona **la raíz exacta** del checkout en `--repo`. `scripts/workspace.py` solo usa esa ruta como identidad, no ejecuta Git ni lee su contenido. Todos los artefactos se almacenan bajo `~/.cognicode-diagrams/workspaces/<nombre>--<hash>/`. Los proyectores Kroki, LikeC4, Structurizr y Markmap consumen solo esos artefactos, jamás montan o inspeccionan el repositorio.

```bash
python3 scripts/workspace.py inspect --repo /ruta/exacta/a/raiz
python3 scripts/workspace.py init --repo /ruta/exacta/a/raiz
python3 scripts/workspace.py init-lens --repo /ruta/exacta/a/raiz --lens c4
```

## Lentes y formatos

La lente `c4` está habilitada; `class`, `use-case` y `vertical-slice` están planificadas, no se simulan. Mermaid, Structurizr y LikeC4 se mantienen como formatos. Markmap forma un atlas del workspace; una vista renderizada no verifica el código.

- [Guía de escaneo y consultas](references/scan.md)
- [Trazabilidad de evidencia](references/evidence.md)
- [Navegación](references/navigation.md)
- [Proyectores](references/projectors.md)
- [Guía de instalación/diagnóstico](references/bootstrap.md)
- [Validación](references/validate.md)

## Investigación y renderización sin lectura del checkout

**Todo código objetivo lo analiza únicamente CogniCode CLI/MCP.** Ni LLM, ni subagentes, ni scripts ni proyectores pueden abrir los ficheros del proyecto, siquiera mediante un wrapper/otro agente/GitHub/shell. Las respuestas estructuradas y código **por símbolo** proceden del runtime real de CogniCode; si carece de soporte o cobertura, `PARTIAL/UNKNOWN`, sin fallback. El checkout se utiliza únicamente como **ruta opaca** para identificar el workspace de diagramas externo.

## Proyección editorial opcional

Además de las vistas técnicas, `scripts/editorial.py` produce una explicación C4 en HTML/SVG autónomo **a partir de claims CogniCode ya seleccionados** en un informe `*.atlas.json` (sin leer o volver a investigar el checkout). Rechaza relaciones `reference_link`, nodos sin queries y diagramas demasiado grandes: 2–9 nodos, 12 aristas máximo. Su HTML es estático y se sirve con CSP sandbox en el visor del atlas.

```bash
python3 scripts/editorial.py --repo /ruta/exacta/a/raiz --view context
```

La presentación ahora participa en el router HATEOAS: `intent=editorial` lleva a `--check`, render, enlace con `--link-atlas`, sincronización y revisión visual. `--pattern topology|dependencies|traceability` elige topología, dependencias **locales** o bloque trazable; `--focus 'App::Api'` marca un símbolo existente. Para `change_impact`, `dependency_structure` y `traceable_decomposition`, el agente descubre **roles** CogniCode, nunca comandos supuestos. [HATEOAS](references/navigation.md#proyección-editorial-autodescubierta-intenteditorial) y [patrones](references/editorial.md#patrones-útiles-incorporados-de-diagram-design).

El aspecto puede personalizarse con `--profile dark` y un JSON cerrado de seis tokens bajo `~/.cognicode-diagrams/profiles/dark.json` (sin tocar el repo y con contraste obligatorio). [Perfiles](references/editorial.md#perfiles-de-colores-sin-dependencias).

Añadir al mismo informe de vista los assets `lenses/c4/renders/context.editorial.svg` y `lenses/c4/renders/context.editorial.html`, y ejecutar `atlas.py sync`. El atlas enlaza HTML y SVG; el SVG sigue siendo la miniatura. No se habilitan por ello lentes `planned`. [Contrato y router semántico](references/editorial.md).

## Pruebas

`python3 -m unittest discover -s skills/cognicode-diagrams/tests -p 'test_*.py' -v`

`tests/skill-evals.md` contiene casos de aceptación obligatorios (más detalle, insuficiencia, conflicto documento/código, ausencia de CogniCode, subagentes, aislamiento de proyectores). Los tests unitarios y mocks no equivalen a una UAT real con CogniCode.

## Atlas de conocimiento incremental

En el curso de la investigación se reutilizan claims y consultas CogniCode, luego se enlaza cada diagrama a sus afirmaciones con `reports/<vista>.atlas.json` y se ejecuta `atlas.py sync`. Markmap ofrece contexto visual navegable sin base de datos ni analizadores nuevos. [Procedimiento](references/knowledge-atlas.md).

## Preflight 2026-10: C4 sin bloqueo por grafo

La skill requiere [preflight por versión, lenguaje, catálogo y proceso MCP](references/session-preflight.md) y registra [evidencia de relaciones por referencias](references/evidence-reference-links.md) sin inventar `relation_id`. La navegación usa primero símbolos/referencias, después grafo en el **mismo proceso** solo si añade valor. Máximo 15 nodos por vista antes de dividir; [guía de kinds de LikeC4](references/formats/likec4-kinds.md). Los nuevos estados solo describen fixtures sintéticos: UAT real de agente+CogniCode sigue `NOT_RUN` hasta ejecutarla.

## Contexto visual tipado

La [política de procedencia](references/visual-evidence.md) separa categorías implementadas e intención, preserva queries/cobertura y permite metadata de LikeC4. El [visor local de Markmap](references/projectors/markmap.md) se gestiona por `projectors.py` con el ciclo `status/start/stop/remove`; no es obligatorio para construir el atlas ni se inicia automáticamente.

## Roadmap: lenguaje ubicuo y Moldable Development

**Disponible:** [Report Thinking MVP](references/report-thinking.md) genera `Term Card` y `Symbol Passport` (JSON para agentes, Markdown para novatos) desde el **mismo** ledger CogniCode, enlazados al atlas tras `atlas.py sync`. El lenguaje ubicuo es contextual, separa candidato y aceptación humana, y nunca reemplaza `symbol_id`. **Disponible M3**: [navegación contextual moldable](references/moldable-navigation.md) con fichas, diagramas C4 y evidencia vinculados por el mismo símbolo; HTML sencillo para humanos y JSON para agentes. [Moldable Knowledge](references/moldable-knowledge.md) mantiene planificados los enlaces inversos desde nodos SVG y el Change Impact Brief; no incorpora GT, lectores del checkout ni analizadores paralelos.
