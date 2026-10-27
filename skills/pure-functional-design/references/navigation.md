# Máquina de decisión y navegación sin HTTP

El router no ejecuta operaciones: produce `{rel, href, why}` locales, sin acceso automático a Git ni ejecución de compilers. Los flags `observed` provienen del usuario/agente y **no** están certificados por el helper.

## Entrada

```json
{
  "intent": "refactor",
  "language": "rust",
  "basis": "observed",
  "signals": ["large-service", "side-effects", "invalid-state"],
  "risk": "high"
}
```

- `intent`: `catalog|discovery|design|implementation|refactor|review`.
- `language`: `rust|kotlin|other|unknown`.
- `basis`: `observed|unknown|stale` para revisión y señales de código (no garantiza que exista grafo CogniCode).
- `signals`: `domain-ambiguity|invalid-state|side-effects|large-service|duplicate-logic|complex-algorithm|nested-data|cross-context|legacy-test-coupling|unknown`.
- `risk`: `routine|high|critical`.

## Prioridades

1. `catalog`: listar lentes `ready` y `planned` explícitamente, sin pretender ejecutarlas.
2. `basis != observed`: `inspect-code` o `refresh-basis`, nunca recomendaciones como hallazgos confirmados.
3. `language == unknown`: `identify-language` antes de proponer syntaxis.
4. Sin señales: `discover-signals`, no seleccionar por moda.
5. Con evidencias: seleccionar hasta tres lentes metodológicas relevantes por `intent` y `signals` (prioridad de dominio y fronteras primero), más la lente de lenguaje si es `ready` y aplica.
6. Al terminar el análisis: `propose-slice` con alcance mínimo; si se implementa, `verify-contracts` con `delivery-first-testing` cuando corresponda.
7. Lente `planned` no se considera disponible; sin playbook, no hay acción ejecutable.

## Resultados de verdad

- `OBSERVED`: existe código/firma/ejecución cuya procedencia conocemos.
- `INFERRED`: hipótesis de dominio pendiente de confirmar.
- `NOT_RUN`: comandos, compilers, tests o probes no ejecutados.
- `BLOCKED`: falta permiso, herramienta, grafo o fuente.
- `STALE`: cambió el código o su entorno después de la observación.

No inferir una transición `PASS` del estado del router. El router es un recomendador, no certificador de refactors.
