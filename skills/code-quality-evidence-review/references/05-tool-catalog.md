# ANEXO — Herramientas para reunir evidencia de calidad (catálogo opcional)

**Última revisión documental:** 2026-09-22. Enlaces a proyectos o documentación oficial de referencia. La lista es **amplia, no exhaustiva**: el ecosistema cambia, la edición/licencia puede variar y no todas las herramientas abarcan todos los lenguajes. Antes de instalar o ejecutar: comprobar compatibilidad con toolchain, licencia, privacidad, configuración, artefactos a exportar y aprobación del usuario. La skill es independiente de cualquier SaaS, runner, servidor o analizador.

**Selector mínimo:** (1) ¿cuál es la hipótesis? (2) ¿qué lenguaje/artefacto? (3) ¿sirve la herramienta ya instalada? (4) ¿acepta el entorno sus costes/privacidad? (5) ¿emite evidencia reproducible local? (6) ¿qué no puede demostrar? Prefiere una herramienta por *pregunta*; evita instalar diez scanners con alertas solapadas. Las herramientas con resultados potencialmente sensibles requieren redacción de hallazgos antes de compartir.

## A. Arquitectura, límites, grafo y búsqueda semántica

| Herramienta · fuente oficial | Aplicación concreta | Límites y precauciones |
|---|---|---|
| [ArchUnit](https://www.archunit.org/) | Tests ejecutables de capas, dependencias y ciclos JVM/Java (puede analizar bytecode Kotlin compilado). | Necesita compilar; prueba las reglas y paquetes configurados, no DI/runtime por completo. |
| [Konsist](https://github.com/LemonAppDev/konsist) | Kotlin: comprobaciones de estructura y arquitectura a partir del código fuente. | Su alcance es el código que recibe y las reglas programadas; validar capacidad por versión. |
| [dependency-cruiser](https://github.com/sverweij/dependency-cruiser) | JS/TS: grafo, ciclos y reglas de importación prohibida. | Resolución de alias/import dinámico depende de configuración; distinguir fuente vs bundle. |
| [Deptrac](https://deptrac.github.io/deptrac/) | PHP: capas y violaciones de dependencia arquitectónica. | El mapa de capas es una decisión del proyecto, no se autodetecta la arquitectura correcta. |
| [ArchUnitNET](https://github.com/TNG/ArchUnitNET) | .NET: tests de arquitectura entre assemblies/capas. | Inspección de ensamblados y reglas declaradas; verificar APIs disponibles. |
| [cargo-modules](https://docs.rs/crate/cargo-modules/latest) | Rust: dependencias internas de módulos, estructura y ciclos. | Árbol del módulo ≠ dependencias externas; complementar con Cargo metadata/tree. |
| [Cargo tree](https://doc.rust-lang.org/cargo/commands/cargo-tree.html) | Rust: árbol de crates y features/dependencias resueltas. | No descubre por sí mismo coupling entre símbolos del mismo crate. |
| [Gradle dependency reports](https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html) | JVM/otros Gradle: declaraciones, resolución y causa de una transitiva. | Configuration y variant importan; una arista de build no prueba uso en producción. |
| [Maven Dependency Plugin](https://maven.apache.org/plugins/maven-dependency-plugin/tree-mojo.html) | JVM/Maven: árbol de dependencias resueltas. | Profiles, scopes y multi-módulo requieren precisión. |
| [Madge](https://github.com/pahen/madge) | JS/TS: exploración gráfica y ciclos. | Verificar alias/dynamic imports; si ya existe dependency-cruiser, evitar redundancia. |
| [ts-morph](https://ts-morph.com/) | TS: consultas programáticas al AST/typechecker. | Crear reglas requiere implementar hipótesis; el AST no da automáticamente normas de diseño. |
| [ast-grep](https://ast-grep.github.io/) | Reglas de AST multilenguaje para patrones propios. | Hallazgo sintáctico requiere contexto/triage; cobertura depende de lenguaje y patrón. |
| [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) | Parser incremental para inventarios, queries y navegación multilenguaje. | Requiere construir el análisis; sintaxis por sí sola no prueba semántica de compilador. |
| [CodeQL](https://codeql.github.com/docs/) | Consultas semánticas/dataflow y reglas de acoplamiento o seguridad en lenguajes soportados. | Compatibilidad, coste de crear DB y **condiciones de licencia** según uso/repo; no presume soporte PHP/Scala. |
| [Graphviz](https://graphviz.org/) | Visualización de aristas y SCC ya recogidos. | Diagrama ≠ evidencia adicional; conservar grafo fuente y significado de flechas. |
| [Semgrep](https://semgrep.dev/docs/) | Reglas personalizadas de imports, APIs, patterns y seguridad. | Ediciones tienen distinta profundidad de análisis; no concluir ausencia por scan sin alertas. |

## B. Diseño, acoplamiento, duplicidad, complejidad y deuda

| Herramienta · fuente oficial | Aplicación concreta | Límites y precauciones |
|---|---|---|
| [jscpd](https://jscpd.dev/) | Detección de clones y duplicación de bloques multilenguaje. | Clon textual no demuestra responsabilidades duplicadas; excluir generated/fixtures pertinentes. |
| [Lizard](https://github.com/terryyin/lizard) | Complejidad ciclomática, longitud y funciones multilenguaje. | Umbrales son señales, no prueba de defecto; configuración y dialecto importan. |
| [Radon](https://radon.readthedocs.io/) | Python: complejidad ciclomática, Halstead y Maintainability Index. | Fórmulas no equivalen a riesgo funcional; comparar mismo universo y versión. |
| [detekt](https://detekt.dev/) | Kotlin: smells, complejidad y reglas customizables. | Un “smell” es candidato; baseline y supresiones pueden esconder deuda. |
| [PMD](https://pmd.github.io/) | Java y otros lenguajes soportados: estática, reglas y duplicación CPD. | Confirmar versión, lenguajes y dialectos; falsos positivos contextuales. |
| [ESLint](https://eslint.org/) | JS/TS mediante parser/plugins: reglas de diseño y patrones defectuosos. | Reglas específicas requieren plugin/typed lint; no detecta toda duplicación semántica. |
| [Ruff](https://docs.astral.sh/ruff/) | Python: linter y chequeos consistentes de reglas seleccionadas. | No sustituye tests de comportamiento ni typecheck formal. |
| [Clippy](https://doc.rust-lang.org/clippy/) | Rust: lints y patrones idiomáticos. | No convierte un resultado de `cargo clippy` en evaluación arquitectónica completa. |
| [golangci-lint](https://golangci-lint.run/) | Go: orquestación de linters configurados. | Reportar herramientas/linters activos y tiempo; no equivaler warnings con bugs. |
| [NDepend](https://www.ndepend.com/) | .NET: métricas/grafos, acoplamiento y reglas de dependencia. | Comercial: comprobar licencia; no requisito de la skill. |
| [Git](https://git-scm.com/docs) | `blame`, historial de co-cambios, regresión vs legado y evolución. | Co-cambio ≠ dependencia causal; un autor o un commit no demuestra responsabilidad. |

**Connascence:** no se avala ninguna herramienta “SCIJ Kotlin” como estándar. Construye candidatos con consultas AST/CodeQL/Semgrep, inspecciona pares A/B y registra distancia + obligación de cambio. Solo cuantifica con definición reproducible y herramienta validada para ese lenguaje; las variantes dinámicas requieren trazas/experimentos, no solo AST.

## C. Pruebas, cobertura, contratos y mutación

| Herramienta · fuente oficial | Aplicación concreta | Límites y precauciones |
|---|---|---|
| [JUnit](https://junit.org/junit5/docs/current/user-guide/) / [pytest](https://docs.pytest.org/) / [Vitest](https://vitest.dev/) | Suites unitarias/contratos, selección focal según código afectado. | La existencia del test y su número no acreditan cobertura funcional ni ejecución en HEAD. |
| [cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html) / [Go test](https://pkg.go.dev/cmd/go#hdr-Test_packages) / [dotnet test](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test) | Runners de los ecosistemas y selección por paquete/caso. | Comandos ejecutan proyecto; confirmar permisos, efectos de tests y toolchain. |
| [JaCoCo](https://www.jacoco.org/jacoco/) / [Kover](https://kotlin.github.io/kotlinx-kover/) | Cobertura JVM/Kotlin según integración y módulos. | Líneas/ramas ≠ calidad de aserciones; generators/inlining complican correlación. |
| [coverage.py](https://coverage.readthedocs.io/) | Cobertura de líneas y branches Python. | Registrar omit/include y test command; no inferir runtime completo. |
| [Istanbul/nyc](https://github.com/istanbuljs/nyc) / [c8](https://github.com/bcoe/c8) | Cobertura JS/TS según runtime/transpilación. | Sourcemaps/coverage provider importan; no sumar universos distintos. |
| [cargo-llvm-cov](https://github.com/taiki-e/cargo-llvm-cov) | Cobertura Rust basada en LLVM. | Instrumentación y features afectan el universo y coste. |
| [PIT](https://pitest.org/) | JVM: mutation testing de calidad de assertions. | Puede ser costoso; se limita a mutadores y tests seleccionados. |
| [StrykerJS](https://stryker-mutator.io/) | JS/TS: tests de mutación. | Focalizar rutas y revisar mutantes equivalentes; coste considerable. |
| [cargo-mutants](https://github.com/sourcefrog/cargo-mutants) | Rust: mutation testing. | No ejecutar en CI rápido sin presupuesto/selección; mutantes equivalentes. |
| [Hypothesis](https://hypothesis.readthedocs.io/) / [jqwik](https://jqwik.net/) / [proptest](https://github.com/proptest-rs/proptest) / [fast-check](https://fast-check.dev/) | Property-based testing según lenguaje. | Generadores necesitan invariantes correctas y reproducibilidad de seed. |
| [Pact](https://docs.pact.io/) | Contratos consumidor/proveedor de APIs y mensajes. | Contrato define expectativas; no reemplaza integración de despliegue o compatibilidad semántica no representada. |
| [Testcontainers](https://testcontainers.com/) | Tests de integración con servicios reales controlados. | Puede levantar Docker, descargar imágenes y consumir recursos; requiere permiso. |
| [Playwright](https://playwright.dev/) | E2E UI y flujos reproducibles. | Fragilidad de selectores y coste; no sustituye tests de dominio ni autorización profunda. |
| [libFuzzer](https://llvm.org/docs/LibFuzzer.html) / [cargo-fuzz](https://rust-fuzz.github.io/book/cargo-fuzz.html) | Fuzzing de parsers/límites y entradas arbitrarias. | Permisos/sandbox/time budget y harness necesario; crash requiere triage. |

## D. CI/CD, seguridad de código y secretos

| Herramienta · fuente oficial | Aplicación concreta | Límites y precauciones |
|---|---|---|
| [GitHub CLI](https://cli.github.com/manual/gh_run_view) | `gh run view <id> --json headSha,status,conclusion,jobs` donde API/versión lo permita; extraer runs por SHA. | Autenticación; no usar badge histórico; contrastar jobs/matriz y artefactos. |
| [GitLab CI](https://docs.gitlab.com/ci/) / [Jenkins API](https://www.jenkins.io/doc/book/using/remote-access-api/) / [Azure Pipelines](https://learn.microsoft.com/en-us/azure/devops/pipelines/) | Leer configuración y ejecución concreta en plataforma real. | Confirmar commit del run, reintentos, reglas `allow_failure`, saltos, permisos. |
| [actionlint](https://github.com/rhysd/actionlint) | Validación estática de workflows GitHub Actions. | Workflow sintácticamente válido ≠ jobs ejecutados ni CI verde. |
| [OpenSSF Scorecard](https://scorecard.dev/) | Señales de prácticas de seguridad del repositorio. | Señales indicativas; no usar score como verdict de seguridad/código. |
| [Semgrep](https://semgrep.dev/docs/) / [CodeQL](https://codeql.github.com/docs/) | SAST y reglas propias ligadas a sinks/rutas de riesgo. | Triar falsos positivos, cobertura y límites de edición/licencia; un scan limpio no prueba seguridad. |
| [Gitleaks](https://github.com/gitleaks/gitleaks) | Detección de posibles secretos en fuente e historial. | Proteger el output: no publicar tokens en reportes; revisar falsos positivos y revocación. |
| [Trivy](https://trivy.dev/docs/latest/) | Vulnerabilidades en dependencias/imagen, IaC y secretos según target/opciones. | Scan de repo, imagen y SBOM cubren universos distintos; base de datos/fecha importan. |
| [Checkov](https://www.checkov.io/) | Misconfiguración de Terraform, Kubernetes y otra IaC. | Política por entorno y excepciones; no sustituye runtime security. |
| [OWASP ZAP](https://www.zaproxy.org/docs/) | DAST de endpoints web autorizados y staging controlado. | Puede generar tráfico y modificar estado: consentimiento, ámbito y límites; no es un linter inocuo. |

## E. Dependencias, SBOM, vulnerabilidades y licencias

| Herramienta · fuente oficial | Aplicación concreta | Límites y precauciones |
|---|---|---|
| [Syft](https://github.com/anchore/syft) | Crear SBOM de filesystem/imagen (SPDX, CycloneDX). | Comparar artefacto final vs manifest; distinguir paquetes detectados y usados. |
| [OSV-Scanner](https://google.github.io/osv-scanner/usage/) | Comparar paquetes/locks/imágenes contra avisos de seguridad. | Versión V2 cambia sintaxis frente a V1; requiere datos de vulnerabilidades y triage de aplicabilidad. |
| [Grype](https://github.com/anchore/grype) | CVEs de imagen/SBOM. | Identidad/versiones/distribución del paquete condicionan resultado. |
| [cargo-audit](https://github.com/rustsec/rustsec/tree/main/cargo-audit) | Advisories en dependencias de Cargo. | Revisar árbol resuelto, features y rutas reales afectadas. |
| [govulncheck](https://go.dev/doc/tutorial/govulncheck) | Go: vulnerabilidades según módulos y llamadas cuando el análisis lo permite. | No afirma ausencia de todas las clases de vulnerabilidad. |
| [pip-audit](https://pypi.org/project/pip-audit/) | PyPI: vulnerabilidades conocidas en entorno/requirements. | Asegurar intérprete/entorno y versiones realmente desplegadas. |
| [npm audit](https://docs.npmjs.com/cli/commands/npm-audit) | npm: avisos en árbol npm. | No recomendar `--force` automático; verificar runtime, severidad y explotación. |
| [OSS Review Toolkit](https://oss-review-toolkit.org/) | Inventario, licencia/compliance, política y SBOM multilenguaje. | Análisis de licencias no sustituye criterio jurídico; puede tener setup/descargas costosos. |
| [ScanCode Toolkit](https://scancode-toolkit.readthedocs.io/) | Identificación de licencias/copyright en archivos y dependencias. | Evidencia documental; clasificación de obligaciones depende del uso/distribución. |
| [SPDX](https://spdx.dev/) / [CycloneDX](https://cyclonedx.org/) | Formatos SBOM interoperables. | Formato no implica inventario completo ni certificar ausencia de CVEs. |

## F. Rendimiento, memoria, observabilidad y documentación

| Herramienta · fuente oficial | Aplicación concreta | Límites y precauciones |
|---|---|---|
| [hyperfine](https://github.com/sharkdp/hyperfine) | Benchmark repetido de comandos/CLI con warm-up. | Aislar máquina y controlar caché/I/O; resultados no extrapolan a carga real. |
| [JMH](https://openjdk.org/projects/code-tools/jmh/) | JVM: microbenchmarks con control de warmup/JIT. | El microbenchmark no prueba latencia end-to-end. |
| [Criterion.rs](https://bheisler.github.io/criterion.rs/book/) | Rust: benchmarks estadísticos de funciones. | Versión, entorno, regresión mínima y representatividad del dato importan. |
| [pytest-benchmark](https://pytest-benchmark.readthedocs.io/) | Python: benchmarking de funciones/test cases. | Comparar intérprete, dependencias y hardware equivalentes. |
| [Grafana k6](https://grafana.com/docs/k6/latest/) | Carga de APIs con thresholds y percentiles. | Solo sistemas autorizados; generar carga no es revisión estática, puede afectar servicio. |
| [Linux perf](https://perf.wiki.kernel.org/) / [async-profiler](https://github.com/async-profiler/async-profiler) | Profiling CPU/allocations según runtime/OS. | Permisos kernel/overhead y condiciones de prueba; perf no disponible en todos los SO. |
| [OpenTelemetry](https://opentelemetry.io/docs/) | Instrumentar y exportar trazas, métricas y logs sin atarse a vendor. | No es requisito universal; revisar cardinalidad, privacidad y coste de instrumentación. |
| [Prometheus](https://prometheus.io/docs/) / [Jaeger](https://www.jaegertracing.io/docs/) / [Grafana](https://grafana.com/docs/) | Captura/consulta/visualización de métricas y trazas. | UI vacía no demuestra ausencia de eventos; revisar exportación, sampling y retención. |
| [lychee](https://github.com/lycheeverse/lychee) | Chequeo de links rotos en documentos y repos. | Red, rate limits y enlaces internos privados provocan falsos positivos. |
| [markdownlint](https://github.com/DavidAnson/markdownlint) / [Vale](https://vale.sh/) | Consistencia de Markdown y estilo documental. | Formato limpio no significa ADR o comandos actualizados. |

## Instalación de las herramientas del catálogo

Para cada CLI o plugin seleccionado, consulta [`08-installation-managers.md`](08-installation-managers.md): compara disponibilidad en **asdf-vm**, **mise** y **Homebrew**, diferencia runtime de CLI/librería/servicio, verifica la fórmula o backend, fija versión cuando sea posible y **nunca instales sin autorización**. La matriz de ese anexo es orientativa, no un mandato para instalar todas las herramientas.

## Recetas de elección por objetivo (80/20)

- **Flechas y límites:** manifests/build + una regla ejecutable del lenguaje + comprobar la arista real; no pagar CodeQL solo por contar imports.
- **Clones y smells:** jscpd + linter nativo + muestra manual; solo medir complejidad si el coste/riesgo lo justifica.
- **Defecto funcional:** test focal y contrato inverso primero; cobertura/mutación solo si aportan información al riesgo.
- **Seguridad de PR:** rutas de entrada/sink y reglas específicas; herramienta SAST + lock scanner si hay cambio relevante; DAST/fuzz aislados y autorizados.
- **Release:** manifiesto/artefacto + CI del SHA + cobertura de gates del proyecto + SBOM/scan cuando el producto lo requiera.
- **Rendimiento:** perfil en ruta crítica medida antes de imponer un benchmark completo.

**Evidencia:** los enlaces son puntos de consulta, no validaciones instaladas ni mediciones de ningún repositorio. No confundir una feature de un producto con haberla usado. En herramientas SaaS o de licencia dual, comprobar términos actuales antes de mandar código o integrarlas.
