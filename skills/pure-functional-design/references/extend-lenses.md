# Añadir y retirar lentes

1. Identificar una pregunta nueva no contestada por las lentes `ready`.
2. Establecer señales observables, precondiciones, no aplicabilidad y coste incremental.
3. Escribir procedimiento numerado reproducible, resultado verificable, anti-patrones y un caso adversarial.
4. Registrar con `status=planned`; probar router (selección positiva, negativa y conflicto con otra lente).
5. Probar la lente contra al menos dos slices reales de lenguajes diferentes cuando sea transversal, y un contraejemplo donde **no** debe actuar.
6. Promocionar `ready` solo con guía completa, rutas válidas y evaluación; eliminar la lente si ninguna decisión diferencial justifica su coste.

No agregar un motor de reglas genérico, una taxonomía extensa o un DSL de HKT antes de medir un problema real. Preferir ampliar guías existentes antes de duplicarlas.
