# EJEMPLO DIDÁCTICO — repositorio ficticio (NO es una auditoría real)

El proyecto ficticio `sample-orders` declara en `docs/architecture.md` que el módulo `domain` no debe importar adaptadores de persistencia. En un diff **inventado**, `src/domain/order_service.py:14` contiene `from infra.postgres import OrderRow`. Esta información es una *fixture*, no evidencia sobre ningún repositorio real.

### H-01 — Dependencia directa del dominio hacia adaptador SQL

**Severidad:** MEDIA — infringe un límite expresamente declarado en el ejemplo y obliga al dominio a conocer el adaptador; la severidad real requeriría estudiar los consumidores afectados.

**Ubicación:** `src/domain/order_service.py:14`, `OrderService`; `src/infra/postgres.py` (ambas rutas ficticias).

**Evidencia:** `CÓDIGO` ficticio `from infra.postgres import OrderRow` + norma ficticia `docs/architecture.md`; **NO EJECUTADO:** no se ha construido ni probado el paquete. Para una auditoría real, adjuntar SHA, ruta:línea, manifest y regla aplicada y comprobar imports indirectos/DI.

**Impacto:** POTENCIAL — un cambio en el modelo SQL puede forzar cambios en contrato de dominio. No se afirma que haya causado un fallo observado.

**Recomendación:** investigar si el uso puede sustituirse por un tipo interno, adaptando la persistencia en su borde. Criterio de cierre: test arquitectónico que prohíba `domain → infra` y tests focales de mapping, ejecutados y vinculados al SHA nuevo.

### No-hallazgo demostrativo

«No existe tracing porque `grep OpenTelemetry` no devuelve resultados» **no es válido**. La revisión ha buscado una cadena, no el comportamiento observable. Formular la necesidad operacional, identificar otras implementaciones y medir una ejecución de diagnóstico antes de declarar un problema.
