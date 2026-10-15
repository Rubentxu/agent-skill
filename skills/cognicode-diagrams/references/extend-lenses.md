# Extender la solución con una nueva lente, sin tocar CogniCode

**No crear una skill instalable nueva por lente.** Los diagramas producidos por esa lente se almacenan en `~/.cognicode-diagrams/workspaces/<repo-name>--<id>/lenses/<id>/` siguiendo el [contrato de workspace](workspace.md); no crear carpetas de nueva lente dentro del repo. Todo vive en `skills/cognicode-diagrams/`; no modificar la lógica del orquestador al añadir una lente.

1. Definir la pregunta que resuelve, entidades y relaciones propias y qué evidencias requiere. Para un flujo ordenado, especificar evidencia temporal; para casos de uso, objetivos del actor; para clases, relaciones de tipos. No asumir que un grafo de llamadas satisface todas las lentes.
2. Crear `references/lenses/<id>.md` con: ámbito, entradas, ruta mínima CLI/MCP con descubrimiento real de herramientas, ontología, incertidumbres, modelos equivocados frecuentes, criterios de evidencia, salidas compatibles y pruebas negativas.
3. Añadir un registro en `references/lens-registry.json` con `id` en kebab-case, `status="ready"` únicamente tras comprobación de los requisitos, `playbook`, `evidence`, y las capacidades `formats`. Usar `native`, `adapted` o `unsupported` por formato; `adapted` requiere advertencia de pérdidas.
4. Añadir una receta especializada de formato si falta, como `references/formats/<formato>-<lente>.md`; la representación nunca debe inventar semántica. Guardar plantillas en `assets/` solo si aportan valor.
5. Añadir casos en `tests/skill-evals.md` y tests del catálogo/hypermedia: descubrimiento, interpretación, generación, validación, faltas de evidencia, formato no compatible, errores y degradación. No activar sin evaluaciones reales con agente.
6. Mantener el único `SKILL.md` breve. Añadir una entrada al catálogo raíz de `Rubentxu/agent-skill` si aún no aparece; no añadir paquetes instalables por separado.

## Matriz inicial

| Lente | Estado | Mermaid | Structurizr DSL |
|---|---|---|---|
| `c4` | `ready` | C4 nativo | C4 nativo |
| `use-case` | `planned` | futuro flowchart **adaptado** | futuro contexto/custom **adaptado**, no UML Use Case |
| `class` | `planned` | futuro `classDiagram` | **unsupported** para UML clases |
| `vertical-slice` | `planned` | futuro flowchart/sequence según evidencia | dynamic **adaptado**, exige orden corroborado |

`planned` significa especificado como hueco para evolución; **no significa listo**. La matriz oficial reside en el JSON, no en esta tabla.

Documentación: https://mermaid.js.org/intro/ y https://docs.structurizr.com/dsl/language.

## Protocolo distinto de proyector

Actualmente la lente C4 admite `mermaid`, `structurizr` y `likec4` (este último `adapted`, requiere [su receta](formats/likec4-c4.md)). Un nuevo proyector debe consumir un formato generado por el agente, declarar precondiciones y acreditar su visualización sin introducir análisis de repositorios o servidores MCP alternativos. Añadir playbook bajo `references/projectors/`, sin instalar una skill extra y manteniendo el gestor de contenedores aislado del Git checkout. El router admite nuevos formatos declarados en el catálogo; para nuevos binarios contenedorizados, ampliar la lista explícita de imágenes/proyectores con pruebas de seguridad.
