---
name: pipelinek-local-ci
description: "Adopta PipelineK como CI/CD local agent-first: instala y fija PipelineK con mise/asdf, crea y revisa pipeline.kts reales, migra Jenkins/GitHub Actions/GitLab CI, ejecuta gates locales, diagnostica fallos con eventos tipados, proyecta NDJSON para auto-fix y puede ejecutar operaciones autenticadas mediante Agent Secretless Vault sin entregar secretos al agente. Úsala para bootstrap, scaffold, review, run, migrate, diagnose, observe o secretless."
metadata:
  version: "2.1.0"
---

# PipelineK local CI — agent-first

PipelineK debe convertirse en la **autoridad local ejecutable** de CI del repositorio. No traduzcas YAML/Groovy mecánicamente y no inventes DSL.

> Esta skill es un router. Carga sólo la referencia necesaria para el modo actual.

## Modos

| Modo | Cuándo | Referencias |
|---|---|---|
| `bootstrap` | PipelineK no está instalado, hay conflicto mise/asdf o hay que fijar versión | `04-version-resolution.md` |
| `scaffold` | Crear o ampliar `pipeline.kts` | `00-decision-tree.md`, `01-pipeline-authoring.md`, `06-jenkins-familiar-dsl.md` |
| `review` | Auditar pipeline existente | `01-pipeline-authoring.md`, `06-jenkins-familiar-dsl.md`, `08-review-checklist.md` |
| `run` | Usar PipelineK como gate del trabajo del agente | `02-agentic-loop.md`, `05-events-and-troubleshooting.md` |
| `observe` | Filtrar/proyectar eventos sin perder la evidencia completa | `10-event-filters.md` |
| `secretless` | Pipeline necesita Git/SSH/API/DB autenticado sin entregar credenciales al agente | `07-security.md`, `09-agent-secretless.md`, `10-event-filters.md` |
| `migrate` | Sustituir Jenkins/GitHub Actions/GitLab CI | `03-migration-hosted-ci.md`, `06-jenkins-familiar-dsl.md` |
| `diagnose` | Fallo de DSL, ejecución, toolchain, shim, credencial o evento | `04-version-resolution.md`, `05-events-and-troubleshooting.md`, `10-event-filters.md` |

Si el usuario no nombra modo, infiérelo por intención. Una adopción desde cero normalmente ejecuta `bootstrap → scaffold → run`. Si aparecen credenciales, decide explícitamente entre `withCredentials` y `secretless` según el threat model.

## No negociables

1. **Identidad exacta.** Antes de acreditar CI conoce `command → realpath → pipelinek version`. Si se pidió `V` y runtime reporta otra versión, es `IDENTITY_MISMATCH`.
2. **Cero comandos ficticios.** Nunca generes `project-wrapper`, `run-tests-here` ni placeholders ejecutables. Detecta comandos reales del repo.
3. **Proyecto primero.** Prefiere `./gradlew`, `./mvnw`, scripts de `package.json`, `uv`, `cargo`, `go`, `make` o `just` realmente presentes.
4. **DSL observada.** `pipelinek validate` es obligatorio después de editar DSL. La tabla Jenkins-familiar de esta skill es orientación; la instalación real manda.
5. **Fallos visibles.** No añadas `|| true`, `--quiet`, `/dev/null` ni redirecciones que oculten el comando causal. Si usas `tee`, conserva el exit con `pipefail`.
6. **Estado fuera del repo.** Journal/control-root bajo XDG state salvo política explícita del proyecto.
7. **No duplicar política.** Si PipelineK es autoridad CI, un workflow remoto puede ser trigger/matrix/distribución, pero no una segunda definición divergente de tests/gates.
8. **No rebajar gates para obtener verde.** Clasifica el fallo y corrige causa o contrato.
9. **Credenciales según postura.** Nunca imprimas secretos. `withCredentials` limita/redacta exposición; para non-disclosure frente al agente prefiere signer/proxy/session de ASV. No llames secretless a un env/file que entrega bytes al child.
10. **Eventos como API agentic.** Conserva el NDJSON completo; usa filtros como proyecciones. Exit y `RunFinished.outcome` contradictorios son un defecto, no una invitación a elegir el verde.
11. **Jenkins-familiar ≠ Jenkins mágico.** Mantén nombres/patrones familiares donde tengan semántica real; fail-closed para lo aún no soportado.

## Flujo por defecto

### 1. Inspeccionar

Lee `AGENTS.md`, build manifests, wrappers, lockfiles, scripts, CI existente y `pipeline.kts`. Detecta stack con `00-decision-tree.md`.

### 2. Bootstrap si hace falta

Si PipelineK falta o la resolución es ambigua, usa `04-version-resolution.md`. En modo bootstrap la instalación **sí está dentro de scope**: prefiere pin por proyecto; no cambies globales salvo petición explícita.

### 3. Diseñar o revisar

Construye stages por responsabilidad observable: validate/static → build → unit/contract → integration/UAT → package. Usa templates de `examples/` sólo después de comprobar que sus comandos existen en el repo.

Si un step necesita autenticación, clasifica antes:

```text
raw env/file acceptable? -> PipelineK withCredentials
agent must never receive secret? -> ASV signer/proxy/session
```

### 4. Validar DSL

```bash
pipelinek validate pipeline.kts
```

Una feature Jenkins-familiar que no valida o cuya semántica no está soportada se rediseña; no se simula.

### 5. Ejecutar como gate agentic

Usa `02-agentic-loop.md`: tests afectados primero durante desarrollo; pipeline completa en frontera de integración/release según política del repo.

Para secretos fuertes, ejecuta PipelineK dentro de la sesión ASV cuando esa integración esté disponible:

```bash
asv run -- pipelinek run --workspace . pipeline.kts
```

ASV resuelve autenticación; no cambia los gates/operator approvals del pipeline.

### 6. Proyectar evidencia

Usa `10-event-filters.md` para obtener:

- terminal outcome;
- primer `StepFailed` causal;
- timeline de stages/control-flow;
- lifecycle de credenciales sin valores;
- contradicciones exit/outcome.

Conserva siempre el stream completo.

### 7. Cerrar con evidencia

Reporta: HEAD, path real de PipelineK, versión, pipeline, comando, exit, `RunFinished.outcome`, primer fallo causal, stages realmente ejecutados, postura de credenciales usada y skips/bloqueos.

## Definition of Done

- [ ] No quedan placeholders ejecutables ni comandos inventados.
- [ ] PipelineK resuelto y versión exacta verificada.
- [ ] `pipeline.kts` valida con la instalación seleccionada.
- [ ] Existe al menos un run positivo real.
- [ ] Si se creó/migró pipeline, existe un negativo discriminante que falla donde debe.
- [ ] Los comandos de build/test proceden del proyecto, no de memoria.
- [ ] Los eventos/outcome y exit no se contradicen; si lo hacen, queda reportado.
- [ ] El NDJSON completo se preserva cuando se usan filtros/proyecciones.
- [ ] No se dejó estado operativo dentro del repo sin política explícita.
- [ ] Si hay credenciales, la postura está explícita: strong-secretless, short-lived, isolated o process exposure.
- [ ] Si se sustituyó CI alojado, las responsabilidades remotas restantes están delimitadas.
- [ ] La superficie Jenkins-familiar usada figura como soportada o fue validada explícitamente.
