# Delegación por skills realmente disponibles

Leer `skill-registry.json` cuando aparezca una necesidad especializada. El catálogo **no** prueba que otra skill esté instalada: `available_skills` debe venir de la inspección real del agente. Delegar solo si coincide intención + señal. No invocar comandos imaginarios y no transferir credenciales ni artefactos privados a terceros.

- `delivery-first-testing`: aceptación efímera e integración funcional, no suplantar la prueba de instalación del paquete real.
- `pipelinek-local-ci`: respetar la CI local del proyecto, no crear GitHub Actions innecesarias.
- `code-quality-evidence-review`: informe de bugs de publicación con evidencia reproducible.
- `retrospective-cycle-audit`: reconciliar provenance de versiones antiguas, logs y recibos sin declarar PASS.

La skill principal es autónoma; si las otras no existen, continuar con las lentes locales.
