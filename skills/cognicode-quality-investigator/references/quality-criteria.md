# Criterios de revisión: las mismas doce dimensiones de code-quality-evidence-review

**Esta ficha conserva los criterios de la skill genérica. CogniCode se utiliza como explorador según `cognicode-queries.md`, nunca como sustituto del contraste independiente.**

**Método común por ficha:** cuestión falsable → universo de archivos/símbolos → extracción/manual o herramienta → contraste y contraejemplo → evidencia `SHA/ruta:línea/comando/resultado` → impacto → cierre. No exijas ninguna técnica concreta si no es relevante para el producto o el diseño declarado. En una PR inspecciona cambios + consumidores inversos y riesgo transversal; en auditoría global recorre todas las fichas.

## D01 — Arquitectura y límites hexagonales (cuando existan)

**Preguntas.** ¿Qué responsabilidades y límites declara el sistema? ¿El dominio/application depende de adaptadores/infraestructura o solo de abstracciones permitidas? ¿Hay puertos que filtran tipos/frameworks ajenos? ¿La composición se sitúa en un borde apropiado? ¿Build, fuente, DI/runtime y código generado respetan el contrato?

**Obtención.** Extrae módulos/manifests, rutas e interfaces; dibuja grafo `módulo → módulo` y `símbolo → símbolo`; detecta imports, herencia, DTOs, plugins de compilación, reflective loading y registro/DI. Abre el archivo y manifest de **ambos extremos** de una arista sospechosa; inspecciona el caso de uso y los tests del contrato. Herramientas orientativas: ArchUnit, Konsist, dependency-cruiser, Deptrac, cargo-modules, ArchUnitNET (según lenguaje). También se puede verificar con build aislado/archivo de regla minimalista.

**Contraste.** Distingue build vs runtime, código de test vs producción, contrato interior vs librería de utilidad permitida, excepciones documentadas. `grep -r import` solo inspecciona una cadena; nunca concluye “dominio independiente” sin revisar manifests, otras clases de referencias y alcance. **Salida:** reglas concretas y aristas prohibidas verificadas; arquitectura desconocida o híbrida no equivale automáticamente a hexagonal mal implementada.

## D02 — SOLID, tipos funcionales y validez de estados

**Preguntas.** ¿Qué componentes tienen motivos incompatibles de cambio (SRP)? ¿Cómo extiende un consumidor una implementación (OCP/DIP)? ¿Un sustituto respeta contratos (LSP)? ¿El cliente depende de capacidades que no consume (ISP)? ¿Existen estados o errores semánticamente distintos mezclados en un boolean/null/string que permitan decisiones incorrectas? ¿Qué funciones prometen pureza y dónde hay I/O?

**Obtención.** Localiza contratos públicos, implementaciones, extensiones, enum/sealed/union y todas sus ramas, adaptadores e I/O. Examina cambios de código en historial para verificar cambios coordinados; busca flags, casts, `Any`, excepciones y valores centinela como **candidatos**; contrasta con pruebas de propiedad/contrato y casos límite. Herramientas: language server, typechecker, detekt/Ruff/ESLint/Clippy/PMD o reglas AST/CodeQL propias.

**Contraste.** Null es válido para ausencia legítima; excepciones son válidas en los bordes; funciones impuras en adaptadores no violan el diseño. Un objeto pequeño también puede tener dos motivos de cambio. **Salida:** contrato y ruta concreta de fallo o coste real de extensión; preferir un tipo suma/enum si efectivamente evita estados imposibles y el lenguaje lo permite.

## D03 — Connascence estática

**Preguntas.** ¿Qué pares de elementos han de cambiar juntos por nombre, tipo, significado, posición o algoritmo? ¿Se protege el acuerdo con contrato versionado/tipo o viaja mediante magia semántica? ¿Cuál es la distancia entre dependientes?

**Obtención.** Busca símbolos usados en más de un módulo, schemas y codecs, ordinales, strings duplicados y algoritmos replicados; identifica productor A/consumidor B, regla de coordinación, escenario de evolución y ejemplo de cambio conjunto. Emplea búsqueda semántica, reglas personalizadas ast-grep/Semgrep, diagramas de dependencias, análisis de co-cambios Git y tests de compatibilidad.

**Contraste.** Formatos posicionales validados pueden ser intencionales. Un ADT reduce ambigüedad de significado, no elimina la connascence of Type. Un grafo no demuestra un índice cuantitativo. No llames SCIJ a una métrica casera de Kotlin/Rust/Python ni uses “alta/baja” sin unidad de análisis. **Salida:** parejas A/B, distancia, impacto de cambio y test que fallaría.

