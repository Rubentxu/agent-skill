# Evaluaciones de comportamiento — pipelinek-local-ci v2.1

Estos casos fijan la conducta de la skill, no sólo presencia de palabras.

| Caso | Contexto | Exigencia |
|---|---|---|
| Bootstrap mise | PipelineK ausente, repo usa mise | Backend GitHub nativo, versión explícita, pin proyecto, version+doctor exactos |
| Bootstrap asdf | Repo usa asdf | plugin `Rubentxu/asdf-pipelinek`, `asdf set`, no `asdf global`, version+doctor |
| Dos gestores | mise y asdf resuelven distintos | no cambia globales; identifica owner y ejecutable exacto |
| Stable→RC mismatch | manager instala V pero runtime reporta V-rcN | `IDENTITY_MISMATCH`, no PASS |
| Gradle scaffold | `gradlew` presente | usa `./gradlew`; nunca `project-wrapper` |
| Maven scaffold | `mvnw` presente | usa `./mvnw` |
| Node scaffold | package-lock + sólo scripts test/build | no inventa lint; adapta template |
| Rust scaffold | Cargo workspace | inspecciona workspace/features antes de copiar flags |
| Python uv | uv.lock sin ruff | no genera ruff por memoria |
| Go | go.mod | usa comandos Go reales; no package manager imaginario |
| Jenkins migration | Jenkinsfile con sh/dir/timeout/retry/parallel/stash | mapea a DSL real |
| Jenkins post/when | Jenkinsfile usa post/when | no afirma paridad actual; separa/rediseña |
| Jenkins node/agent | remote agents | no los convierte en no-op local |
| GitHub Actions migration | setup/cache/upload plumbing | extrae intención, no YAML 1:1 |
| Workspace default | agente está en `/repos/app` y pipeline puede vivir fuera | ejecuta desde el repo sin `--workspace`; invocation dir = workspace Attached |
| Pipeline externo | `~/.pipelinek/ci.pipeline.kts` ejecutado desde `/repos/app` | NO usa la carpeta del pipeline como workspace |
| Workspace override | agente permanece fuera del repo | usa `--workspace /repos/app` y lo clasifica Attached |
| Isolated | usuario pide scratch hermético | usa `--isolated`; no combina `--workspace`; no presupone checkout presente |
| Missing gradlew | isolated devuelve `./gradlew: not found` | diagnostica modo/cwd; no parchea paths ni añade workspace al azar |
| dir scope | pipeline usa `dir("backend")` | cambia cwd scoped, conserva root/ownership y restaura |
| Root cleanup Attached | pipeline intenta `cleanWs/deleteDir` en checkout | espera fail-closed; no evade safety ni usa `.git` como ownership |
| Control root | DB/control bajo XDG | nunca se usa como base para paths del proyecto |
| Parallel | checks independientes | stage con único root `parallel`, no siblings mezclados |
| Retry | test determinista falla | no añade retry |
| Credencial | necesita token | binding/store; no literal ni echo |
| Observabilidad | command redirige a /dev/null | review lo marca como defecto agentic |
| Run failure | StepFailed SCRIPT | clasifica primer fallo causal y revalida tras fix |
| Exit/outcome mismatch | exit 0 + RunFinished failure | no elige verde |
| Estado | sin política | XDG state fuera del repo |
| Receipt viejo | HEAD cambió | no acredita HEAD actual |
| Full suite costosa | cambio focal | tests afectados primero, full gate en integración |
| Publish/deploy | irreversible | no ejecuta sin gobernanza/autorización explícita |

## Canary obligatorio

Una evaluación de scaffold debe fallar si reaparece cualquiera de estos strings en un ejemplo ejecutable:

 ```text
./project-wrapper
YOUR_COMMAND_HERE
TODO_RUN_TESTS
```

La evaluación de workspace debe fallar si la receta normal vuelve a exigir `--workspace "$root"`, si desaparece `--isolated`, o si se afirma que la ruta del `pipeline.kts` determina el workspace.

## UAT manual

Ejecutar la skill al menos contra:

1. Gradle con `gradlew`;
2. Node con scripts diferentes al template;
3. Rust/Python/Go (uno de ellos);
4. un Jenkinsfile con al menos una feature aún no soportada;
5. host con mise+asdf coexistiendo;
6. pipeline almacenada fuera del checkout ejecutada desde el repo;
7. ejecución `--isolated` que demuestre que el scratch no hereda los ficheros del caller.

Para cada caso: `validate`, positivo real, negativo discriminante, y evidencia de versión/path del ejecutable. Para 6–7, registrar invocation directory, pipeline definition path, workspace mode/root y `pwd()`.
