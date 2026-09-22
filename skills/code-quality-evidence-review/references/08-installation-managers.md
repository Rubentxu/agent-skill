# ANEXO — Instalación controlada de herramientas: asdf, mise y Homebrew

**Revisión documental:** 2026-09-22. Este anexo acompaña a `05-tool-catalog.md`; **no instala nada por sí solo**, no exige un gestor concreto y no obliga a añadir herramientas a la aplicación auditada. Los nombres de paquetes, backends, versiones y compatibilidad con cada sistema cambian: **comprobar la fuente indicada y el entorno real antes de proponer un comando ejecutable**. Los ejemplos con `VERSION` son plantillas: sustituir por una versión existente y aprobada, nunca ejecutar literalmente.

## 1. Política de selección e instalación (obligatoria para el agente)

1. **Detectar antes de sugerir:** lenguaje, versión del runtime, OS/arquitectura, shell, contenedor, binarios presentes (`command -v <binario>`), gestores presentes (`command -v mise; command -v asdf; command -v brew`), archivos `.tool-versions`, `mise.toml`, `Brewfile`, manifests y lockfiles. No asumir que cualquiera de los gestores está instalado; un binario puede pertenecer al repositorio, a la distribución o a un contenedor.
2. **Distinguir tipos de herramienta:** (a) **CLI independiente** (actionlint, Trivy, hyperfine); (b) **runtime** (Java, Node, Python, Rust, Go); (c) **plugin/librería del proyecto** (ArchUnit, Konsist, JaCoCo, Kover, PIT, JMH, test runners, TypeScript/ESLint, etc.); (d) **servicio** (Prometheus, Jaeger, Grafana, ZAP); (e) **utilidad del sistema** (perf, Graphviz). Las categorías (c) y (d) NO se resuelven automáticamente instalando un binario global.
3. **Preferir, en este orden:** versión y runner ya declarados por el proyecto → CLI preexistente y compatible → ejecución efímera, aislada y autorizada → mise/asdf con versión fijada para herramientas versionables → Homebrew con `Brewfile` para utilidades compartidas → instalador oficial si no hay alternativa adecuada. No mezclar gestores para el MISMO ejecutable sin motivo; evitar sombreado de `$PATH`.
4. **Antes de actuar:** identificar **por qué** hace falta, indicar mínimo de herramientas, mostrar comandos, fuente y consecuencias (red, scripts de instalación, cambios de PATH, home/proyecto, descargas y credenciales), comprobar permisos/privacidad y solicitar autorización para instalación, edición de configuración, ejecución de contenedores o escaneos con efectos. Nunca ejecutar `curl | sh` ni scripts de plugins comunitarios de un repo desconocido sin revisión y autorización.
5. **Reproducibilidad:** resolver y fijar versión exacta (`mise use --pin`, `mise lock`/`mise install --locked` cuando proceda, `asdf set` con versión concreta, dependencias en lockfile). Guardar gestor, fuente/plugin, versión, plataforma, ruta del binario y comando de comprobación; tener en cuenta checksums/provenance cuando el backend los soporte. `latest` es para explorar, NO un lock de auditoría.
6. **No se autoriza por omisión:** la petición de *auditar* no autoriza instalar herramientas, alterar repositorios ni transmitir código a SaaS. Si faltan dependencias o permiso, ofrecer alternativa manual y marcar evidencia `NO VERIFICADO`.

**Selección rápida:**

| Circunstancia | Gestor preferente | Qué queda versionado | Qué NO resuelve |
|---|---|---|---|
| Equipo que ya utiliza mise | **mise** para CLIs y runtimes disponibles en su registry o backend verificable | `mise.toml`, `mise.lock` cuando se utiliza | Librerías de proyecto, servicios, instalaciones de host ajenas |
| Equipo que ya utiliza asdf | **asdf** para runtimes y plugins mantenidos; instalar las CLIs mediante el gestor del lenguaje o binarios autorizados | `.tool-versions` de runtimes; *no* las CLIs instaladas con pip/npm/cargo si no se registran aparte | Un plugin de asdf para *cada* herramienta del catálogo |
| Utilidades de estación de trabajo en macOS o Linux con Homebrew | **Homebrew** y, opcionalmente, `Brewfile` | Declaración de fórmulas; versiones generalmente **móviles** al actualizar | Pin completo de versiones antiguas, runtime de la aplicación, librerías internas |
| Proyecto que ya usa Gradle/Maven/npm/Cargo/uv/dotnet | **Gestor nativo del proyecto** y wrapper/lockfile | Dependencias por aplicación | No conviene duplicarlas globalmente con asdf/mise/brew |

