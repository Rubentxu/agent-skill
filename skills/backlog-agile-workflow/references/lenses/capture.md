# Capture — de idea a registro verificable

1. Buscar duplicados `backlog search "término" --json` y revisar entradas; no crear varias tareas para el mismo resultado.
2. Determinar si es idea no refinada, decisión de arquitectura, bloqueo o incremento de valor. Idea incierta → `backlog draft create "..."`; decisión → `backlog decision create "..."` si el usuario lo autoriza; trabajo listo para refinar → tarea.
3. Escribir título orientado a resultado, una descripción que explique por qué, criterios de aceptación observables; una tarea por capacidad. No fabricar story points, deadlines ni responsables.
4. Evitar flags status/priority/project si no están configurados. No confundir `--ref` con `--doc`; sólo registrar enlaces existentes.
5. Confirmar IDs devueltos por CLI y reconsultar con `task view --json`. No construir IDs por secuencias inferidas.

**Anti-patrón:** convertir «moderniza la aplicación» en 30 tickets sintácticos sin usuarios ni contratos. **Resultado:** un borrador o tarea mínima con incertidumbre explícita.
