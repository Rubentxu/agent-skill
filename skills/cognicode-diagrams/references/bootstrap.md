# Diagnóstico de CogniCode sin fallback de investigación

Solo se permite inspeccionar la disponibilidad de **CogniCode CLI/MCP** y su ayuda real. No revisar el checkout mediante Git, shell, Github ni otra utilidad. `command -v` / `type -a` sirven únicamente para localizar los binarios de CogniCode, no para extraer arquitectura.

`
command -v cognicode
command -v cognicode-mcp
command -v cogh
cognicode --help
cognicode capabilities --json
cognicode doctor
`

Las tres últimas órdenes solo deben ejecutarse si existen y la versión observada las admite. Descubrir los esquemas MCP mediante `initialize/tools/list` reales y paginar. Una documentación de instalación no acredita soporte runtime.

Instalación/actualización solo con permiso explícito, siguiendo el mecanismo de distribución de CogniCode correspondiente a la plataforma. **No abrir ni interpretar archivos internos del repo para compensar la falta del binario.** Si CogniCode no está disponible, marcar `BLOCKED`, indicar qué falta y cómo instalar/configurar; nunca buscar por otra vía.

La skill no instala, altera ni reconstruye CogniCode; sus proyectores tampoco lo invocan. [Contrato](investigation-contract.md).
