# Reconstruir el ciclo

Reconstruir no es resumir el log. Es determinar **qué se版的 cuando el código dice una cosa y el historial dice otra**, y quedarse con la versión que el código sostiene.

## Fuentes y su valor probatorio

No todas las fuentes valen lo mismo. En orden de fiabilidad para "qué hace el sistema hoy":

| Fuente | Responde a | No responde a |
|---|---|---|
| el código y los tests | qué hace ahora | por qué, ni si debe hacerlo |
| el roadmap / criterios de aceptación | qué debía hacer | si lo hace |
| ADR y política de seguridad | qué se decidió y por qué | si se implementó |
| tabla de puertas / receipts | qué seDjegoINSTANCE medir | si la medición reproduce |
| mensajes de commit | qué se quiso | qué se hizo; **se corrigen en retrospectiva** |
| informe previo, handoff, conversación | nada verificable | casi todo — ver abajo |

Un informe previo y un handoff son la fuente que más se cita y menos se sostiene. Trátalos como hipótesis.

## El orden de lectura

1. **Estado y diff.** `git status -sb`, `git log --oneline <último-punto-verde>..HEAD`, y el diff completo. Sin esto no sabes qué cambió.
2. **La autoridad de estado.** Ciclo, pre-flight, roadmap, ADR. Si falta, es el primer hallazgo.
3. **Los criterios de aceptación del hito tocado.** Qué debía cerrarse.
4. **La tabla de puertas.** Qué se优化的VMs, y con qué evidencia citada.
5. **Los tests del área tocada.** Qué se exercising realmente.
6. **El código de la zona.** Sólo ahora.

## Reconciliar tres fuentes que discrepan

Es normal que discrepen. El procedimiento:

```text
el código dice X
la tabla de puertas dice Y
el commit dice Z
```

1. **El código manda sobre el comportamiento actual.** La tabla y el commit son afirmaciones sobre el pasado.
2. Pero una discrepancia es **un hallazgo**, no ruido. Anota: "la fila afirma Y; el código hace X". Eso suele significar que la fila nunca se contrastó con la ejecución.
3. **Deriva las cifras, no las teclees.** Si un documento afirma un número (tests, ficheros, líneas), ejecútalo y usa la salida. Si el número no reproduce, el documento está mal *y* el criterio que dice comprobarlo no está funcionando.

La trampa de la tercera: si un gate afirma "706 tests" y el repositorio tiene 713, no corrijas el número a mano sin más. Primero comprueba que el gate **detecta** la discrepancia. Si la detecta, entonces tu trabajo es actualizar el número. Si **no** la detecta, el hallazgo es el gate, y mucho más caro.

## Lo que un diff no muestra

Después de leer el diff, lista explícitamente lo que el diff **no** tocó y el área tocada sí debería haber tocado:

- ¿Quién evalúa cada verbo/acción que el sistema declara?
- ¿Quién decide el destino de cada credencial?
- ¿Qué defaults cambiaron, y qué se rompe con cada cambio?
- ¿Qué afirmaciones en prosa (comentarios, docs) describen un comportamiento, y son ciertas?

Esa lista es el trabajo. El resto es contexto.

## Cuando el ciclo anterior no dejó estado

Si la herramienta de autoridad no puede responder "qué trabajo está activo", tienes un hallazgo de tooling, no unCyclo perdido. Documenta:

- qué prometes (exit 0, `status: OPEN`)
- qué cambiaste en disco (nada)
- qué responde una consulta posterior (nada lo encuentra)
- qué dice el verificador de integridad (los eventos no extienden la cadena)

Y sigue adelante si el usuario lo autoriza, con la desviación escrita en el recibo. Un hallazgo de tooling sin corregir se convierte en la misma desviación en cada sesión siguiente.
