# Evaluaciones de activación y comportamiento

## Positivos — debe activar

### P1 — adopción tecnológica

**Prompt:** “Necesito entender Temporal a fondo antes de decidir si encaja como motor de workflows durables. No quiero un resumen comercial: quiero conceptos, arquitectura, lifecycle, fallos y trade-offs.”

**Esperado:** activar; `scope` primero si no hay criterio de decisión suficiente y luego perspectivas con énfasis `product/process`; evidencia primaria y modelos.

### P2 — aprendizaje para ingeniería

**Prompt:** “Aprende WebAssembly Component Model para que podamos integrarlo en nuestro runtime. Quiero saber qué problema resuelve, conceptos, componentes, interfaces, estados y qué no entendemos todavía.”

**Esperado:** activar; 7P + fichas + modelos conceptual/estructural/dinámico + gaps.

### P3 — enseñanza técnica

**Prompt:** “Quiero preparar un curso serio de Kubernetes que explique por qué funciona, no sólo kubectl. Necesito ordenar conceptos, arquitectura, procesos y comportamiento.”

**Esperado:** activar; objetivo/audiencia explícitos y cobertura equilibrada de las tres perspectivas.

## Negativos — no debe activar

### N1 — consulta factual breve

**Prompt:** “¿Qué puerto usa PostgreSQL por defecto?”

**Esperado:** no activar; una investigación MOSAT sería desproporcionada.

### N2 — troubleshooting puntual

**Prompt:** “Mi pod está en CrashLoopBackOff, ayúdame a diagnosticarlo.”

**Esperado:** no activar por defecto; usar diagnóstico operativo salvo que el usuario pida aprender/modelar Kubernetes como objetivo.

### N3 — tutorial directo

**Prompt:** “Dame un ejemplo mínimo de docker-compose con Postgres y Redis.”

**Esperado:** no activar; el usuario pide una receta, no comprensión sistémica.

## Ambiguos — debe acotar antes de profundizar

### A1 — “investiga X”

**Prompt:** “Investiga Nix.”

**Esperado:** puede activar sólo en `scope`; debe determinar propósito, profundidad y entregable antes de producir una investigación extensa.

### A2 — comparación de tecnologías

**Prompt:** “¿Kafka o NATS para eventos internos?”

**Esperado:** activar si la decisión requiere comprensión arquitectónica; estudiar sólo las propiedades que cambian la decisión, no ejecutar MOSAT exhaustivo para ambas.

## Invariantes de calidad

1. No presentar `confidence`, estados de gap o niveles de profundidad como elementos originales de MOSAT.
2. Mantener visibles hechos, inferencias, supuestos y desconocidos.
3. No cerrar una ficha crítica sin fuente cuando la fuente primaria sea accesible.
4. Un modelo debe enlazar a conocimiento de las fichas; no generarse sólo por plausibilidad.
5. La siguiente iteración debe estar guiada por gaps de impacto, no por una lista arbitraria de más fuentes.
