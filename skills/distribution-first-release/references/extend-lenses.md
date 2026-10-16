# Autodescubrimiento y extensión responsable de lentes

No crear una lente solo por el nombre de una herramienta. Detectar repetidamente un **hueco de decisión** que no cubran las lentes existentes (p.ej. registry con POM/sources requeridos, OCI multiarch o firma platform-specific).

1. Formular pregunta y señales observables; documentar qué decisiones cambia.
2. Comparar con lentes existentes y con reglas normativas del proyecto: ampliar una ya existente antes que duplicar.
3. Declarar `status: planned` y enlazar provisionalmente este documento. No anunciarla como ejecutable.
4. Añadir playbook `references/lenses/<id>.md` con acciones read-only, límites, requisitos, casos adversariales y evidencia.
5. Añadir 2 escenarios positivos, 1 contraejemplo y tests de router para activación y ausencia de falsos verdes.
6. Solo entonces cambiar a `ready`. Mantener la semántica `application` distinta de `library/sdk`.
7. Retirar o fusionar lentes que no aporten decisiones nuevas; no crear otro framework CI, servicio, MCP, plugin o autoridad paralela.

Futuros candidatos: `registry-contracts` (Maven/Nexus/npm/crates y fuentes exigidas), `native-packaging` (JLink/jpackage/Rust/Go, ABI, librerías del SO). Ambos están **planned** y no son funciones disponibles hoy.
