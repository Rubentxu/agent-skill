# Lente: diagnóstico diferencial por problema

**Pregunta:** ¿qué evidencia demuestra el problema, qué alternativa es mínima y cuándo conviene mantener el código actual?

## Algoritmo

1. Partir de un caso de uso observable y fijar revisión, firma, consumidores y garantía. No convertir un nombre de clase, cantidad de LOC o cantidad de `mut` en causa probada.
2. Separar **síntoma** (`large-service`), **mecanismo causal** (p. ej. reglas con propietarios diferentes en una transacción) y **problema** en `../problems.json`.
3. Para afirmar `OBSERVED`, registrar al menos una prueba concreta `{source, observation}` (ruta, símbolo, trace, resultado de test u observación real). De lo contrario, etiquetar `INFERRED` y pedir inspección.
4. Enumerar al menos tres opciones cuando sea útil: `KEEP_AS_IS`, mejora local y transformación de `../recipe-registry.json`. No elegir una por parecerse a Haskell.
5. Aplicar contraejemplos del catálogo: un bucle simple, código cohesionado, DTO deliberadamente permisivo o políticas distintas NO exigen un refactor.
6. Refutar hipótesis causales con consumidor inverso, invariante y frontera transaccional. Si no se dispone del código, abstenerse.
7. Proponer la transformación viable más pequeña, con coste, riesgos, precondiciones faltantes y punto de reversión. El router solo propone: no certifica ni ejecuta.

**Salida:** `problema | evidencia | hipótesis rival | alternativas | decisión APPLY/INSPECT_MORE/KEEP_AS_IS/BLOCKED | razón | siguiente observación`.

**Contraejemplo:** una clase de 800 LOC que encapsula un algoritmo cohesionado no se parte por longitud; un bucle claro no se convierte en `fold` para satisfacer un estilo.
