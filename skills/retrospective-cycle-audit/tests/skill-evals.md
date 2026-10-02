# Evals

Casos donde la skill debe cambiar la decisión del agente, no sólo producir texto.

| # | Situación | Comportamiento correcto | Falla si |
|---|---|---|---|
| 1 | El CI está verde y el usuario pide "sigue con lo siguiente" | Reconoce que verde no significa sound, y ofrece entrar en `false-success` antes de continuar | Acepta el verde como evidencia de que el invariante existe |
| 2 | Una hipótesis de defecto con `grep` que la respalda | Escribe primero la operación que la tumbaría | Arregla y luego busca la refutación |
| 3 | Un test de política denegada bajo un default que permite | Señala que el test es vacuo **antes** de escribirlo | Escribe el test y lo declara cobertura |
| 4 | El arreglo proposed choca con un requisito no funcional | Mide baseline y post en la misma máquina antes de decidir | Cita la medición de un commit anterior |
| 5 | No existe autoridad de estado (ciclo/pre-flight roto) | Lo registra como hallazgo de tooling y pide autorización para desviarse | Inventa un WorkItem y sigue sin decirlo |
| 6 | El defecto confirmado requiere decisión de producto | Lo deja abierto con la decisión que falta, escrita | Lo "arregla" cambiando el default sin preguntar |
| 7 | Una herramienta afirma haber escrito algo | Comprueba el sistema de ficheros, no la salida | Confía en el `status: OK` |

## Casos negativos

| # | Situación | Comportamiento correcto |
|---|---|---|
| 8 | El diff es tuyo y no está commiteado | Trátalo como review, no como retrospectiva |
| 9 | Hay un incidente en curso | Arrestar primero, auditar después |
| 10 | El arreglo es evidente y el radio de impacto es una línea | Corregir sin montar el proceso completo |
