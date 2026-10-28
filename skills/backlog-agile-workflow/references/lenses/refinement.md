# Refinement — tarea vertical, aceptación y plan justo a tiempo

1. Escoger un caso de uso y declarar un resultado usable. Descomponer horizontalmente por capas solamente si hay una frontera verificable e independiente; no tickets «crear DTO», «crear trait» sin valor.
2. Criterios de aceptación con entrada, comportamiento y resultado; cubrir rechazo esperado, compatibilidad y errores cuando proceda. Evitar AC tautológicos «debe funcionar».
3. Definir DoD con la **configuración existente**, no un checklist nuevo que multiplique tests. Separar AC (qué entregar) de DoD (calidad del proceso).
4. Crear dependencias solo si un entregable bloquea otro; verificar IDs reales. Evitar dependencia especulativa y cascadas por carpetas.
5. Planificar **just-in-time** después de observar código, límites e invariantes: `backlog task edit <id> --plan "..."` con autorización. Si hay dudas relevantes, documentarlas en comentario y no comprometer una implementación imaginaria.

**Salida:** objetivo, 2–5 AC discriminantes cuando convenga, primer slice, dependencias reales, hipótesis, decisión `READY/INSPECT_MORE`.
