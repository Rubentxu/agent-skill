# Estrategia de fuentes

## Prioridad

Busca primero la evidencia capaz de responder preguntas, no “todo lo que exista” sobre la tecnología.

Orden recomendado:

1. especificación, RFC, estándar o paper fundacional;
2. documentación oficial y documentación de arquitectura;
3. código fuente y tests cuando la semántica ejecutable importe;
4. papers académicos o whitepapers técnicamente relevantes;
5. documentación de proveedores/implementaciones;
6. ingeniería de terceros con reputación y evidencia;
7. comunidad, foros y experiencias de campo;
8. contenido introductorio sólo para navegación inicial.

Una fuente secundaria puede descubrir vocabulario o rutas, pero no debe sustituir una fuente primaria para afirmaciones fuertes cuando ésta existe.

## Organizar por pregunta y perspectiva

Evita una bibliografía plana. Para cada fuente registra:

```text
source
  perspective: discipline | process | product
  questions_answered: [...]
  authority: primary | official | academic | practitioner | community
  scope/version: ...
  freshness: ...
  contradictions: [...]
```

## Selección activa

Conserva una fuente si al menos una condición es cierta:

- responde una pregunta MOSAT relevante;
- refuta o matiza una afirmación importante;
- describe un mecanismo que el modelo no representa;
- aporta evidencia de comportamiento real;
- cambia una decisión o un riesgo.

Descarta o aparca fuentes redundantes que sólo repiten lo ya establecido.

## Señales de búsqueda dirigida

- término ambiguo → buscar definición/estándar;
- componente sin autoridad clara → arquitectura/código/tests;
- capability sin mecanismo → implementación o diseño;
- estado sin evento → protocolo, lifecycle o state machine;
- afirmación histórica → fuente fechada;
- trade-off → evidencia comparativa y condiciones, no rankings genéricos.
