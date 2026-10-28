# Lente Groma: explorar arquitectura real antes de decidir

**Activar:** al pedir mapa C4/OKF, análisis de componentes, impactos de un cambio, duplicaciones de lógica o arquitectura de un bloque de roadmap.

1. Leer [integración y límites](../groma-integration.md) y verificar `groma --version`, `groma plugin list`. La skill nunca supone que el CLI/scanner está instalado. Verificar además que `groma/` o `.groma/` se mantiene privado si así exige el consumidor.
2. `groma agent-instructions`; después `groma agent-instructions inspect`, `groma view --plain`, `groma view <file>` y drill-down por ID. No escanear ni iniciar servidor para una consulta si hay vista actual disponible.
3. Si el mapa está ausente o obsoleto, proponer `groma scan` con permiso; puede escribir OKF y activar comprobación de updates. Si el escáner no cubre el lenguaje o el archivo, decir COVERAGE_UNKNOWN, no inventar ownership.
4. Un C4 component expresa **responsabilidad**, no un archivo, directorio o capa. Inspeccionar código real y contrastar `groma lint`; solo recomendar refactor si una regla tiene dueño claro y beneficio. Consultar `pure-functional-design` si está anunciada.
5. No confundir plan con hecho: `groma draft` propone estructura futura; el scan no la certifica. Tras cambios estructurales, verificar IDs, flujos y relaciones con Groma y registrar referencias del trabajo en Backlog.md.

**Resultado:** `estado map|coverage|componente/archivo|hecho o hipótesis|riesgo de impacto|siguiente comprobación|IDs conservados`.
