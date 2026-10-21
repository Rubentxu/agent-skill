# Lente: UAT/E2E efímero de un ciclo con Harness Base

**Pregunta:** ¿puede el consumidor utilizar ahora la feature en el artefacto correcto, sin acumular una suite permanente?

1. Extraer criterios de aceptación observables. Elegir la menor frontera real: binario CLI, API, gRPC, navegador o instalación. Verificar la identidad del binario/HEAD antes de contar evidencia.
2. **Reutilizar el harness del proyecto** (`test-harness/` o `v2/test-harness/`). Si no existe, adaptar la [plantilla portable](../../assets/test-harness-base/README.md); no introducir un segundo framework de tests ni mover infra operativa al repo de la skill.
3. Reutilizar drivers, fixtures, perfiles, aserciones, observabilidad y limpieza; **crear solamente escenarios específicos de la feature**, en `.sessions/` ignorado por Git o en `mktemp` externo. Los escenarios son repetibles durante el ciclo, no necesariamente una sola ejecución.
4. PREPARE: entorno aislado y datos exclusivos, puertos dinámicos, servicios identificados, timeout. EXECUTE: ejecutar binario/servicio real. ASSERT: resultados públicos y negativos discriminantes, esperas condicionadas (no sleeps fijos). EVIDENCE: guardar resultado, ID de sesión, SHA/digest, fallos, skips y cobertura efectiva. CLEANUP: procesos/grupos/contenedores que pertenezcan a la sesión, también tras fallo/señal.
5. Si el UAT detecta defecto, reproducir/corregir/revalidar antes de cierre. Decidir `PROMOTE | REPLACE | RETIRE | DEFER` por garantía y registrar primero la evidencia. Retirar scripts efímeros al finalizar el bloque, nunca eliminar el harness ni garantías críticas sin protección equivalente.

**Contrapruebas:** sin navegador/herramienta o artefacto vigente → `BLOCKED`; shell sale 0 antes de aserción → falso verde; un proceso huérfano o fixture contaminado → no dar por completo el cierre. No conservar secretos, datos personales ni logs sensibles. Sesiones distintas no comparten estado mutable.

**Cierre:** aceptación observada por escenario, artefacto vigente, ciclo de limpieza verificado y decisión de regresión. Un UAT no sustituye tests de contrato de protocolo o persistencia si son garantías distintas.
