---
name: pipelinek-local-ci
description: "Diseña, crea, migra, valida y opera pipelines PipelineK como CI/CD local para agentes de codificación. Úsala cuando se pida crear o corregir pipeline.kts, sustituir GitHub Actions/Jenkins/GitLab CI por un gate local, ejecutar CI antes de cerrar cambios, interpretar eventos/fallos de PipelineK o integrar PipelineK en un agent harness. Verifica la CLI y la DSL reales instaladas; no inventa Steps ni instala/cambia gestores de versiones por defecto."
---

# PipelineK local CI para agentes

Usa PipelineK como **gate local ejecutable**, no como sustituto textual de YAML/Groovy.

## Flujo

1. **Descubre autoridad y entorno.** Lee instrucciones del repo, build files, wrappers, tests y CI existente. Resuelve el binario real con `command -v pipelinek`, `readlink -f`, `pipelinek version` y `pipelinek doctor`. Si hay mise/asdf/symlinks contradictorios, consulta [resolución de instalación](references/04-version-resolution.md) antes de ejecutar gates. No instales ni cambies la versión activa sin autorización.

2. **Decide si crear, migrar o ejecutar.**
   - Sin `pipeline.kts`: diseña uno desde la intención real del proyecto.
   - Con pipeline existente: preserva su contrato y corrige sólo con evidencia.
   - Migración desde CI alojado: extrae build/tests/gates/artefactos/secretos; no traduzcas sintaxis 1:1. Consulta [migración](references/03-migration-hosted-ci.md).

3. **Diseña el pipeline.** Usa [authoring](references/01-pipeline-authoring.md). Prefiere wrappers del repo (`gradlew`, `mvnw`, package scripts, cargo, etc.), stages con responsabilidad clara y comandos reproducibles. Mantén publicación/despliegue destructivo fuera del pipeline local salvo petición explícita. No inventes DSL: toda construcción nueva debe pasar `pipelinek validate`.

4. **Valida antes de ejecutar.** Ejecuta `pipelinek validate <pipeline>`. Un construct que compila pero no demuestra su semántica no se considera soportado si hay señales contrarias. Simplifica hacia primitives verificadas en vez de fabricar workarounds.

5. **Ejecuta como agente.** Sigue [agentic loop](references/02-agentic-loop.md): paths de estado fuera del repo, `run --workspace`, outcome/exit/eventos, corrección focal y rerun/resume. Durante desarrollo usa el gate proporcional definido por el proyecto; full pipeline en integración/release, no tras cada edición salvo contrato explícito.

6. **Cierra con evidencia.** Registra binario resuelto, versión, pipeline usado, comando, exit, `RunFinished.outcome`, fallo tipado si existe y qué quedó sin ejecutar. Nunca conviertas `SKIPPED`, timeout, warning o un recibo anterior en PASS.

## Límites

- PipelineK es autoridad de CI local cuando el proyecto lo adopta; no borres workflows remotos automáticamente. Pueden quedar como trigger fino, distribución o redundancia.
- No uses GitHub Actions como oráculo si el objetivo del repo es CI local; valida el mismo trabajo mediante PipelineK.
- No escribas journal/control-root/cachés dentro del repo salvo política explícita.
- No leas ni edites SQLite como API estable; usa CLI y eventos observables.
- Para triage de eventos/fallos consulta [troubleshooting](references/05-events-and-troubleshooting.md).
