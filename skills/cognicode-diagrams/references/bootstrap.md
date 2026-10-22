# Descubrir CogniCode sin suponer subcomandos

No existen comandos CLI obligatorios codificados en esta skill aparte de **consultar la ayuda real del ejecutable identificado**. La versión instalada decide si ofrece `capabilities`, `doctor`, `graph` u otra operación: **no invocar subcomandos heredados que no estén anunciados**.

1. Identificar la interfaz CogniCode CLI/MCP proporcionada por el usuario, sin leer archivos del checkout.
2. Solicitar ayuda/versiones con los flags que admita esa instalación. En MCP usar `initialize` y `tools/list` paginado con schemas efectivos.
3. Elegir una capacidad estructurada observada y probarla sobre un símbolo real **para el lenguaje del proyecto**. Registrar identidad, ubicación, contexto, relaciones, cobertura y omisiones.
4. Si la herramienta anunciada falla, anotar la limitación de esa capacidad y lenguaje, sin declarar incompatible todo Kotlin/Rust. Probar otra capacidad estructurada pertinente.
5. Si ninguna interfaz está disponible, `BLOCKED`. No suplir la carencia con shell, Git, documentos, indexadores externos ni lectura raw.

Instalar o modificar CogniCode exige consentimiento. Los proyectores no lo sustituyen y solo reciben artefactos derivados de HOME.
