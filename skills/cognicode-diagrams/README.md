# cognicode-diagrams

Skill instalable para investigar repositorios y producir representaciones diagramáticas utilizando **CogniCode CLI/MCP + interpretación de agentes**, sin alterar CogniCode. Orquestación HATEOAS-like (estado observado → enlaces a procedimientos locales) con carga gradual de referencias.

## Qué aporta

- Entrada única: `SKILL.md`.
- Bootstrap de `cogh`/CLI/MCP y verificación real de la instalación, solo si procede y con autorización.
- Escaneo mínimo de símbolos y grafos por alcance, sin imponer indexación completa a cada petición.
- Catálogo de lentes en `references/lens-registry.json`; la única lente actualmente `ready` es **C4**.
- C4 en Mermaid (`C4Context`, `C4Container`, `C4Component`) y Structurizr DSL; interpretación y reconciliación con código.
- Puntos de extensión documentados para `use-case`, `class`, `vertical-slice`, sin duplicar la skill orquestadora ni crear un nuevo servidor.
- Pruebas de selección de acciones y de compatibilidad con salidas.

## Reglas de formatos

**Lente != formato.** Una lente establece qué entidades/relaciones tienen sentido; los renderizadores expresan lo que cada lenguaje admite. Mermaid tiene `classDiagram`, pero Structurizr DSL no equivale a UML class diagrams. Structurizr tiene vistas dinámicas, pero requieren una semántica ordenada; el grafo de llamadas no basta para inferirla. Nunca convertir "aproximadamente" sin declararlo.

## Ejemplos de peticiones

- "Prepara CogniCode localmente y escanea este repositorio para hacer diagramas más tarde".
- "Usa CogniCode MCP para descubrir los límites reales de mi sistema y generar C4 C1/C2/C3 en Mermaid y Structurizr".
- "Interpreta este workspace.dsl y tradúcelo a Mermaid C4, preservando el significado".
- "Revisa el C4 del repositorio contra HEAD y señala relaciones inventadas".
- "Enumera las lentes disponibles y dime cuáles están por implementar".

## Integrar / instalar

La ruta de integración es `skills/cognicode-diagrams/` dentro de `Rubentxu/agent-skill`, sin depender de ninguna otra skill para sus archivos. Tras integrar y publicar en el repositorio externo:

```bash
npx skills add Rubentxu/agent-skill --skill cognicode-diagrams --agent opencode
```

Para OpenCode, el runtime `cognicode-mcp` y sus skills de acompañamiento se instalan con `cogh`; usar la guía oficial en `https://github.com/Rubentxu/CogniCode/blob/main/docs/distribution/INSTALL.md`. Para Claude Code u otros agentes, adaptar la configuración MCP existente sin sobrescribirla y utilizar el catálogo runtime `tools/list`.

## Pruebas locales

```bash
python3 -m unittest discover -s skills/cognicode-diagrams/tests -p 'test_*.py' -v
python3 skills/cognicode-diagrams/scripts/affordances.py skills/cognicode-diagrams/examples/session-c4.json
```

El helper es una **referencia pura opcional**, no una dependencia necesaria para el agente. No ejecuta CogniCode, no escribe archivos y no utiliza red. Las pruebas no sustituyen UAT con agente, CogniCode real y validadores de los diagramas.

## Límites

No se ha incluido un nuevo motor de grafos, ontología persistida genérica, LLM interno, parser de Structurizr, CLI nuevo ni modificaciones del repositorio CogniCode. Los documentos de futuras lentes no equivalen a funcionalidades activas. No se afirma que los UAT de integración con los agentes se hayan ejecutado.
