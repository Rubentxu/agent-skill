# Modelos sistémicos

## Principio

Los modelos sintetizan conocimiento adquirido y deben revelar inconsistencias. No dibujes por obligación: selecciona el modelo que reduzca incertidumbre relevante.

## Modelo conceptual

Responde **qué existe y cómo se relaciona**.

Incluye conceptos, categorías, relaciones, cardinalidades o reglas semánticas cuando sean importantes. UML de clases puede servir, pero una taxonomía o grafo es válido si expresa mejor el dominio.

Criterio: cada concepto crítico tiene definición consistente y las relaciones importantes no viven sólo en prosa.

## Modelo estructural

Responde **de qué está hecho y dónde están las fronteras**.

Representa componentes, responsabilidades, dependencias, tecnologías base, autoridades de estado/datos y arquitectura relevante.

Criterio: debe ser posible preguntar “¿quién es responsable de X?” y encontrar una respuesta no ambigua o un gap explícito.

## Modelo funcional

Responde **qué hace y cómo fluye el trabajo**.

Representa capacidades, funciones, servicios, casos de uso y actividades principales. Puede usar descomposición funcional, casos de uso, activity/BPMN o secuencias simples.

Criterio: cada capacidad decisiva enlaza a componentes/mecanismos que la realizan.

## Modelo dinámico

Responde **cómo cambia con el tiempo**.

Representa estados, eventos, transiciones, fallos, recuperación, concurrencia o lifecycle cuando afecten a la comprensión.

Criterio: ninguna transición crítica aparece “por magia”: identifica evento/causa y, cuando aplique, autoridad/observador.

## Modelo contextual

Esta skill añade un quinto agrupador práctico para hacer explícito el entorno: actores, sistemas vecinos, protocolos, fronteras de confianza, inputs/outputs y dependencias externas. Es una normalización útil, no una categoría formal añadida al MOSAT original.

## Coherencia entre modelos

- concepto importante → debe aparecer coherentemente en estructura/función cuando corresponda;
- componente → debe tener responsabilidad;
- capacidad → debe tener mecanismo;
- workflow → debe usar conceptos/componentes existentes;
- estado → debe pertenecer a una entidad/sistema y cambiar por eventos identificables.
