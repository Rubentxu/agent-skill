---
name: pipelinek-local-ci
description: "Adopta PipelineK como CI/CD local agent-first: instala y fija PipelineK con mise/asdf, crea y revisa pipeline.kts reales, migra Jenkins/GitHub Actions/GitLab CI, ejecuta gates locales, diagnostica fallos con eventos tipados y explota la DSL Jenkins-familiar sólo cuando la versión instalada lo demuestra. Úsala para bootstrap, scaffold, review, run, migrate o diagnose de PipelineK."
metadata:
  version: "3.0.0"
---

# PipelineK local CI — agent-first

PipelineK debe convertirse en la **autoridad local ejecutable** de CI del repositorio. Esta skill no traduce YAML/Groovy mecánicamente: descubre el proyecto, materializa una pipeline real, la valida con el binario instalado y usa outcomes/eventos como feedback para el agente.

> Router: carga sólo la referencia necesaria para el modo actual.

## Modos

| Modo | Cuándo | Carga |
|---|---|---|
| `bootstrap` | instalar/fijar PipelineK o resolver mise/asdf/PATH | `04-version-resolution.md`, `09-installation-cookbook.md`; ejecuta `scripts/pipelinek-preflight.sh` |
| `scaffold` | crear/ampliar `pipeline.kts` | `00-decision-tree.md`, `01-pipeline-authoring.md`, `12-agentic-recipes.md`; ejecuta `scripts/discover-ci-context.sh` |
| `review` | auditar pipeline existente | `06-jenkins-familiar-dsl.md`, `08-review-checklist.md` |
| `run` | usar PipelineK como gate del cambio | `02-agentic-loop.md`, `05-events-and-troubleshooting.md`, `11-cli-cookbook.md` |
| `migrate` | sustituir Jenkins/Actions/GitLab CI | `03-migration-hosted-ci.md`, `10-jenkins-migration-cookbook.md` |
| `diagnose` | fallo DSL/runtime/toolchain/shim/plugin | `04-version-resolution.md`, `05-events-and-troubleshooting.md`, `11-cli-cookbook.md` |

Si no se nombra modo, infiérelo. Adopción desde cero: `bootstrap → scaffold → run`.

## No negociables

1. **Identidad exacta.** Antes de acreditar CI conoce `command → realpath → pipelinek version`. Requested/selected/runtime deben coincidir.
2. **Cero comandos ficticios.** Nunca generes `project-wrapper`, `YOUR_COMMAND_HERE` ni scripts/targets inventados.
3. **Proyecto primero.** Usa wrappers, manifests y scripts realmente presentes.
4. **Instalación reproducible.** Para proyecto, pin explícito en `mise.toml` o `.tool-versions`; no `latest` persistente.
5. **Mise y asdf no son la misma implementación.** Mise usa backend GitHub nativo; asdf usa `Rubentxu/asdf-pipelinek`. No hagas `mise → asdf plugin`.
6. **DSL observada.** Toda edición estructural termina en `pipelinek validate`. Una tabla de esta skill nunca tiene más autoridad que el binario.
7. **Jenkins-familiar ≠ paridad supuesta.** Migra por carrier/semántica. Una feature no soportada queda externa o fail-closed; no se simula.
8. **Fallos visibles.** No `|| true`, no quiet/redirección que oculte la causa; con pipes conserva el exit.
9. **Estado fuera del repo.** Journal/control-root bajo XDG state salvo política explícita.
10. **No duplicar política.** Si PipelineK es CI authority, hosted CI queda como trigger/matrix/distribution/deploy, no como segunda definición de gates.
11. **Credenciales como bindings.** Nunca literales/argv/logs; carga `07-security.md` cuando haya secretos.
12. **Fast/slow lane.** Feedback focal durante desarrollo; full pipeline en integración; certificación pesada en harness cuando el proyecto la separa.

## Flujo por defecto

### 1. Preflight + discovery

```bash
bash <skill>/scripts/pipelinek-preflight.sh
bash <skill>/scripts/discover-ci-context.sh
```

Después lee `AGENTS.md`, wrappers, manifests, scripts y CI existente.

### 2. Bootstrap si hace falta

Usa `09-installation-cookbook.md`. Prefiere pin por proyecto y un único resolver activo. Una instalación sólo termina después de `version` + `doctor` por el mismo provider.

### 3. Crear/revisar pipeline

Diseña stages por responsabilidad observable. Usa ejemplos sólo si se cumplen sus precondiciones. Para Jenkins, usa el cookbook y valida cada construct contra la instalación.

### 4. Validar y sondar

```bash
pipelinek validate pipeline.kts
```

Para semántica sensible ejecuta además un positivo real y un negativo discriminante. Compilar no prueba comportamiento.

### 5. Gate agentic

Usa el bucle `affected check → PipelineK gate → outcome/eventos → smallest fix → rerun`. Para comandos exactos carga `11-cli-cookbook.md`.

### 6. Cierre

Reporta HEAD, resolver/path/version, pipeline, comando, exit, `RunFinished.outcome`, primer fallo causal, stages ejecutados/skipped y evidencia.

## Definition of Done

- [ ] No placeholders ejecutables.
- [ ] PipelineK path/version inequívocos.
- [ ] Pin de proyecto reproducible si se hizo bootstrap.
- [ ] `pipeline.kts` valida.
- [ ] Positivo real ejecutado.
- [ ] Negativo discriminante para una pipeline nueva/migrada.
- [ ] Comandos observados en el repo.
- [ ] Exit/outcome coherentes o contradicción registrada.
- [ ] Estado operativo fuera del repo salvo política.
- [ ] Secretos no aparecen en source/log/argv.
- [ ] Responsabilidades remotas restantes delimitadas.
- [ ] Toda feature Jenkins-familiar usada está validada en la versión instalada.
