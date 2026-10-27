# Lente Rust — semántica pura aprovechando el compilador

**Alcance:** Rust nativo; no emular Haskell con una jerarquía genérica de HKTs. Este perfil se combina con UNA lente metodológica.

## Herramientas idiomáticas

- **Suma:** `enum` con payload por variante y `match` exhaustivo; **producto:** `struct` con campos privados; smart constructors `Result<T, DomainError>`.
- `Option<T>` para ausencia y `Result<T,E>` para fallo. `?`, `map`, `and_then`, `map_err`, `collect::<Result<Vec<_>,_>>()` para composición clara.
- `Iterator`, `map`, `filter`, `flat_map`, `fold`, `try_fold`, `find`, `any`, `all`; evitar `.clone()` implícito en cada paso o colección intermedia por defecto.
- `From`/`TryFrom` para conversión de tipos en frontera. Traits solo para comportamiento intercambiable; `dyn Trait` cuando realmente haga falta dispatch dinámico.
- Ownership impide aliases mutables simultáneos; no equivale a pureza semántica si hay IO o `Mutex` global. `&mut Vec` local durante cálculo puede preservar pureza observacional si no fuga referencia ni efectos.
- Typestate cuando hay procesos lineales que deben impedir transiciones en compilación y no se serializan arbitrariamente. En workflows persistentes/event-sourced, generalmente enum de estado + transition function simplifica restauración.
- Fronteras: separa crates solo si tienen API, propietarios y usuarios independientes; primero un `mod domain`, `application`, `adapters` **dentro del slice** si eso basta.

## Algoritmo del perfil

1. Revisar `rust-version`, edition, layout y traits/imports ya usados. No asumir crates (`im`, `itertools`, `tap`, `derive_more`) sin evidencia.
2. Elegir estados/enums, errores tipados, `fn decide(&State,&Command,&Context)->Result<Decision,Error>` o ownership-by-value si más claro. No inyectar `&dyn Repository` en el core.
3. Optimizar semántica y asignaciones: para estructuras grandes devolver owned state o deltas/events según necesidades; `Arc` o copia persistente solo si hay fan-out real.
4. Efectos: invocar DB, fs, red, reloj en adapter y gestionar cancelación, retry, atomicidad y outbox si la garantía exige publicación duradera.
5. Asegurar compatibilidad `serde`/wire enums si existen; cambios de variante son cambios de contrato potencialmente breaking.
6. Verificar compilación y test rápido selectivo con los comandos propios del repo; si no corrió, `NOT_RUN`.

## Ejemplo breve

```rust
#[derive(Debug, Clone, PartialEq, Eq)]
enum State { Draft, Published { version: u64 } }
#[derive(Debug, Clone, PartialEq, Eq)]
enum Error { AlreadyPublished }
fn publish(state: &State) -> Result<State, Error> {
    match state {
        State::Draft => Ok(State::Published { version: 1 }),
        State::Published { .. } => Err(Error::AlreadyPublished),
    }
}
```

El core no abre archivos ni genera timestamps. Si `version` viene de otro agregado, cambiar el ejemplo: el estado mostrado es didáctico, no universal.

**Sources:** [Rust Book](https://doc.rust-lang.org/book/), [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/), [Rust Design Patterns](https://rust-unofficial.github.io/patterns/).
