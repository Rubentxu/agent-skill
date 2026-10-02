# Evals

| # | Situación | Comportamiento correcto | Falla si |
|---|---|---|---|
| 1 | Un enum de 13 acciones, 4 puntos de evaluación | Tabla de intersección, y nombra los 3 inertes con su sitio esperado | Acepta que "el motor los soporta" |
| 2 | Un inerte cuyo default concede | Lo clasifica FALSO CONTROL y dice que bloquea una release | Lo registra como deuda |
| 3 | Un UAT describe una amenaza sobre la ruta "equivalente" | Comprueba si la ruta equivalente **tiene** el campo; si no, dice que el UAT apunta a la ruta imposible | Da el UAT por cubierto porque el nombre coincide |
| 4 | Un allowlist de `host` con `host_addr` libre | Señala que el par no está atado y que el control pasa pruebas y no cierra el agujero | Da el arreglo por bueno |
| 5 | Un script extractor dice "todos vivos" | Verifica contra un árbol donde se sabe que hay uno muerto, antes de confiar | Reporta el verde sin refutar |
| 6 | La configuración por defecto no declara nada | Lo trata como posición válida que niega todo | Lo trata como "aún sin configurar" y permite |
| 7 | Una petición malformada recibe un error de configuración | Lo marca: el orden sintaxis→configuración está invertido | Lo acepta como un detalle de redacción |

## Casos negativos

| # | Situación | Comportamiento correcto |
|---|---|---|
| 9 | PR pequeño que no toca el vocabulario ni defaults | Aplazar la auditoría; el coste no se paga solo |
| 10 | Sistema sin motor de políticas (validador, parser) | Adaptar el razonamiento, bajar severidad: no hay política que el operador escriba |