## D04 — Duplicidad de responsabilidades, acoplamiento, cohesión y complejidad

**Preguntas.** ¿Dos implementaciones hacen lo mismo pero divergen? ¿Qué ciclos o capas concentran cambios? ¿Hay módulos de múltiples razones de cambio? ¿La complejidad dificulta una ruta crítica?

**Obtención.** Detector de clones (jscpd), grafo dirigido y SCC/ciclos (dependency-cruiser, cargo-modules, ArchUnit o script), complejidad ciclomática (Lizard, Radon, herramientas de lenguaje), fan-in/out definido por grafo, `git log --follow`/diffs. Localiza test que compare salidas de implementaciones cuando haya dos motores/versiones.

**Contraste.** Clon textual ≠ mismo comportamiento/semántica; módulos de compatibilidad pueden estar duplicados deliberadamente. Métricas no son diagnósticos sin lectura de rutas, propósito y cambio. **Salida:** lugares de responsabilidad duplicada/ciclos reproducibles; costes concretos de mantenimiento o divergencia.

## D05 — Deuda técnica

**Preguntas.** ¿Es un defecto del diff o una decisión preexistente? ¿Hay dueño, fecha, condición de retirada, alternativa y consumo actual? ¿La aceptación de la deuda sigue siendo válida?

**Obtención.** `git blame/log`, ADRs vigentes/superados, TODOs contextualizados, issues relacionadas, deprecaciones, migraciones incompletas y cambios simultáneos que exigen tocar caminos legados. Herramientas: Git, gestor de issues, analizadores de duplicación/dependencia para respaldar el costo.

**Contraste.** No conviertas un TODO decorativo en bloqueo ni el legado del repositorio en regresión de una PR. La ausencia de benchmark/cobertura sin requisito, objetivo o consumidor puede ser una oportunidad, no una deuda confirmada. **Salida:** deuda aceptada / introducida / sin propiedad y criterio de cierre independiente del capricho de herramienta.

## D06 — Tests y cobertura

**Preguntas.** ¿Qué comportamiento/contratos protegen los tests actuales? ¿Qué caminos críticos carecen de assertions? ¿Qué fue ejecutado en este SHA? ¿Cobertura de líneas/ramas, mutación y aceptación describen fenómenos distintos?

**Obtención.** Ubica suites, fixtures, asserts y artefactos de test. Ejecuta suite focal sobre archivos cambiados y consumidores del contrato; añade property-based/fuzz/contract/integration/UAT según riesgo y permisos. Para porcentaje mide instrumentación con JaCoCo/Kover, coverage.py, gcov/llvm-cov, Go cover, nyc/c8, cobertura .NET, etc. Para calidad de aserciones usa PIT, Stryker, cargo-mutants (si compensa coste) y ejemplos de defectos inyectados. Registra comandos, SHA, suite y cobertura del universo.

**Contraste.** Test existente ≠ ejecutado; 100 % de líneas ≠ 100 % de comportamiento; logs sin exit code no acreditan éxito; tests filtrados omiten el resto; un timeout no es un PASS. **Salida:** mapa de riesgo/contrato/test, números solo si se han medido, pruebas y lagunas.

## D07 — CI/CD y reproducibilidad

**Preguntas.** ¿Qué jobs, matrices, `needs`, reglas de skip y condiciones se ejecutan realmente en el SHA auditado? ¿Build local y CI usan mismo artefacto? ¿Se verifican checks de release, permisos mínimos, secrets, cache, toolchain y rollback exigidos?

**Obtención.** Lee workflows/pipelines y triggers; identifica id de run, commit SHA, jobs y estados finales; inspecciona artifacts, JUnit/SARIF/coverage, presupuestos de timeout, dependencias de jobs, desactivaciones, retry y scripts que realmente invocan. Alternativas según plataforma: gh, GitLab CLI/API, Jenkins API/Blue Ocean, Azure DevOps CLI o inspección de artefactos proporcionados. Si no hay credenciales, registra `CI no verificado` y qué run falta.

**Contraste.** Workflow presente ≠ job ejecutado; green badge de main ≠ head de PR; `continue-on-error`, matriz parcial, `skipped`, test report antiguo y retries pueden esconder ausencia de validación. **Salida:** tabla por gate y SHA con PASS/FAIL/NO EJECUTADO/NO APLICA más evidencia.

## D08 — Seguridad

**Preguntas.** ¿Cuál es el límite de confianza? ¿Entrada no confiable llega a sink sensible? ¿Existen límites de tamaño/tiempo, validaciones, aislamiento, autorizaciones y manejo seguro de secretos? ¿Una alerta corresponde a ruta real explotable?

