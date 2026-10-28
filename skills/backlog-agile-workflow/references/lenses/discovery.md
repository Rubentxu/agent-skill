# Discovery — CLI, proyecto y configuración

1. Verificar `backlog --version`/`backlog --help` solo si CLI disponible. Sin instalación: describir `npm i -g backlog.md` o `npx backlog.md` (solicitar autorización).
2. Localizar el proyecto mediante comando CLI actual, sin suponer `backlog/`; si ausente proponer `backlog init` y revisar banderas `--defaults`, `--backlog-dir`, `--config-location`, `--agent-instructions` o `--no-git` según contexto. No iniciar wizard en sandbox sin TTY.
3. Consultar `backlog instructions overview` **antes de trabajar con tareas**. Inspeccionar configuración avanzada y riesgos de Git (`references/configuration.md`) antes de escrituras.
4. Si existe un `ROADMAP.md` o un `BACKLOG.md` heredado, **no importarlo ni borrarlo automáticamente**: contrastar objetivos actuales, buscar duplicados y proponer migración incremental aprobada.
5. Terminar con `CLI/version | raíz/corpus | git/no-git | estados | efectos colaterales | disponible/bloqueado`; sin inventar resultados.

**Contraejemplo:** ejecutar `backlog init` sobre una carpeta existente por ver un nombre familiar. Eso podría introducir configuración, no es descubrimiento puro.
