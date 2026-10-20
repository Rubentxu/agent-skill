# Lente: empaquetado y entrega

Por defecto, entregar **un HTML ejecutable directamente** con CSS/JS/SVG inline y assets embebidos correctamente cuando sea razonable, sin fuentes remotas, `fetch()` de CDNs ni dependencias invisibles. Para app existente respetar stack y generar build distribuible funcional. Separar los archivos de *desarrollo* en fuentes modulares y empaquetar al final, sin incorporar un bundler nuevo si no hace falta.

Verificar apertura en `file://` y sin red según navegador/entorno disponible; no prometer persistencia entre ubicaciones o navegadores, cuyos comportamientos varían. Comprobar tamaño/carga y degradación si datos/mapas son grandes. Preservar licencias y crédito para imágenes/mapas. Evitar fuentes, software o datos no redistribuibles.

Entregar HTML descargable y, cuando lo solicita el usuario o aporta valor, ZIP fuente con README. Nunca basta una captura ni diseño en Figma. Si navegador no está disponible, reportarlo, no afirmar «offline verificado».
