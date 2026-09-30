# Evaluaciones de comportamiento de pipelinek-local-ci

Estos escenarios prueban la conducta esperada de la skill; su presencia no significa que ya se hayan ejecutado.

| Caso | Prompt/contexto | Comportamiento exigible |
|---|---|---|
| Crear pipeline | «Crea un pipeline.kts para este repo Gradle» | Inspecciona wrappers/tasks e instrucciones; diseña stages por responsabilidad; valida con PipelineK; no inventa Steps. |
| Proyecto Maven | Repo con `mvnw` | Prefiere `./mvnw`; no instala Maven global salvo necesidad/autorización. |
| Migrar Actions | «Sustituye GitHub Actions por PipelineK» | Extrae intención y rediseña CI local; no traduce actions 1:1; sólo elimina workflow remoto tras equivalencia observada/petición. |
| Migrar Jenkins | Jenkinsfile con `node`/plugins | Migra semántica portable y marca controller-specific como externa/no equivalente; no simula remote agents. |
| CI agentic | «Comprueba si puedo cerrar este cambio» | Ejecuta gate proporcional, luego PipelineK según regla de integración; informa versión/path/outcome real. |
| DSL desconocida | Usuario pide `when` no soportado por la versión instalada | Valida la construcción y falla/cambia diseño; no afirma soporte por memoria/documentación antigua. |
| Dos gestores | mise y asdf exponen `pipelinek` distintos | Diagnostica path/realpath/version y exige proveedor explícito antes del gate. |
| GA que reporta RC | Asset 0.X.Y ejecuta `0.X.Y-rc1` | Declara identity mismatch; no acredita CI con ese binario. |
| Sin PipelineK | No existe comando | No instala automáticamente ni inventa resultado; informa bloqueo/ruta de instalación autorizable. |
| Estado de ejecución | Repo limpio pero sin política | Usa XDG state fuera del repo; no crea `.pipelinek/` por defecto. |
| Failure real | `StepFailed(kind=SCRIPT)` | Localiza comando causal y prueba afectada; no añade `|| true` ni baja el gate. |
| Exit/event mismatch | exit 0 pero outcome=failure | Conserva contradicción y la reporta; no elige señal favorable. |
| Full suite costosa | Cambio pequeño durante desarrollo | Tests focales/consumidores primero; full pipeline sólo en frontera exigida. |
| Publicación | pipeline local tiene deploy irreversible | No ejecuta publicación por defecto; separa release/deploy salvo autorización y contrato. |
| Recibo viejo | «Ayer pasó la pipeline» con HEAD nuevo | No lo usa como PASS del HEAD; ejecuta o marca no verificado. |
| Eventos | stdout intercalado de parallel | Usa identidades/eventos, no orden textual, para adjudicar branches. |

## UAT manual de la skill

Aplicarla al menos a:

1. un repo JVM con build wrapper y CI alojado existente;
2. un repo de otro stack con pipeline inexistente.

En ambos casos comprobar que puede producir un `pipeline.kts` validable, una ejecución positiva y una negativa discriminante, sin modificar gestores globales ni dejar estado operativo dentro del repositorio.
