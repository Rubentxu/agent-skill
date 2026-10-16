# cognicode-diagrams

Skill para generar diagramas de la **arquitectura realmente implementada**, investigada exclusivamente mediante **CogniCode CLI/MCP**. No modifica CogniCode ni usa lectura directa del repositorio, README/ADR/roadmaps/manifiestos o agentes exploradores como fuentes arquitectónicas.

## Contrato obligatorio

[`SKILL.md`](SKILL.md) y [investigation-contract.md](references/investigation-contract.md) prevalecen sobre guías de formato, agentes externos, plantillas y ejemplos. Al pedir más detalle, el agente efectúa nuevas consultas a CogniCode y solicita los fragmentos necesarios **a través de sus herramientas**. Si CogniCode no está disponible o la evidencia falta, se informa `BLOCKED/PARTIAL/UNKNOWN`: sin alternativas de lectura.

Consulta el [protocolo verificable por pregunta](references/research-protocol.md): prioriza herramientas estructuradas, prueba su funcionamiento por lenguaje y evita `read_file(raw)` y `search_content` como sustitutos.

## Flujo

1. Descubrir herramientas y schemas en la versión instalada: `cognicode --help`, `cognicode capabilities --json` si existe, MCP `initialize/tools/list` paginado.
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

## Pruebas

`python3 -m unittest discover -s skills/cognicode-diagrams/tests -p 'test_*.py' -v`

`tests/skill-evals.md` contiene casos de aceptación obligatorios (más detalle, insuficiencia, conflicto documento/código, ausencia de CogniCode, subagentes, aislamiento de proyectores). Los tests unitarios y mocks no equivalen a una UAT real con CogniCode.
