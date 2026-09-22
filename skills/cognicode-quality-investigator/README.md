# cognicode-quality-investigator

Skill alternativa autocontenida para auditoría reproducible de doce dimensiones. **Backend actual:** `cognicode-mcp` principal; `cognicode` CLI alternativo solo para operaciones comprobadas. **Fuera de alcance:** `explorer-mcp`, `explorer-api` y herramientas exclusivas de Explorer; su adaptación es un evolutivo separado y no bloquea esta skill.

- `SKILL.md`: flujo y guardas; `references/01-capabilities-and-limits.md`: soporte real y límites.
- `references/02-dimension-recipes.md`: las 12 dimensiones sin presuponer herramientas de Explorer.
- `references/03-evidence-and-adjudication.md`: registro, corroboración y hallazgos.
- `references/05-cli-mcp-parity-and-certification.md`: contratos CLI/MCP y puertas de certificación.
- `references/04-cognicode-evolution.md`: etapas futuras, sin dependencias actuales.
- `assets/report-template.md`, `examples/`, `tests/`: salida, ejemplo y evaluaciones.

## Configuración

Conecta el servidor `cognicode-mcp --cwd <ruta-proyecto>` a un cliente MCP compatible y comprueba `initialize`, `tools/list` completo y una llamada real. Para CLI consulta `cognicode --version`, `cognicode --help`, `cognicode graph --help` y `cognicode index --help`: la paridad se demuestra por operación, no por la presencia de un subcomando. Ninguna instalación de CogniCode es automática.

Instalación selectiva desde GitHub, una vez fusionada la PR: `npx skills add Rubentxu/agent-skill --skill cognicode-quality-investigator --agent opencode`.

**Certificación:** el inventario PRF documenta funcionamiento de un `cognicode-mcp` 0.97.3 sobre un entorno y corpus específicos; no hemos ejecutado en esta edición la UAT MCP/CLI de la skill ni probado paridad general. El CI del repositorio de skills valida su estructura, no el comportamiento de CogniCode. No afirmar que la skill ya está certificada por que su PR esté verde.
