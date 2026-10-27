# Ontología mínima del trabajo funcional

| Nombre | Definición operativa | Anti-concepto común |
|---|---|---|
| Concepto de dominio | Término que explica una decisión o dato del negocio | Nombre técnico de tabla/clase inferido como verdad |
| Invariante | Propiedad que todo estado válido satisface | Assert arbitrario que replica código |
| Producto | Varios hechos simultáneos (Rust struct; Kotlin data class) | Fila con campos opcionales inconexos |
| Suma/ADT | Una alternativa entre estados explícitos (Rust enum; Kotlin sealed) | `status:String` con combos de flags |
| Smart constructor | Creación que valida una precondición | Constructor público que permite datos inválidos |
| Transition | `State × Command × Context -> Result<Decision, Error>` | Llamadas a la BD dentro de una condición de negocio |
| Decision | Nuevos hechos/acciones requeridas sin interpretarlos todavía | Ejecutar IO antes de validar una regla |
| Effect handler | Interpreta instrucciones externas y traduce errores técnicos | Reglas de dominio escondidas en un adaptador |
| Slice | Flujo completo de una capacidad con dueños claros | Agrupación artificial de archivos por tecnología |
| Bounded context | Ámbito donde un término y sus reglas tienen significado consistente | Entidad universal compartida en toda la organización |
| Lens (skill) | Guía de decisión consultada por el agente | `Lens<S,A>` (optic funcional) |
| Lens (optic) | Abstracción de acceso/actualización de un campo | Obligación de introducir Arrow o librería óptica |

El núcleo puro decide; la capa de infraestructura observa/aplica. No usar "functional core" como excusa para mover responsabilidades al módulo `common` o recrear un orquestador central.