**Obtención.** Modela entradas → validadores → comandos/DB/archivos/network, revisa rutas de fallo y límites; analiza reglas con Semgrep/CodeQL, secretos con Gitleaks, dependencias con OSV/Trivy y configuración IaC con Trivy/Checkov (según alcance). Prueba rutas negativas con fixtures inertes en sandbox con consentimiento. Para detalles ver `references/07-security-supply-chain.md`.

**Contraste.** Hallazgo SAST requiere triage, versión de dependencia y condiciones de explotación; no reproduzcas secretos o payload dañino. **Salida:** condición, ruta, barreras reales, impacto y test de regresión de seguridad.

## D09 — Rendimiento

**Preguntas.** ¿Qué operación importa al consumidor (arranque, endpoint, batch, replay, serialización)? ¿Cuál es SLA/SLO o baseline aprobado? ¿Existen regresión y variabilidad medidas bajo mismas condiciones?

**Obtención.** Define workload, dataset, entorno, CPUs/RAM, versión de runtime y warm-up, concurrencia y percentiles; mide latencia, throughput, CPU, asignación/memoria e I/O pertinente. Herramientas posibles: hyperfine para CLI, JMH para JVM, Criterion para Rust, pytest-benchmark, k6 para carga de API, perf/flamegraph/profilers según permisos. Compara distribución base vs HEAD antes de atribuir causalidad.

**Contraste.** Build cache/paralelismo y tamaño del repo no prueban performance de la aplicación. Un único tiempo no demuestra regresión; benchmark micro no acredita E2E. **Salida:** mediciones reproducibles, incertidumbre, SLO/objetivo definido o baseline por establecer.

## D10 — Dependencias, licencias y SBOM

**Preguntas.** ¿Cuál es el árbol *resuelto* y qué se distribuye realmente? ¿Se controla versión, transitorias y licencia real? ¿Qué vulnerabilidades aplican al artefacto y al despliegue concretos?

**Obtención.** Lee manifest/lock + grafo resuelto; registra runtime/build/test y runtime final/imagen. Genera SBOM opcional (Syft/ORT), escanea vulnerabilidades (OSV-Scanner/Trivy/Grype/cargo-audit etc.) y licencias (ORT/ScanCode/SPDX). Fecha de consulta, advisory, affected range, versión resuelta, mitigación y exclusión forman parte de evidencia.

**Contraste.** CVE de versión no instalada, paquete solo de test, API no usada o licencia de proyecto de referencia no certifican impacto. **Salida:** lista verificable de dependencias afectadas con camino desde artefacto y acción de actualización/mitigación; riesgos legales a validar con especialistas.

## D11 — Documentación y mantenibilidad

**Preguntas.** ¿Una persona puede construir, ejecutar, probar y desplegar usando instrucciones actuales? ¿ADRs, ejemplos y contratos reflejan código vigente? ¿Quién es dueño de cambios y qué rutas están obsoletas?

**Obtención.** Contrasta README, changelog, ADR, API docs, configuración, ejemplos, `AGENTS.md`, runbooks y diagramas con build y código. Reproduce onboarding con shell aislado si está permitido; comprueba links y referencias cruzadas, decisiones supersedidas, opciones de configuración huérfanas. Herramientas posibles: markdownlint, lychee, Vale, MkDocs/Docusaurus si ya existen; tests de ejemplos del repositorio.

**Contraste.** Volumen de docs no es actualidad. Desvío documental es hallazgo si muestra usuario/comando/contrato afectado. **Salida:** instrucción concreta no reproducible o inconsistencia demostrada y corrección comprobable.

## D12 — Observabilidad

**Preguntas.** ¿Puede un operador o consumidor reconstruir resultado/causa de error/reintento? ¿Hay correlación de logs, eventos, métricas y spans cuando el producto lo requiere? ¿Qué señales faltan para responder a incidentes reales?

**Obtención.** Traza `petición/ejecución → span/evento/log → ID/correlación → almacenamiento/lectura → alerta`; inspecciona formato, IDs, errores, pérdida de eventos, sampling, cardinalidad, PII y propagación de contexto. Mide una ejecución de prueba y verifica recuperación de señales. Herramientas opcionales: SDK/Collector OpenTelemetry, Prometheus para métricas, Grafana/Jaeger/Tempo para visualización, logs estructurados nativos. Decide qué se necesita según requisitos de operación.

**Contraste.** Eventos tipados ≠ tracing distribuido, y ausencia de OTel ≠ ausencia de observabilidad. No impongas SaaS/APM para servicios locales sin necesidad. **Salida:** escenario de diagnóstico reproducible, laguna observable y señal/test requerido.
