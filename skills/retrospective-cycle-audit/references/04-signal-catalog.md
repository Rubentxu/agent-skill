# Catálogo de señales

Dónde mirar primero, ordenado por el coste de encontrar el hallazgo. Cada señal dice cómo se **busca**, no sólo qué es.

## 1. Vocabulario declarado que nadie evalúa

**La señal más cara de este catálogo.** Un sistema que declara un vocabulario (acciones, verbos, permisos, roles, destinos, puertos) y un motor que lo evalúa: cada elemento del vocabulario debería ser construible desde el código de producción. Si no lo es, es decorativo.

```bash
# ¿cada acción declarada se construye en producción?
grep -rn "Action::" src/ --include=*.rs | grep -v "/tests/" | grep -v "src/lib.rs:.*=>" | sort -u
```

Compara con el `match` que mapea cada variante a su nombre, y con las reglas del motor. Lo que aparezca **sólo** en el mapeo, **sólo** en las reglas, o **sólo** en tests, es vocabulario muerto.

Aparece en: pasarelas de autorización, listas de roles, esquemas de permisos,catálogos de conectores, tablas de códigos de error, vocabularios de un ADR.

## 2. El destino lo elige el solicitante

Si una credencial se presta a algo, y el *destino* de esa cosa viene en el request, entonces el solicitante elige adónde va la credencial. Busca campos de destino (`host`, `addr`, `url`, `endpoint`, `audience`, `target`) en las peticiones, y comprueba si el recurso de política los incluye o no.

El sub-tipo peligroso: el allowlist está sobre un campo pero **otro campo del mismo par no está atado**. Un allowlist de `host` con un `host_addr` libre sigue siendo un agujero, porque el solicitante conserva el nombre y cambia la dirección.

## 3. Comentarios que afirman invariantes

```bash
# comentarios que promising que algo ocurre en otro sitio
grep -rniE "happens (here|later|below|downstream)|is checked|still happens|re-checked|before this" src/ --include=*.rs
```

Cada uno es una afirmación verificable. Verifícala. Un comentario que promete una comprobación inexistente es **el hallazgo más caro del catálogo**, porque un revisor no tiene nada que revisar: no hay diff, no hay rama, no hay llamada. Y sobrevive ciclos porque nada lo contradice.

## 4. Defaults que conceden

Un default que concede hace que toda prueba negativa sea vacua, y hace que un usuario que no leyó la configuración create que tiene un control que no tiene.

```bash
# qué conceden los defaults?
grep -rniE "fn default|impl Default" src/ --include=*.rs | head -40
```

## 5. Errores mal tipados

Un error que se mapea a un código que no describe lo que pasó. Señal concreta: un `match` de error donde dos casos distintos caen en el mismo código "para simplificar". Y su gemelo: un código que un cliente no puede distinguir entre "nunca existió" y "ya no existe" — a veces es deliberado (anti-enumeración), y entonces debe estar escrito por qué.

## 6. Ramas sin cubrir

```bash
# arms de match que ninguna prueba alcanza
# pista: un enum con un _ => catch-all, o un match sin exhaustividad forzada
grep -rn "_ =>" src/ --include=*.rs | grep -v "/tests/" | head -30
```

Un `_ =>` en un match de **seguridad** es un default-deny disfrazado de atajo. En un match de **errores** suele ser un fallo silencioso.

## 7. Responsabilidades solapadas

Dos módulos que responden a la misma pregunta, y no necesariamente igual. Señal: un comentario "same shape as X, and for the same reasons" seguido de una copia. Y su inversa: una función que **debería** ser compartida y está duplicada tres veces con tres redactos.

## 8. Duplicidad con divergencia

```bash
# misma constante o allowlist declarada en más de un sitio
grep -rn "\"api\.github\.com\"\|\"api.github.com\"" src/ --include=*.rs
```

## 9. La claim que se contradice a sí misma

En documentación y cabeceras: una línea que declara un identificador y cuatro líneas después lo descarta. En un fichero de test, una cabecera que reclama algo que el fichero no ejercita.

```bash
# cabeceras que declaran un identificador
grep -rn "^//!.*[A-Z]\+-[0-9]\{3\}" --include=*.rs .
```

Y después: ¿el fichero realmente hace eso?

## 10. Números afirmados sin derivar

Ficheros de test contados a mano, líneas de código, "N de M", porcentajes. Derivarlos:

```bash
grep -c "#\[test\]\|#\[tokio::test\]" src/lib.rs     # y comparar con lo que el doc afirma
cargo test --workspace --locked -- --list | grep -c ": test"
```

## Cómo ordenar el trabajo

No todos los hallazgos valen lo mismo. Puntúa por **impacto × probabilidad × alcance** frente a **coste de verificar**:

- Un vocabulario muerto en una pasarela de autorización: impacto alto, y el coste de verificarlo es un `grep`. Va primero.
- Una rama sin cubrir en un parser: impacto medio, coste medio.
- Una cifra en un documento: impacto bajo, coste el de derivarla. Va al final, pero **se deriva**, no se teclea.
