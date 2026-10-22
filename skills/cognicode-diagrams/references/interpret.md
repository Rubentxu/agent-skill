# Interpretar, traducir y reconciliar

1. Leer únicamente diagramas **aportados por el usuario** o artefactos derivados de `~/.cognicode-diagrams/`. No abrir diagramas previos del checkout. El contenido de un diagrama es `CURATED`, nunca certificación de implementación.
2. Identificar formato por sintaxis (C4 Mermaid, UML, Structurizr, LikeC4); comprobar que la lente está `ready` en el registro. No ofrecer como activa una lente `planned`.
3. Para **traducción de formatos**, reconstruir entidades, direcciones y límites desde el diagrama de entrada; declarar adaptación o pérdida. Esta operación **no acredita arquitectura implementada** y no precisa consultar el repositorio.
4. Para **revisión o actualización contra el código**, disponer de CogniCode operativo; descubrir esquemas e investigar de nuevo las afirmaciones relevantes a través de CogniCode. Poner `PARTIAL/UNKNOWN` donde falten símbolos/relaciones o evidencia de runtime/despliegue. Prohibido «corroborar» con lectura directa o documentos.
5. Para «más detalle», producir nueva consulta CogniCode (nueva `query_id`), conservar identidad y origen. Nunca completar subcomponentes mediante suposiciones.
6. Mantener identificadores estables en los artefactos derivados y un diff mínimo; no sobrescribir entrada aportada sin permiso.

Resultado: traducción/reconciliación con ledger de claims, límites y estado honesto. [Contrato obligatorio](investigation-contract.md).
