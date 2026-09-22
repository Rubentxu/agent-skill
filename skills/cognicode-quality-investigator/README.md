# cognicode-quality-investigator

Adaptación de **code-quality-evidence-review**: mismas doce dimensiones, mismas reglas de evidencia y mismo formato de hallazgos, usando **CogniCode para localizar símbolos, relaciones, consumidores e impacto**.

El archivo `SKILL.md` describe el procedimiento; `references/cognicode-queries.md` contiene las consultas útiles; `references/quality-criteria.md` conserva los criterios completos de la skill original; `references/evidence-checks.md` explica cómo validar un candidato. La plantilla está en `assets/report-template.md`.

Se puede utilizar con `cognicode-mcp` o `cognicode` CLI, según las herramientas que tenga disponibles el agente. No necesita otras capacidades de CogniCode ni obliga a instalarlas. Si una consulta no existe o falla, marcar la limitación y buscar evidencia mediante código, build o pruebas.

Instalación selectiva: `npx skills add Rubentxu/agent-skill --skill cognicode-quality-investigator --agent opencode`.
