# agentchanges-review

Skill de operación para [agentchanges](https://github.com/Rubentxu/agentchanges) (`agc`):
revisión de diffs entre refs de git con notas ancladas al contenido, y aplicación de
parches verificados con el mismo motor que usa la GUI.

## Qué aporta

`agc` resuelve el problema de las notas por número de línea: cuando el código se
mueve, la nota se mueve con él, porque el ancla es el **hash del contenido** que el
revisor vio, no una coordenada. Antes de escribir un parche, el motor comprueba con
`git hash-object` que el código en disco sigue siendo ese — y se niega si no lo es.

Esta skill es el contrato de operación para agentes: qué se espera de cada tipo de
nota, en qué orden se invocan las tools, y qué no se debe hacer nunca.

## Modos

| Modo | Para qué |
|---|---|
| `review` | abrir la revisión, leer el encargo, anotar discrepancias |
| `fix` | previsualizar, aplicar y verificar parches |
| `semantics` | elegir `kind`, `status` y `check` con criterio |
| `setup` | instalar `agc` y registrar el servidor MCP en un cliente |
| `diagnose` | anclas no limpias, parches rechazados, MCP caído |

## Requisitos

El CLI instalado (`npm install -g agentchanges`) y, si usas las tools, el servidor
MCP registrado en tu cliente. `agc mcp --list-tools` debe devolver 11 tools.

## Precauciones

- Las revisiones se guardan en el home del usuario, **nunca dentro del repositorio**.
- Importar un `review.json` ajeno trae checks que son comandos de shell: entran
  suspendidos. No los actives sin leerlos.
- `verified` exige `applied` y un check realmente ejecutado. Un check que pasa sin
  cambios no demuestra nada.
- Un ancla `content-changed` no es reparable con un parche: reancla y reevalúa.

## Instalación

```bash
npx skills add Rubentxu/agent-skill --skill agentchanges-review --agent opencode
npx skills add Rubentxu/agent-skill --skill agentchanges-review --agent opencode --global
```

Consulta el catálogo completo en <https://github.com/Rubentxu/agent-skill>.