# Lente: instalación real del consumidor

1. Obtener un paquete **de los mismos bytes** que se van a distribuir (preferiblemente descargar el asset remoto) y verificar digest. Probar en entorno aislado fuera del checkout y de cachés del build.
2. Instalar y lanzar `version`, `--help`/`doctor` y una operación de negocio/CLI real; comprobar exit, stdout/stderr, efectos y errores, no solo un archivo existente.
3. Declarar OS/CPU/runtime probado; distinguir JVM externa, app autocontenida y binario nativo. No afirmar compatibilidad multiplataforma tras Linux solamente.
4. Probar updater/rollback y plugins externos si son promesas del producto. Escalar HF/restart/sandbox al certifier normativo, sin retener UAT efímeros permanentemente por defecto.
5. Identidad `source SHA → version → artifact digest → invocación → resultado`. Sin entorno compatible: NOT_RUN/BLOCKED, no PASS.

**Salida:** evidencia de usuario final sobre candidato exacto, limitaciones explícitas.
