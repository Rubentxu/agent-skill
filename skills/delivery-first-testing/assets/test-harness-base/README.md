# Test Harness Base — plantilla, no framework nuevo

La skill incluye una **plantilla portable** para copiar al proyecto cuando este no tenga ya una base equivalente. No se instala automáticamente ni redefine CI. Ubicar en `test-harness/` o `v2/test-harness/` según el proyecto; preservar los comandos oficiales de Gradle/Cargo/just/PipelineK. Usar adaptadores de navegador, API, gRPC y Podman solo cuando la feature los requiera, sin crear suites permanentes por cada escenario.

```bash
cp -R skills/delivery-first-testing/assets/test-harness-base ./test-harness
TH_TARGET_ID=<sha-o-digest-real> bash test-harness/examples/cli-version.sh ./dist/product --version
```

El **harness** (`lib/harness.sh`, helpers y perfiles que se añadan) queda versionado. Cada ejecución crea `test-harness/.sessions/run.XXXXXXXX` con permisos restrictivos y logs aislados; se conserva localmente un recibo bajo `.reports/` (ambos ignorados por Git) y se destruye la sesión al salir, incluido fallo/INT/TERM. Se exige `TH_TARGET_ID`, proporcionado por el agente tras verificar la procedencia real del artefacto; la variable **no certifica por sí misma** esa procedencia.

## Interfaz de la biblioteca

- `th_init`: habilita sesión y trampas de limpieza; necesita `TH_TARGET_ID` y GNU `timeout`.
- `th_capture nombre comando ...`: ejecuta sin shell interpolado, con límite `TH_TIMEOUT_SEC` (60 s por defecto), guarda salida y propaga exit != 0. Una salida cero sin aserción adicional no acredita semántica.
- `th_assert_nonempty archivo` / `th_assert_contains archivo texto`: condiciones explícitas, fail-closed.
- `th_wait_until segundos comando ...`: polling por condición con plazo límite, no espera fija como test.
- `th_start_service nombre comando ...`: inicia en un grupo propio (`setsid`) y registra PID para detenerlo al cerrar. Linux requerido para este adaptador.
- `th_register_container podman|docker id`: **registra solo contenedores exclusivos de esta sesión** para `rm -f` en cleanup; no mata recursos compartidos ni hace `pkill` global.

La prueba efímera puede repetir ejecuciones durante la feature, pero su **código no sobrevive al cierre** salvo decisión `PROMOTE/REPLACE`. Guardar aceptación primero en el sistema existente del proyecto. Para inspeccionar fallos usar `.reports/` local; examinar/redactar logs antes de compartir: pueden contener secretos o datos privados. No promover logs a Git. No compartir perfiles con estado mutable, procesos vivos o puertos estáticos entre sesiones.

La plantilla no garantiza limpieza de recursos no registrados ni implementa drivers complejos por defecto. Un adaptador real debe registrar contenedores/grupos **en cuanto se crean**, verificar su apagado y usar `--rm` cuando sea posible. Si no hay runner o identidad verificable, el resultado es `BLOCKED`, no `PASS`.

## Comprobación de la propia plantilla

```bash
bash skills/delivery-first-testing/tests/test_harness.sh
```

Prueba el éxito, propagación de fallo, identidad obligatoria y limpieza de grupos en un directorio temporal. No arranca Podman ni requiere instalaciones nuevas.
