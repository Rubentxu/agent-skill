# Lente: documentar sin reescribir la autoridad

**Pregunta:** ¿Qué objetivos reales de ROADMAP/ADR/specs/gates deben existir como tareas?

1. **Seleccionar fuente canónica** (ROADMAP.md, docs/roadmap/, ADR, specs, estado y gates). No asumir que todos los markdowns tienen el mismo significado. Registrar revisión/versión si es observable. Si hay ZIP, inspeccionar entradas con seguridad antes de extraer fuentes; no inventar documentos.
2. **Distinguir tipos:** roadmap/hito = resultado y orden; SPEC = contrato y criterios; ADR = decisión/restricción, no tarea salvo acción explícita; GATE = condición de cierre y propietario de certificación, no checkbox automático; STATE/recibo = evidencia de pasado, no trabajo nuevo; BACKLOG.md existente = índice/objetivos si es canónico, no reemplazar por una segunda copia.
3. **Separar historial de intención:** un bloque CLOSED con recibo, tag y revisión es histórico, no se reabre. CLOSED en un documento sin evidencia sigue siendo una afirmación, no certificación. Una sección que dice "ya implementado" no obliga a crear trabajo; evaluar si queda gate o deuda pendiente.
4. **Extraer ficha de cada objetivo (sin tarea todavía):** referencia `ruta#ID`, hito, resultado observable para consumidor, alcance/no-alcance, dependencias, restricciones ADR, contrato SPEC, aceptación, DoD/gate, evidencia, estado declarado y preguntas. Preferir IDs estables explícitos (F2.W3, R4, H1, B3); no crear IDs a partir de posición de encabezados ni inventar significado de R1/R2.
5. **Revisar granularity:** hito = entrega usable; tarea = cambio revisable con única responsabilidad y criterio de salida. Un bloque puede contener varias tareas pero nunca convertir cada párrafo, prueba histórica o frase de una ADR en tarea. Para huecos de información, producir `INSPECT_MORE` o un spike timeboxed autorizado, no llenar supuestos.
6. Pasar de lectura a propuesta usando [proyección](spec-reconciliation.md) con `spec-packet` explícito; **no** editar documentos canónicos para acomodarlos a Backlog.md.

**Handoff:** paquete estructurado de objetivos, referencias, bloqueos y evidencias. Todas las decisiones que no son tareas permanecen como referencias a autoridad original. No hay una nueva ontología de estados de Backlog.md.