## 2. Mise: cómo descubrir, instalar y verificar

Documentación oficial: [instalación](https://mise.jdx.dev/getting-started), [registry](https://mise.jdx.dev/registry), [backends](https://mise.jdx.dev/dev-tools/backends/), [configuración](https://mise.jdx.dev/configuration.html), [locking](https://mise.jdx.dev/dev-tools/mise-lock.html).

```bash
# Solo lectura: comprobar si existe y qué fuente/versiones ofrece
command -v mise && mise --version
mise registry actionlint
mise ls-remote actionlint
mise config ls
mise ls --current

# Tras autorización, desde un directorio PROPIO (no en el repo de un tercero):
mise use --pin actionlint
mise exec -- actionlint -version   # actionlint; otras CLIs pueden usar --version

# Si se aprueba un default personal, no editar repositorios:
mise use -g --pin hyperfine
mise exec -- hyperfine --version

# Reproducir herramientas ya declaradas en un proyecto revisado y aprobado:
mise install
```

`mise use` instala **y escribe** la configuración correspondiente; `mise install <tool>` instala sin activarla en un proyecto si no estaba declarada; `mise exec <tool>@VERSION -- <comando>` permite una ejecución concreta sin escribir `mise.toml`. `mise use -g` modifica configuración personal. Registrar y revisar diffs cuando se use `mise use` dentro de un repo. **No lanzar los cuatro comandos como un script automático**: son alternativas para decisiones distintas.

El registry contiene rutas abreviadas para, entre otros, `actionlint`, `ast-grep`, `gitleaks`, `hyperfine`, `lychee`, `syft` y `trivy`; **comprobar plataforma y versiones antes de instalar**. Si no hay alias, estudiar **una** fuente explícita ([aqua](https://mise.jdx.dev/dev-tools/backends/aqua), [GitHub releases](https://mise.jdx.dev/dev-tools/backends/github), [cargo](https://mise.jdx.dev/dev-tools/backends/cargo), [go](https://mise.jdx.dev/dev-tools/backends/go.html), [npm](https://mise.jdx.dev/dev-tools/backends/npm), [PyPI](https://mise.jdx.dev/dev-tools/backends/pipx.html)). Un nombre de proyecto en GitHub no garantiza que el backend encuentre un artefacto compatible.

```bash
# EJEMPLOS POR ECOSISTEMA, solo después de consultar registry, soporte y permisos:
mise use --pin 'cargo:cargo-llvm-cov'   # requiere Rust/Cargo o binario soportado
mise use --pin 'npm:jscpd'              # CLI npm; revisar scripts de instalación
mise use --pin 'pypi:pip-audit'         # CLI PyPI en entorno aislado; backend PyPI actual
# mise exec -- cargo llvm-cov --help / jscpd --help / pip-audit --help
```

Para dependencias nativas/permisos (p. ej., `perf`) no instalar a ciegas desde mise. Para `npm:` y `pypi:` verificar los backends **de la versión instalada** (sintaxis y política de scripts han cambiado), intérprete y procedencia de la distribución. En repos privados, revisar antes cualquier backend que descargue desde Internet. Si se requiere versión reproducible del propio runtime: fijar `node`, `python`, `java`, `rust` o `go` en la configuración aprobada y comprobar `mise exec -- <runtime> --version`.

Ejemplo de configuración **ilustrativa, NO fijada y NO lista para CI**: al aceptar los paquetes, reemplazar las claves de versión `latest` con las versiones resueltas y revisar `mise.lock` cuando proceda:

```toml
# mise.toml de ejemplo, creado únicamente en un workspace autorizado
[tools]
actionlint = "latest"
ast-grep = "latest"
hyperfine = "latest"
trivy = "latest"
```

## 3. asdf-vm: runtimes, plugins y CLIs nativas del lenguaje

Documentación oficial: [guía actual](https://asdf-vm.com/guide/getting-started.html), [gestión de versiones](https://asdf-vm.com/manage/configuration.html), [plugins comunitarios](https://github.com/asdf-vm/asdf-plugins). En versiones modernas de asdf (0.16+) se usa `asdf set [ -u ]`; las instrucciones antiguas `asdf local/global` NO deben copiarse sin comprobar la versión real.

```bash
# Comprobar antes de modificar (asdf moderno)
command -v asdf && asdf --version
asdf plugin list
asdf current

# Elegir SOLO los runtimes necesarios; estos son ejemplos de plugins mantenidos:
asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git
asdf plugin add python https://github.com/asdf-community/asdf-python.git
asdf plugin add golang https://github.com/asdf-community/asdf-golang.git
asdf plugin add java https://github.com/halcyon/asdf-java.git

# Seleccionar un runtime REAL y validado en el repo; VERSION es un marcador:
asdf list all nodejs
asdf install nodejs VERSION
asdf set nodejs VERSION        # escribe .tool-versions local
# asdf set -u nodejs VERSION  # alternativa: default personal
node --version
```

**No ejecutar la lista entera:** instalar un plugin descarga código ejecutable externo, y `asdf install` puede ejecutar scripts del plugin. Revisar sus repositorios/origen y dependencias y solicitar permiso. Si el equipo ya tiene un plugin/configuración, reutilizarla. Para elegir JDK, consultar `asdf list all java` porque las versiones incluyen la distribución (no suponer `java 21` en todos los plugins).

`asdf` **no instala automáticamente** `jscpd`, `dependency-cruiser`, `pip-audit`, `cargo-mutants` o `govulncheck` por haber elegido Node/Python/Rust/Go. Ruta correcta: gestionar el runtime con asdf y **declarar después la CLI en su ecosistema o en un entorno aislado**:

```bash
# Ejemplos independientes: usar solo el ecosistema correspondiente y versión aprobada.
# npm (en un proyecto autorizado, con lockfile):
npm install --save-dev --save-exact 'dependency-cruiser@VERSION' 'jscpd@VERSION'
npx --no-install depcruise --version

# Python: preferir pipx ya existente / entorno dedicado, sin modificar el Python del sistema:
pipx install 'pip-audit==VERSION'
pip-audit --version

# Rust: sólo si el proyecto necesita la CLI y tiene cargo/rustc:
cargo install cargo-llvm-cov --version VERSION --locked
cargo llvm-cov --help

# Go: preferir instalación acotada en un GOBIN aprobado o mise go:...; no modificar la app:
go install golang.org/x/vuln/cmd/govulncheck@VERSION
```

Si se instala una CLI con `npm -g`, `pipx`, `cargo install` o `go install`, su **versión no queda fijada automáticamente por `.tool-versions`**: registrar además la versión del paquete/comando y su dependencia del runtime. Algunas instalaciones con asdf requieren `asdf reshim <runtime>` para descubrir un binario nuevo; comprobar primero el plugin y `$PATH`. Para librerías de calidad JVM usar Gradle/Maven **del proyecto**, no un plugin global improvisado.

## 4. Homebrew: paquetes verificados y `Brewfile`

Fuentes oficiales: [fórmulas](https://formulae.brew.sh/), [manual `brew`](https://docs.brew.sh/Manpage), [`brew bundle`/Brewfile](https://docs.brew.sh/Brew-Bundle-and-Brewfile). Homebrew soporta macOS y Linux, **pero comprobar que existe una bottle compatible con OS/arquitectura y dependencias**; en Linux minimal/immutable puede ser preferible una toolbox/contenedor aprobado. **`brew install` no fija por sí mismo una versión reproducible** a largo plazo.

```bash
# Descubrimiento/lectura (antes de instalar):
command -v brew && brew --version
brew info --formula actionlint
brew info --formula trivy
brew list --versions

# Instalar SOLO lo aprobado, por nombre de fórmula comprobado:
brew install actionlint ast-grep gitleaks hyperfine lychee syft trivy

# Para materializar un conjunto acordado, opcionalmente:
brew bundle check --file=RUTA_AL_BREWFILE
brew bundle install --file=RUTA_AL_BREWFILE
```

**Fórmulas confirmadas documentalmente en Homebrew:** ver la página de fórmula antes de ejecutar el comando. Los siguientes son **nombres de fórmula**, no promesas de compatibilidad con todas las plataformas:

| Tipo | Fórmulas y enlaces oficiales | Precauciones |
|---|---|---|
| Arquitectura y patrones | [`ast-grep`](https://formulae.brew.sh/formula/ast-grep), [`graphviz`](https://formulae.brew.sh/formula/graphviz) | Graphviz dibuja, no descubre arquitectura. |
| Duplicación y complejidad | [`jscpd`](https://formulae.brew.sh/formula/jscpd), [`lizard-analyzer`](https://formulae.brew.sh/formula/lizard-analyzer) | **No** confundir `lizard-analyzer` (complejidad) con [`lizard`](https://formulae.brew.sh/formula/lizard) (compresor). Son paquetes en conflicto. |
| Estática, workflows y secretos | [`semgrep`](https://formulae.brew.sh/formula/semgrep), [`actionlint`](https://formulae.brew.sh/formula/actionlint), [`gitleaks`](https://formulae.brew.sh/formula/gitleaks) | Un scan no prueba ausencia de defectos; outputs pueden contener secretos. |
| Supply chain | [`trivy`](https://formulae.brew.sh/formula/trivy), [`syft`](https://formulae.brew.sh/formula/syft), [`grype`](https://formulae.brew.sh/formula/grype), [`osv-scanner`](https://formulae.brew.sh/formula/osv-scanner), [`checkov`](https://formulae.brew.sh/formula/checkov) | Elegir scanner por artefacto y necesidad; no instalar cinco por defecto. |
| Tests y rendimiento | [`cargo-llvm-cov`](https://formulae.brew.sh/formula/cargo-llvm-cov), [`hyperfine`](https://formulae.brew.sh/formula/hyperfine) | `cargo-llvm-cov` precisa toolchain adecuada; hyperfine mide comandos, no SLA del sistema. |
| Documentación y otros | [`lychee`](https://formulae.brew.sh/formula/lychee), [`vale`](https://formulae.brew.sh/formula/vale), [`pmd`](https://formulae.brew.sh/formula/pmd) | PMD requiere Java compatible; Vale exige configuración de reglas para utilidad real. |

Ejemplo de `Brewfile` **personal/opt-in**, mínimo y no obligatorio:

```ruby
# Solo CLIs independientes que tu auditoría necesite y cuyo nombre has verificado.
brew "actionlint"
brew "ast-grep"
brew "gitleaks"
brew "hyperfine"
# brew "trivy"       # activar solo para escaneo de dependencias/imagen aprobado
# brew "syft"        # activar solo si se necesita generar SBOM
```

`brew bundle check` **no** demuestra que las versiones estén fijadas ni que cada herramienta haya analizado el SHA. Inspeccionar `brew info --formula <nombre>` y la ruta real (`command -v ...`) tras la instalación. No ejecutar `brew bundle` sobre un `Brewfile` arbitrario del repo sin revisar su contenido.

## 5. Matriz por cometido: ruta viable, no obligación

Leyenda: **M** = explorar en el registry de mise (`mise registry <nombre>`), instalable *solo si* hay versión/plataforma compatible; **B** = Homebrew formula indicada en §4; **A→nativo** = asdf gestiona runtime, CLI instalada/versionada por gestor nativo del proyecto; **P** = preferir dependencia/plugin del proyecto; **S** = servicio/host, despliegue separado y autorizado. `—` = no recomendar ese gestor como ruta por defecto (no equivale a imposibilidad absoluta).

| Herramienta/objetivo | mise | asdf | Homebrew / vía recomendada |
|---|---|---|---|
| actionlint, ast-grep, gitleaks, hyperfine, lychee, trivy, syft | M (alias registrado) | — | B (§4) |
| Semgrep, Grype, OSV-Scanner, Checkov | verificar registry antes de afirmar alias | Python/Go según CLI aprobada; no asumir plugin | B (§4) |
| Graphviz, PMD, Vale, jscpd, cargo-llvm-cov | comprobar alias/backend; `npm:jscpd` / `cargo:cargo-llvm-cov` opcionales | A→npm / A→cargo | B (§4) |
| lizard (analizador), Radon, Ruff, pip-audit, pytest-benchmark, coverage.py | `pypi:lizard`/`pypi:radon`/etc. si CLI adecuada; no para librerías importadas | A→pipx o entorno Python **del proyecto** | B únicamente para `lizard-analyzer`; otras rutas requieren comprobación de fórmula |
| dependency-cruiser, Madge, ESLint, Vitest, StrykerJS, Playwright, nyc, c8, fast-check, markdownlint | `npm:<paquete>` para CLI independiente si corresponde; plugins/test suites en proyecto | A→npm **local**, con lockfile | **P** preferente para runners y librerías |
| ArchUnit, Konsist, ArchUnitNET, JaCoCo, Kover, PIT, JMH, jqwik, Pact/Testcontainers SDK, Criterion.rs | gestionar JDK/.NET/Rust cuando se necesiten; dependencia con gestor nativo | A→Gradle/Maven/NuGet/Cargo | **P**: no instalar globalmente la API ni duplicar wrappers |
| cargo-modules, cargo-mutants, cargo-audit, cargo-fuzz, proptest | backend Cargo si es CLI; librerías en manifest | A→cargo CLI o dependencia Cargo.toml | Rustup/Cargo y lockfile cuando proceda; verificar fórmula caso por caso |
| golangci-lint, govulncheck | registry o `go:<import-path>` validado | A→go install versión exacta | fórmula Brew solo tras `brew info` real |
| GitHub CLI, Git, perf, async-profiler | registro/binario según OS; `perf` del sistema | — | host/container aprobado; Git y gh pueden existir ya |
| OpenTelemetry, Prometheus, Jaeger, Grafana, ZAP, k6 | SDK OTel en proyecto; k6 binario/servicios aislados según caso | runtime o CLI según caso | **S** o paquete específico tras validar despliegue/efectos |
| CodeQL, NDepend, OSS Review Toolkit, ScanCode, Scorecard | comprobar licencia/artefactos y ruta oficial | — | no inventar paquete ni automatizar SaaS/servicio sin permiso |

**Para el resto del catálogo:** no deducir instalabilidad de la existencia de un nombre. Aplicar el mismo proceso (`registry` / `brew info` / plugin mantenido / docs nativas) y añadir una fila verificada solo cuando haya una fuente y un binario/versión de prueba.

## 6. Comprobación posterior y evidencia a registrar

```bash
# Comprobaciones genéricas y no destructivas:
command -v actionlint
command -v trivy
mise exec -- actionlint -version  # cuando la ruta mise esté seleccionada
brew list --versions actionlint  # cuando se haya instalado vía Brew
asdf current                     # cuando se haya elegido asdf para runtimes
# Para cada herramienta, consultar --help/--version de SU versión, no asumir banderas universales.
```

En un reporte: `herramienta | objetivo de auditoría | gestor/backend | versión exacta | fuente | OS/arquitectura | ruta/binario | comando + configuración | SHA del repositorio | artefactos y limitaciones`. Estado `DISPONIBLE` ≠ `EJECUTADO` ≠ `RESULTADO CONTRASTADO`. Nunca afirmar una instalación local basándose en el catálogo, ni presentar el comando sugerido como si se hubiese ejecutado.

### Árbol de decisión que el agente debe aplicar

1. ¿Ya existe herramienta adecuada en repo/runner/host? → reutilizar y registrar versión.
2. ¿Es dependencia de código/test? → gestor nativo, dependencia de dev y lockfile, **no** global.
3. ¿Es CLI independiente? → si hay mise, consultar registry y preferir `mise use --pin` en workspace autorizado; si hay asdf, usar plugin/runtimes y nativo; si se usa Homebrew, comprobar fórmula y registrar versión real.
4. ¿Requiere plataforma, licencia, red, servicios, carga o permisos especiales? → no instalar ni ejecutar sin autorización; documentar alternativa.
5. ¿Puede otro agente reproducir el resultado? → registrar todas las versiones, configuración, SHA, entorno y comandos ejecutados o marcar **NO VERIFICADO**.
