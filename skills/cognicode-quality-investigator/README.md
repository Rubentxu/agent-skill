# cognicode-quality-investigator

Skill alternativa, autónoma y **orientada a CogniCode MCP**, complementaria a `code-quality-evidence-review`. Usa el grafo y herramientas de código como fuentes de candidatos y mantiene un ledger reproducible de corroboración frente a código, build, tests y CI.

Instalar dentro de `Rubentxu/agent-skill/skills/cognicode-quality-investigator/` (con `SKILL.md` en la raíz de la skill). No necesita otra skill para funcionar ni depende de que CogniCode esté instalado para degradar a un análisis explícitamente limitado. Su ejecución óptima requiere configurar **los servidores MCP realmente instalados**, pero esta carpeta **no instala ni configura CogniCode automáticamente**.

Estado: **propuesta utilizable a nivel de instrucciones y anexo de investigación**. No se ha ejecutado UAT con `cognicode-mcp`, `explorer-mcp` o repositorios objetivo en esta elaboración. El inventario de herramientas procede de lectura del código y recibos del repo público pinneados a un SHA; debe repetirse con los binarios reales antes de emitir auditorías.

Documentos: `SKILL.md` (procedimiento y guardas), `references/01-capabilities-and-limits.md` (herramientas y límites), `references/02-dimension-recipes.md` (12D), `references/03-evidence-and-adjudication.md` (pruebas), `references/04-cognicode-evolution.md` (roadmap hacia el kernel de evidencias), `assets/report-template.md` (formato de resultados), `examples/hexagonal-investigation.md` (ejemplo sintético), `tests/skill-evals.md` (pruebas de comportamiento de la skill).

Para instalarla localmente mediante skills CLI desde un repositorio multi-skill una vez publicada: `npx skills add Rubentxu/agent-skill --skill cognicode-quality-investigator --agent opencode`. La publicación en GitHub se verifica por separado de la indexación en skills.sh.