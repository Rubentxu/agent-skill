# Lente: composición de artefacto distribuible

1. Construir desde SHA autorizado sin renombrar ZIP de otra versión. Inspeccionar contenido ZIP/TAR/OCI y comparar contra contrato de instalación, no únicamente extensión del archivo.
2. Bloquear rutas absolutas, `..`/Zip Slip, `.git/`, `src/test/`, `tests/`, secretos, credenciales, reportes internos y dumps de workspace. No excluir recursos del runtime (`META-INF/services`, configuraciones, licencias, JARs compilados).
3. Verificar entrypoint, permisos, dependencias y plataforma; distinguir JDK externo de runtime incorporado. Una app que no arranca no es producto usable.
4. Para CLI real exigir `version` + `help/doctor` + una acción funcional, preferiblemente desde entorno limpio; la mera presencia de `bin/` no basta.
5. Los símbolos/debug/docs se publican por separado solo cuando el consumidor los necesita.

**Salida:** estructura real, dependencias, tipo, SHA y prueba de ejecución o NOT_RUN.
