# Recetas por ecosistema: extracción antes de instalar nada

Estas recetas son **ejemplos**, no comandos universales: ejecuta solo si la herramienta ya existe y el usuario autoriza builds/tests que podrían descargar dependencias o ejecutar scripts. Prefiere wrappers/locks del proyecto. Registra toolchain y exit code. No hagas una reinstalación ni invocación de `npx` que descargue software sin consentimiento.

| Ecosistema | Grafo y tipos | Tests focales / completos (adaptar rutas) | Cobertura y análisis opcional |
|---|---|---|---|
| Git / cualquiera | `git rev-parse HEAD`; `git status --short`; `git diff --name-status BASE...HEAD`; `git grep -n 'PATRON' -- 'src/**'` | leer política y script exacto del repo | `git log --oneline -- PATH`; comparaciones `BASE...HEAD` solo con base válida |
| Kotlin / Java + Gradle | `./gradlew projects`; `./gradlew dependencies --configuration <config>` y `dependencyInsight --dependency <name> --configuration <config>`; buscar tipos y referencias con IDE/ArchUnit/Konsist | `./gradlew :modulo:test --tests 'paquete.ClaseTest'`; después gates completos configurados | JaCoCo/Kover/detekt si están configurados; salida solo del módulo instrumentado |
| Java + Maven | `mvn dependency:tree`; revisar `pom.xml` de ambos módulos, scopes y profiles | `mvn -pl modulo -Dtest=ClaseTest test` (dependencias previas según reactor); `mvn verify` cuando proceda | JaCoCo/PIT/ArchUnit según plugins existentes |
| Rust | `cargo metadata --format-version 1 --no-deps`; `cargo tree`; `cargo modules dependencies` si está instalado | `cargo test -p <crate> <filtro>`; para validación workspace usar gates definidos (`cargo test --workspace` si procede) | `cargo clippy`, `cargo fmt --check`, `cargo llvm-cov`, `cargo mutants` opcionales |
| Python | `python -m pip list` solo si identifica entorno del proyecto; leer `pyproject.toml` y lock; `python -m pipdeptree` solo si instalado | `python -m pytest tests/test_modulo.py -q`; suite completa `python -m pytest` cuando esté previsto | `coverage run -m pytest`, `coverage report`, Ruff, mypy/pyright, Radon si configurados |
| JS / TS | leer `package.json` scripts, workspace y lock; `npm ls --all` si usa npm; dependency-cruiser si disponible | `npm test -- --runInBand <filtro>` es **solo** un ejemplo para runners compatibles; usar script/ruta del proyecto y su CLI propia | `tsc --noEmit` si configurado; ESLint, c8/nyc, Stryker, jscpd, dependency-cruiser |
| Go | `go list -m all`; `go list -deps ./...` (puede resolver/descargar); `go mod graph` | `go test ./ruta/... -run 'TestNombre$'`; luego `go test ./...` | `go test ./... -coverprofile=coverage.out`; `go tool cover -func=coverage.out`; `govulncheck` si instalado |
| .NET | `dotnet list <project> package --include-transitive` (consultar comando de SDK instalado); examinar `.sln`, `.csproj` | `dotnet test <project> --filter FullyQualifiedName~NombreTest`; luego `dotnet test` acorde al repo | coverlet / `--collect:"XPlat Code Coverage"` si disponible; ArchUnitNET; `dotnet format --verify-no-changes` |
| PHP | `composer show -t` puede necesitar entorno configurado; inspeccionar `composer.lock` | `vendor/bin/phpunit --filter NombreTest`; suite completa según proyecto | Deptrac, PHPStan/Psalm, PHPUnit coverage (driver configurado) |
| C/C++ | examinar `CMakeLists.txt`, build graph y `compile_commands.json`; `cmake --build <builddir> --target <target>` solo con build preparado | `ctest --test-dir <builddir> -R <patron>`; después `ctest --test-dir <builddir>` | clang-tidy, clang static analyzer, gcov/llvm-cov, sanitizers en entorno aislado |

### Receta transversal para aristas arquitectónicas

1. Detecta **unidad real de compilación** (package, crate, módulo, assembly) y dependencias declaradas.
2. Extrae símbolos del módulo origen referenciados al módulo destino; revisa alias, fully-qualified, anotaciones, DI, imports y generación de código.
3. Intenta build de núcleo aislado o test arquitectónico explícito si existe. Si no, describe la evidencia estática limitada.
4. Clasifica cada arista por regla del repositorio, no por su nombre; el grafo no indica por sí mismo si un límite es bueno o malo.

### Receta mínima de revisión sin ejecución

`git rev-parse HEAD` → `git diff --name-status <base>...HEAD` → archivos de build/locks → productores y consumidores → tests existentes → CI configurada → matriz `CÓDIGO/DOCUMENTADO/NO VERIFICADO`. Esta ruta es válida cuando ejecutar o instalar herramientas no está autorizado.
